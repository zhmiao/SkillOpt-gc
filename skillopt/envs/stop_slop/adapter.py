"""Stop-Slop environment adapter for SkillOpt."""

from __future__ import annotations

import os

from skillopt.datasets.base import BatchSpec
from skillopt.envs.base import EnvAdapter
from skillopt.envs.stop_slop.dataloader import StopSlopDataLoader
from skillopt.envs.stop_slop.grader import JudgeCache
from skillopt.envs.stop_slop.reflect import run_reflect
from skillopt.envs.stop_slop.rollout import run_batch

_DEFAULT_CATALOG_REL = os.path.join("data", "stop_slop_split", "banned_patterns.json")


class StopSlopAdapter(EnvAdapter):
    """Stop-Slop environment adapter.

    Each task item is a (prose_in, banned_patterns, optional gold_rewrite,
    is_negative) dict. The rollout asks the target to rewrite prose_in and
    grades the result against the canonical pattern catalog.
    """

    def __init__(
        self,
        split_dir: str = "",
        data_path: str = "",
        split_mode: str = "split_dir",
        split_ratio: str = "60:20:20",
        split_seed: int = 42,
        split_output_dir: str = "",
        exec_timeout: int = 120,
        max_completion_tokens: int = 4096,
        workers: int = 8,
        analyst_workers: int = 16,
        failure_only: bool = False,
        minibatch_size: int = 8,
        edit_budget: int = 4,
        seed: int = 42,
        limit: int = 0,
        catalog_path: str = "",
    ) -> None:
        self.exec_timeout = exec_timeout
        self.max_completion_tokens = int(max_completion_tokens)
        self.workers = workers
        self.analyst_workers = analyst_workers
        self.failure_only = failure_only
        self.minibatch_size = minibatch_size
        self.edit_budget = edit_budget
        self.catalog_path = catalog_path
        self.judge_cache = JudgeCache()
        self.dataloader = StopSlopDataLoader(
            split_dir=split_dir,
            data_path=data_path,
            split_mode=split_mode,
            split_ratio=split_ratio,
            split_seed=split_seed,
            split_output_dir=split_output_dir,
            seed=seed,
            limit=limit,
        )

    def setup(self, cfg: dict) -> None:
        super().setup(cfg)
        self.dataloader.setup(cfg)
        # Resolve catalog path: explicit > derived from split_dir > project default.
        if not self.catalog_path:
            split_dir = self.dataloader.split_dir
            candidate = os.path.join(split_dir, "banned_patterns.json") if split_dir else ""
            if candidate and os.path.exists(candidate):
                self.catalog_path = candidate
            else:
                self.catalog_path = os.path.abspath(_DEFAULT_CATALOG_REL)
        if not os.path.exists(self.catalog_path):
            raise FileNotFoundError(
                f"Stop-Slop catalog not found: {self.catalog_path!r}. "
                "Run scripts/merge_stop_slop_dataset.py to build the dataset, "
                "or set env.catalog_path in the config."
            )
        print(f"  [stop_slop] catalog: {self.catalog_path}")

    def get_dataloader(self):
        return self.dataloader

    def build_env_from_batch(self, batch: BatchSpec, **kwargs):
        return list(batch.payload or [])

    def build_train_env(self, batch_size: int, seed: int, **kwargs):
        batch = self.dataloader.build_train_batch(batch_size=batch_size, seed=seed, **kwargs)
        return list(batch.payload or [])

    def build_eval_env(self, env_num: int, split: str, seed: int, **kwargs):
        batch = self.dataloader.build_eval_batch(env_num=env_num, split=split, seed=seed, **kwargs)
        return list(batch.payload or [])

    def rollout(
        self,
        env_manager,
        skill_content: str,
        out_dir: str,
        **kwargs,
    ) -> list[dict]:
        items: list[dict] = env_manager
        # Pull the active target deployment from the model package's runtime state.
        from skillopt.model import azure_openai as _llm
        from skillopt.model.backend_config import (
            TARGET_DEPLOYMENT_NAME_FALLBACK,  # noqa: F401  (lazy import keeps unit tests light)
        )

        target_model = getattr(_llm, "TARGET_DEPLOYMENT", "") or ""
        return run_batch(
            items=items,
            out_root=out_dir,
            skill_content=skill_content,
            catalog_path=self.catalog_path,
            target_model=target_model,
            exec_timeout=self.exec_timeout,
            max_completion_tokens=self.max_completion_tokens,
            workers=self.workers,
            judge_cache=self.judge_cache,
        )

    def reflect(
        self,
        results: list[dict],
        skill_content: str,
        out_dir: str,
        **kwargs,
    ) -> list[dict | None]:
        prediction_dir = kwargs.get("prediction_dir", os.path.join(out_dir, "predictions"))
        patches_dir = kwargs.get("patches_dir", os.path.join(out_dir, "patches"))
        random_seed = kwargs.get("random_seed")
        step_buffer_context = kwargs.get("step_buffer_context", "")
        meta_skill_context = kwargs.get("meta_skill_context", "")

        return run_reflect(
            results=results,
            skill_content=skill_content,
            prediction_dir=prediction_dir,
            patches_dir=patches_dir,
            workers=self.analyst_workers,
            failure_only=self.failure_only,
            minibatch_size=self.minibatch_size,
            edit_budget=self.edit_budget,
            random_seed=random_seed,
            error_system=self.get_error_minibatch_prompt(),
            success_system=self.get_success_minibatch_prompt(),
            step_buffer_context=step_buffer_context,
            meta_skill_context=meta_skill_context,
            update_mode=getattr(self, "_cfg", {}).get("skill_update_mode", "patch"),
        )

    def get_task_types(self) -> list[str]:
        return ["rewrite"]
