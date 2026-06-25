---
name: vla-research
description: Use when Codex works on VLA papers, literature review, research scoping, evidence synthesis, hardware metrics, taxonomy, research gaps, or Vision-Language-Action acceleration for robot manipulation, edge deployment, accelerator/NPU/FPGA/ASIC design, action generation, diffusion/flow action heads, and closed-loop control.
---

# VLA Research

Use this skill as a domain adapter for VLA research-to-paper workflows. Keep
VLA knowledge, metrics, and persistent research memory here. Use
`academic-research-suite` as an optional research-method engine for tasks that
need broader academic rigor.

## Source Of Truth

Resolve the research memory from `VLA_RESEARCH_MEMORY`. If it is unset, use:

`%USERPROFILE%\Documents\vla-research-memory`

Read `references/memory-contract.md` for fields and update rules. Read
`references/academic-research-integration.md` when routing through
`academic-research-suite` or consuming its output.

## Preferred Access Order

1. Use the `vla_research` MCP tools when available:
   - `search_papers`
   - `get_paper`
   - `add_or_update_paper`
   - `list_gaps`
   - `recommend_next_reading`
2. If MCP tools are unavailable, use the CLI:
   - `python -m vla_research.cli search "action generation"`
   - `python -m vla_research.cli get T01`
   - `python -m vla_research.cli gaps --priority high`
   - `python -m vla_research.cli recommend --focus "FPGA action generation"`
3. If neither is available, read and edit the memory's JSON and Markdown files
   directly while preserving schema.

## Automatic Research Routing

Classify the task before acting. Do not run a full academic workflow for a
routine paper lookup or reading request.

### Use VLA Research Alone

Handle these tasks directly:

- Search, retrieve, add, or update local paper records.
- 精读, 粗读, explain, or extract metrics from a single paper.
- Compare a small number of papers without systematic evidence synthesis.
- Inspect the reading queue, taxonomy, hardware mapping, or gap table.
- Recommend the next paper from local memory.

### Combine With Academic Research Suite

**OPTIONAL COMPANION SKILL:** Use `academic-research-suite` automatically when
the user asks for:

- A vague research direction, thesis topic, or research-question refinement.
- Deep research, literature review, systematic review, reproducible source
  discovery, or broad fact-checking.
- Evidence-weighted multi-paper synthesis, contradiction analysis, or robust
  gap validation.
- Paper outlining, drafting, citation audit, manuscript review, or revision.
- Experiment planning, statistical interpretation, or reproducibility review.

Use local memory as the starting domain corpus. Give the companion workflow the
current thesis, relevant papers, metrics, gaps, taxonomy, and batch-1
closed-loop constraints. Translate its general academic output back into
VLA-specific conclusions.

Do not claim ARS was used unless its skill instructions were available and
followed. Do not copy ARS prompts or templates into this skill.

### If Academic Research Suite Is Unavailable

Continue with the VLA workflow instead of blocking. State briefly that advanced
systematic-search, source-grading, or adversarial-review stages were not run.
Still use primary sources, separate evidence from inference, and mark
unverified claims honestly.

## Research Workflow

When adding or reviewing a paper:

1. Classify it as VLA foundation, action generation, algorithmic acceleration,
   profiling, systems/runtime, or dedicated hardware.
2. Extract the metric tuple when available:
   `latency`, `p95_latency`, `p99_latency`, `jitter`, `control_hz`,
   `energy_per_action`, `power`, `cost`, `memory_footprint`, `platform`,
   `batch_size`, `success_rate`.
3. Mark unknown values as `not_reported`, `limited`, or `needs_extraction`.
4. Separate explicit evidence, architectural inference, and research
   hypothesis.
5. Update the gap table only when evidence changes the gap picture.
6. Update taxonomy only for a reusable technique family or hardware mapping.

When using the academic companion:

1. Query local memory first and construct the VLA context packet in
   `references/academic-research-integration.md`.
2. Select only the ARS mode needed for the task.
3. Preserve source IDs and evidence status.
4. Apply architecture-specific evidence criteria.
5. Persist only supported findings.

## Paper Reading Modes

Use primary sources whenever possible: paper PDF, proceedings or arXiv page,
DOI page, official project page, or author artifact.

### Intensive Reading

Use for 精读, deep read, intensive read, or section-by-section explanation.
Follow the paper's own section order. For each section:

1. State its purpose.
2. Explain methods, definitions, algorithms, equations, and experiments.
3. Identify the evidence and supported claims.
4. Explain VLA implications for action generation, control frequency, latency,
   hardware/runtime mapping, deployment, or evaluation.
5. Mark unclear or weakly supported points as open questions.

Finish with contribution, strongest evidence, limitations, and implications for
VLA hardware/software co-design.

### Skim Reading

Use for 粗读, rough read, quick read, skim, key points, or high-level summary.
For Chinese requests, use these headings:

1. 该领域当前的问题
2. naive方案是什么
3. naive方案有什么样的挑战
4. 该文章是如何解决这些挑战的
5. 文章解决了什么样的问题，达到了怎样的效果

Separate explicit evidence from inference. Include reported task suite,
baselines, success rate, latency, control Hz, energy, memory, and platform.
Write `not_reported` when a metric is absent.

## Research Prior

Treat action generation and closed-loop control as a promising starting
hypothesis, not a guaranteed conclusion. Investigate action experts,
diffusion/flow action heads, action chunking, parallel/speculative action
decoding, temporal redundancy, and multi-rate scheduling under batch-1 edge
constraints. Revise this prior when stronger evidence points elsewhere.

## Verification Discipline

For paper-draft claims, verify against primary sources. Keep seed entries
unverified until checked.

Treat these as separate questions:

- Does the publication exist and is its metadata correct?
- Was the original paper acquired and read?
- Does the cited passage support the claim?
- Were hardware metrics checked with platform, batch size, measurement scope,
  and baseline?

Do not collapse one positive answer into full verification.
