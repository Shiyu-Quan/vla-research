# VLA Research Memory Contract

## Location

Resolve memory in this order:

1. Explicit script argument.
2. `VLA_RESEARCH_MEMORY`.
3. `%USERPROFILE%\Documents\vla-research-memory`.

## Canonical Files

- `papers/index.json`: structured paper records.
- `pdfs/`: locally obtained paper PDFs.
- `gaps/gap-table.json`: research gaps and opportunity map.
- `state/reading-queue.json`: prioritized reading queue.
- `state/research-state.md`: current research question and thesis.
- `taxonomy/*.md`: technique taxonomy and hardware mapping.
- `matrices/metrics-schema.md`: metric definitions.

## Paper Record Rules

Required fields:

- `id`
- `title`
- `year`
- `status`
- `url`
- `domain`
- `main_technique`
- `hardware_relevance`
- `metrics`
- `tags`
- `read_status`
- `verification_status`

Recommended PDF fields:

- `pdf_path`
- `pdf_source_url`
- `pdf_status`: `saved`, `missing`, or `needs_update`
- `pdf_pages`

Use `not_reported`, `limited`, or `needs_extraction` for unknown metrics.

## Update Policy

Prefer `add_or_update_paper`. It updates the JSON index and renders a Markdown
card under `papers/`.

When editing manually:

1. Preserve valid UTF-8 JSON.
2. Keep tags lowercase and hyphenated.
3. Keep grounded claims in `key_claims`.
4. Put critique and missing information in `limitations`.
5. Keep verification scope explicit in notes.

## CLI

```powershell
python -m vla_research.cli search "FPGA action generation"
python -m vla_research.cli get T01
python -m vla_research.cli gaps --priority high
python -m vla_research.cli recommend --focus "energy action generation"
```
