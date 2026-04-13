# GitHub Leverage Plan

Last updated: 2026-04-12 20:51 EDT
Status: ACTIVE

## Verified repo topology
- `prettybusysolutions-eng/aurex-instance` = root OpenClaw instance / reconstruction archive
- `prettybusysolutions-eng/platform-spine` = private durable execution substrate repo
- `prettybusysolutions-eng/revenue-copilot` = private revenue machine repo

## Leverage doctrine
### 1. Root repo role
Use `aurex-instance` as:
- canonical control plane
- convergence registry
- governing memory and truth archive
- substrate reconstruction ledger

Do not use it as the forever-home for every runtime/generated artifact.

### 2. Subproject repo role
Use subordinate repos as capability homes:
- `platform-spine` for durable execution substrate
- `revenue-copilot` for revenue machine implementation
- other product repos for product-specific implementation truth

### 3. GitHub leverage strategy
- root repo publishes control truth and convergence state
- subrepos carry implementation depth
- promotion happens by proof, not by merely existing in the root archive

## Immediate next GitHub actions
1. keep committing convergence/control artifacts into `aurex-instance`
2. reduce root drift before broad push pressure grows
3. bind platform-spine and revenue-copilot explicitly into the system-of-systems registry as promoted subordinate repos
4. eventually push convergence artifacts upstream when the working tree is strategically clean enough
