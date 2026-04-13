# System 4 Verification — Graceful Degradation Policy

## Gate
- [ ] Simulated memory pressure shifts system to Reduced tier
- [ ] Reduced tier outputs declare reduced confidence
- [ ] Severe exhaustion shifts system to Minimal tier
- [ ] Minimal tier preserves state and defers work without loss
- [ ] No critical path crashes under resource pressure

## Evidence
- resource monitor report
- degraded output artifacts
- preserved checkpoint proof
- deferred work proof
