# VLA Metrics Schema

Extract metrics only when the source reports them and preserve the measurement
context.

## Performance

- End-to-end latency
- p95 and p99 latency
- Jitter
- Control frequency in Hz
- Batch size

## Efficiency

- Energy per action
- Average and peak power
- Memory footprint
- Cost and cost assumptions

## Deployment

- Hardware platform
- Precision
- Runtime and framework
- Communication overhead
- Closed-loop or open-loop setting

## Task Quality

- Success rate
- Dataset or task suite
- Baselines
- Accuracy or trajectory-quality safeguards

Use `not_reported`, `limited`, or `needs_extraction` instead of inventing a
value.
