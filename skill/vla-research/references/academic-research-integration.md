# Academic Research Integration

Combine `vla-research` with `academic-research-suite` (ARS) without copying ARS
content. ARS supplies general research methods; this skill supplies the VLA
corpus, hardware interpretation, and persistent memory.

## Routing

| User intent | ARS route | VLA responsibility |
|---|---|---|
| Vague thesis direction | Socratic/scoping | Supply thesis, gaps, constraints, and precedents |
| Literature review | Deep research | Search local memory first and add VLA terms |
| Systematic review | Systematic-review mode | Supply corpus and map results to taxonomy |
| Claim verification | Fact-check mode | Preserve IDs and verification scope |
| Multi-paper synthesis | Synthesis and adversarial review | Translate themes into hardware opportunities |
| Paper writing or review | Paper/reviewer workflow | Supply checked claims and records |
| Experiment planning | Experiment workflow | Supply models, platforms, baselines, and metrics |

Do not invoke ARS for routine search, one-paper reading, metric extraction, or
reading-queue maintenance.

## VLA Context Packet

```yaml
research_goal: <goal>
candidate_rq: <question or null>
current_thesis: <working thesis>
scope:
  task_domain: <manipulation or other>
  deployment: <edge/on-robot/cloud>
  batch_size: <value>
  control_setting: <closed-loop/open-loop>
local_sources:
  - id: <local ID>
    title: <title>
    read_status: <queued/skimmed/read>
    verification_status: <status>
    relevance: <reason>
priority_metrics:
  - latency
  - p95_latency
  - p99_latency
  - jitter
  - control_hz
  - energy_per_action
  - power
  - cost
  - memory_footprint
  - platform
  - batch_size
  - success_rate
active_gaps: []
taxonomy_focus: []
known_constraints: []
```

Local records are a starting corpus, not automatically trusted evidence.

## Architecture Evidence Criteria

Assess:

1. Publication status and source integrity.
2. Reproducibility of code, model, workload, hardware, and configuration.
3. Measurement quality, including tails, run count, synchronization, and
   end-to-end boundary.
4. Comparison quality across baselines, precision, task, and platform.
5. Deployment relevance to batch size, robot loop, communication, and edge
   constraints.
6. Task preservation through success rate or another quality measure.

Use `strong`, `moderate`, `limited`, or `unverified` with a reason.

## Verification Dimensions

```yaml
existence_status: verified | plausible | unverified | failed
source_acquired: true | false
metadata_checked: true | false
claims_checked: true | false
metrics_checked: true | false
verification_method: <method>
verification_notes: <scope and limitations>
```

Publication-existence checks do not by themselves verify performance claims.

## Consuming ARS Outputs

- RQ Brief: update research direction only after user approval.
- Bibliography: deduplicate against the index and add new records unverified.
- Verification report: update metadata and scoped notes.
- Synthesis: propose taxonomy or gap changes with supporting paper IDs.
- Adversarial review: preserve unresolved counter-evidence and assumptions.
- Experiment plan: map hypotheses to platforms, baselines, metrics, and
  task-success safeguards.

Persist evidence, inference, and hypothesis separately. Do not write generated
narrative into numeric metric fields.

## Graceful Degradation

If ARS is unavailable, continue locally, use this context packet as a checklist,
verify primary sources where possible, and name the omitted research stages.
