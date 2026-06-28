# Stream 2 auto-diff mining notes

Initialized after reading `dev_docs/design/dataset_construction_plan.md` top to bottom.

## Inputs verified

- HumanEmbedding essay versions on disk: `essay_v2.md`, `essay_v3.md`, `essay_v4.md`, `essay_v5.md`, `essay_v6.md`, `essay_v7.md`, `essay_v8.md`, `essay_v9.md`, `essay_v10.md`, `essay_v11.md`, `essay_v12.md`, `essay_v13.md`, `essay_v14.md`, `essay_v15.md`, `essay_v16.md`, `essay_v17.md`, `essay_v18.md`, `essay_v19.md`, `essay_v20.md`, `essay_v22.md`.
- Missing version noted: `essay_v21.md`; skipped `v20→v21` and `v21→v22`.
- Pattern catalogs read: `HumanEmbedding/docs/research/ai_writing_tells.md` and `~/.copilot/skills/stop-slop/references/phrases.md`.

## Extraction method

- Plain `git diff essay_vN.md essay_vM.md` returns no useful output for two tracked paths in the same worktree, so extraction used `git --no-pager diff --no-index --unified=0 --no-color essay_vN.md essay_vM.md` for hunk accounting plus paragraph-block matching from file contents.
- Paragraph blocks shorter than 80 characters, headings, code fences, tables, footnotes, and unchanged moved paragraphs were skipped.
- Replace hunks were paired by greedy semantic score inside each paragraph-level replace group; low-score unpaired old paragraphs became pure-deletion candidates and were kept only when a strong catalogued tell was present.
- Judge policy was conservative: keep only if at least one named catalog pattern decreased and the rewrite did not introduce high-salience tells.

## Current result

- Raw paragraph candidates: 659
- Judge-kept medium-quality items: 147
- Dropped candidates: 512
- Items JSON appended incrementally at `/home/miao/repos/SkillOpt-gc/dev_docs/design/dataset_construction/stream2_items.json`.
