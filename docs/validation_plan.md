# Validation Plan

## Current validation

The repository validates:

- deterministic demo instance generation
- exact schedule search
- feasibility diagnostics
- result serialization
- script execution
- unit tests for selected structural outputs

## Next validation gates

1. Add randomized constellation instances with fixed seeds.
2. Add parameter sweeps over link capacity, downlink capacity, terminal limit, and energy state.
3. Compare exact enumeration against local heuristic methods for larger instances.
4. Add route-diversity diagnostics for top candidate schedules.
5. Add latency and feasibility plots for capacity sweeps.
6. Add rolling-horizon extensions across multiple scheduling slices.

## Acceptance logic

A useful scheduling instance should produce a feasible solution, expose capacity and energy diagnostics, and preserve enough structure to compare exact, heuristic, and quantum-inspired methods on the same input.
