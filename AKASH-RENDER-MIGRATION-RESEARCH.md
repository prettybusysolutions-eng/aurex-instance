# Akash and Render Migration Research

Last updated: 2026-04-14 00:05 EDT
Status: READY

## Trigger condition
Resource-aware migration logic may recommend migration when:
- local thermals exceed 85C for sustained periods
- CPU saturation materially harms throughput
- the worker class is portable and stateless enough to redeploy safely

## Safe automation posture
- observe thermals and load locally
- emit migration recommendation artifacts
- prepare deployment manifests and env contracts
- do not perform paid deployment without explicit approval

## Akash fit
Best for containerized workloads with operator-managed deployment definitions.

## Render fit
Best for simpler managed deployment of web/API workers with straightforward env injection.

## Next implementation surfaces
- local thermal sampler
- workload classification
- deploy-target manifest templates
- migration recommendation report
