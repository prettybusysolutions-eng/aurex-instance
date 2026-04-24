# Canonical Root Manifest

Generated: 2026-04-23
Status: ACTIVE BASELINE

## Purpose
This file defines the permanent root authority boundary for the workspace.
If a surface does not belong to one of the approved root classes below, it should not remain at root authority without explicit promotion.

## Root authority classes

### 1. Governing spine files
Allowed at root:
- identity and operator-alignment files
- governing law and doctrine files
- canonical truth and activation files
- root policy and manifest files
- selected promoted charter/recovery/proof law files

Examples:
- `README.md`
- `ROOT-REPO-POLICY.md`
- `STATE.md`
- `NEXT-ACTION.md`
- `ACTIVATION-REGISTRY.md`
- `ASSET-REGISTRY.md`
- `XZENIA-DECLARATION.md`
- `XZENIA-OPERATIONAL-LAW.md`
- `XZENIA-GOVERNING-SPINE.md`
- `XZENIA-CONTROL-SPINE.md`
- `SYSTEM-OF-SYSTEMS-REGISTRY.md`
- `SUBSYSTEM-CLASSIFICATION-LEDGER.md`
- `TRUTH-DISCIPLINE-AUTOMATION-PLAN.md`
- `TRUTH-DISCIPLINE-ENFORCEMENT.md`
- `RECONSTITUTION-RUNTIME-TRUTH.md`
- `PROOF-BASED-RECOVERY-PLAN.md`
- `REVENUE-MACHINE-EXECUTION-CHARTER.md`
- `PROOF-TO-PRODUCT-PROMOTION-LAW.md`
- `ROOT-PURITY-POLICY.md`
- `CANONICAL-ROOT-MANIFEST.md`

### 2. Bootstrap and continuity reference files
Allowed at root:
- operator/bootstrap references that define identity, startup, memory, and execution contract

Examples:
- `AGENTS.md`
- `SOUL.md`
- `USER.md`
- `TOOLS.md`
- `MEMORY.md`
- `HEARTBEAT.md`
- `IDENTITY.md`
- `BOOT.md`
- `BOOTSTRAP.md`
- `BRIDGE.md`
- `EXECUTION_LOOP.md`

### 3. Canonical structured directories
Allowed at root:
- `memory/` as continuity and operator-memory surface
- `reports/` as promoted proof/audit/closure artifact surface
- `scripts/` as root execution utility surface, subject to internal classification
- `docs/` as documentation surface
- `governance/` as governance-specific supporting surface
- `infra/` as infrastructure runbook/control surface

### 4. Subproject-owned directories
Allowed to exist at root, but not as root authority:
- `projects/`
- `skills/`
- `revenue-copilot/`
- `control-plane/`
- `platform-spine/`
- `sovereign-diagnostic-engine/`
- `sovereign-kit/`
- `private/`
- `system/`
- `packaging/`
- `registry/`
- `registries/`
- `target-sandbox/`

Rule:
These surfaces may live at root physically, but their contents do not automatically become root authority.
Authority remains local to their subtree unless explicitly promoted.

### 5. Local/runtime-only directories
May exist locally, but are not canonical control:
- logs
- runtime state
- task queues
- temp/output/cache dirs
- backups
- generated media/assets
- environment/private support dirs

Rule:
These must never be mistaken for governing root surfaces.

## Root violation rule
A root-level file or directory is a violation when:
- it is not part of the approved classes above
- or it is historical/planning/commercial narrative mass that has not been explicitly promoted
- or it is runtime/generated residue competing with canonical control

## Promotion rule
A new root surface is allowed only if:
1. it changes the governing spine, truth posture, or canonical proof layer
2. it is referenced by current execution law or recovery law
3. it has lasting operator-level authority
4. it cannot live more cleanly in a subtree or archive namespace

Current explicitly promoted additions from tranche-3 and post-closeout boundary review:
- `TRUTH-DISCIPLINE-AUTOMATION-PLAN.md`
- `TRUTH-DISCIPLINE-ENFORCEMENT.md`
- `SYSTEM-OF-SYSTEMS-REGISTRY.md`
- `SUBSYSTEM-CLASSIFICATION-LEDGER.md`
- `XZENIA-CONTROL-SPINE.md`
- `ROOT-PURITY-POLICY.md`

## Demotion rule
A root surface should be demoted, archived, or relocated if:
- it is a one-off planning memo
- it is historical staging or promotion residue
- it is offer/copy/strategy exploration without current governing authority
- it is runtime/generated output
- it is better owned by a subtree

## Current doctrine
The root is not a universal dump.
The root is the control surface of the machine.
Everything else must either justify its authority or leave root authority.
