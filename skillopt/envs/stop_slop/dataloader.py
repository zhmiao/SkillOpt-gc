"""Stop-Slop dataloader.

Reads ``data/stop_slop_split/{train,val,test}/items.json`` produced by
``scripts/merge_stop_slop_dataset.py``. Each items.json is a list of
items conforming to the schema in
``dev_docs/design/dataset_construction_plan.md``.
"""

from __future__ import annotations

import json
import os

from skillopt.datasets.base import SplitDataLoader


class StopSlopDataLoader(SplitDataLoader):
    """Stop-Slop dataloader (items.json per split directory)."""

    def load_split_items(self, split_path: str) -> list[dict]:
        # The split layout already provides items.json explicitly.
        items_path = os.path.join(split_path, "items.json")
        if not os.path.exists(items_path):
            return super().load_split_items(split_path)
        with open(items_path) as f:
            items = json.load(f)
        if not isinstance(items, list):
            raise ValueError(f"{items_path}: expected JSON array, got {type(items).__name__}")
        return items

    def load_raw_items(self, data_path: str) -> list[dict]:
        with open(data_path) as f:
            return json.load(f)
