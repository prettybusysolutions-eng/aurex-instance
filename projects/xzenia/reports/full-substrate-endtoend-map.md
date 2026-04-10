# XZENIA ENTIRE SUBSTRATE — END-TO-END MAP
**Generated:** 2026-03-23 11:30 EDT  
**Version:** 1.0  
**Scope:** All systems, components, and dependencies

---

## EXECUTIVE MAP

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         XZENIA SUBSTRATE                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│  │   CHARTER   │───▶│   FRONTIER  │───▶│   EXECUTION │                 │
│  │   LAYER     │    │   LAYER     │    │   LAYER     │                 │
│  └─────────────┘    └─────────────┘    └─────────────┘                 │
│        │                  │                  │                         │
│        ▼                  ▼                  ▼                         │
│  ┌─────────────────────────────────────────────────────────────┐      │
│  │                    CSMR LEDGER                              │      │
│  │              (767 events, 39 proposals)                     │      │
│  └─────────────────────────────────────────────────────────────┘      │
│        │                  │                  │                         │
│        ▼                  ▼                  ▼                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│  │  SUPERVISOR │    │   RECOVERY  │    │   AGENTS    │                 │
│  │  Health 0.7 │    │   12 Tasks  │    │   Unified   │                 │
│  └─────────────┘    └─────────────┘    └─────────────┘                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## LAYER 1: CHARTER & STRATEGY

### 1.1 Charter Files
| File | Purpose |
|---|---|
| `charter/build-charter.json` | 5 systems (7.5→9.0) |
| `charter/unheard-of-threshold-charter.json` | 4 frontiers toward threshold |
| `charter/domain_contract_schema.json` | Domain onboarding contract |
| `charter/defect_schema.json` | Defect classification |

**Systems Defined:**
- system-1-closed-defect-loop ✅
- system-2-canonical-scheduler-executor-contract ✅
- system-3-unified-supervisor ✅
- system-4-graceful-degradation-policy ✅
- system-5-domain-onboarding-contract ⚠️ blocked

---

## LAYER 2: STATE & PERSISTENCE

### 2.1 Core State Files
| File | Purpose |
|---|---|
| `state/latest-checkpoint.json` | Last checkpoint + phase |
| `state/resume-queue.json` | Pending work queue |
| `state/ecosystem-index.json` | Node activation status |
| `state/bottleneck-registry.json` | Active bottlenecks |

### 2.2 Execution State
| File | Purpose |
|---|---|
| `execution/autofallback-state.json` | Fallback chain position |
| `execution/token_budget_guard.py` | Budget monitoring |
| `execution/degradation_evaluator.py` | Tier evaluation |

### 2.3 Agent State
| File | Purpose |
|---|---|
| `state/unified-agent-state.json` | Unified controller state |
| `state/edge-executor-state.json` | Edge execution stats |
| `state/cloud-reasoner-state.json` | Cloud reasoning stats |
| `state/screen-buffer.json` | 5-second screen window |

---

## LAYER 3: ORCHESTRATION

### 3.1 Model Orchestration
| File | Purpose |
|---|---|
| `orchestration/openclaw-model-registry.json` | 15 models, 8 providers |
| `orchestration/resilience-policy.json` | Fallback chain config |
| `orchestration/bottleneck-registry.json` | Active bottlenecks |

### 3.2 Execution Orchestration
| File | Purpose |
|---|---|
| `execution/checkpoint_contract.py` | Checkpoint wrapper |
| `execution/auto_fallback_enforcer.py` | API error fallback |
| `execution/api_error_watchdog.py` | Rate limit detection |
| `execution/model_switch.py` | Manual model switching |

---

## LAYER 4: SUPERVISOR & HEALTH

### 4.1 Unified Supervisor
| File | Purpose |
|---|---|
| `supervisor/unified_supervisor.py` | Health monitoring |
| `csmr/reports/unified-supervisor-health*.json` | Health reports |

**Functions:**
- Contradiction detection
- Health scoring (0.7 current)
- Remediation triggers

### 4.2 Degradation Policy
| File | Purpose |
|---|---|
| `runtime/degradation-policy.json` | Tier thresholds |
| `runtime/degradation_gate.py` | Tier evaluation |
| `runtime/normal_tier_assessor.py` | Normal tier check |

**Current Tier:** normal (19GB disk)

---

## LAYER 5: CSMR — CAUSAL SELF-MODIFICATION RUNTIME

### 5.1 Core CSMR Components
| Component | File | Purpose |
|---|---|---|
| Ledger | `csmr/ledger/causal_ledger.sqlite` | 767 events |
| Proposals | `csmr/modification_proposals/` | 39 proposals |
| Frontier-3 | `csmr/frontier_3_executor.py` | Mutation executor |
| Frontier-4 | `csmr/frontier_4_moat.py` | Moat builder |

### 5.2 CSMR Pipeline
```
Event → Attribution → Proposal → Gate A → Gate B → Gate C → Apply → Verify → Retain
```

| Status | Count |
|---|---|
| validated_gate_a | 20 |
| promoted | 8 |
| applied | 2 |
| applied_target | 3 |
| applied_skill | 1 |
| rejected_gate_c | 2 |
| rejected_gate_b | 1 |
| rejected_gate_a | 1 |

---

## LAYER 6: UNIFIED AGENT ARCHITECTURE

### 6.1 Tesla Digital Optimus Inspired
| Component | File | Type |
|---|---|---|
| Controller | `agents/unified_agent_controller.py` | Orchestrator |
| Edge (System 1) | `agents/edge_executor.py` | Fast local |
| Digital Agent | `agents/digital_agent.py` | Hybrid |
| Cloud Reasoner | `agents/cloud_reasoner.py` | System 2 |
| Screen Capture | `agents/screen_capture.py` | Real-time input |

### 6.2 Execution Modes
| Mode | Latency | Cost | When |
|---|---|---|---|
| edge | <50ms | $0.001 | Routine actions |
| cloud | <2s | $0.05 | Complex reasoning |
| hybrid | <500ms | $0.02 | Edge + validation |

---

## LAYER 7: RECOVERY & CONTINUITY

### 7.1 Recovery Stack
| Component | File | Purpose |
|---|---|---|
| Tier 1 | `recovery/tier1_*.py` | Boot + integrity + health |
| Tier 2 | `recovery/tier2_*.py` | Correlation + attribution |
| Reconciliation | `recovery/reconcile_state.py` | State sync |
| Resume | `recovery/resume_last_intent.py` | Intent recovery |

### 7.2 LaunchAgents (12 Active)
- `com.xzenia.api-error-watchdog` — rate limit detection
- `com.xzenia.model-guardian` — budget switching
- `com.xzenia.autonomy.refresh` — recurring autonomy
- `com.xzenia.critical.refresh` — critical node health
- `com.xzenia.priority.refresh` — bottleneck prioritization
- `com.xzenia.adaptive.resume` — cross-layer adaptation
- `com.xzenia.unified.cycle` — Tier 7 orchestration
- `com.xzenia.trend.proposal.cycle` — trend-fed cadence
- `com.xzenia.tier1.recovery` — continuity guard
- `com.xzenia.resurrection` — legacy recovery
- `com.xzenia.browser.agent` — browser relay
- `com.xzenia.county-homelessness-monitor` — external task

---

## LAYER 8: DOMAINS

### 8.1 Onboarded Domains
| Domain | File | Status |
|---|---|---|
| Pretty Busy Cleaning | `domains/pretty-busy-cleaning.domain.json` | Active |
| Revenue Recovery | `domains/revenue-recovery.domain.json` | Active |

### 8.2 Domain Artifacts
- `domains/pretty-busy-cleaning/` — Lead engine scaffold
- `domains/validate_domain_contract.py` — Validator

---

## LAYER 9: SKILLS & SYSTEM

### 9.1 Skills
| Skill | Location | Purpose |
|---|---|---|
| next-step-autonomy | `workspace/skills/next-step-autonomy/` | Auto-continue |
| meta-healing | `workspace/skills/meta-healing/` | Self-repair |
| skill-harvester | `workspace/skills/skill-harvester/` | Lesson capture |
| substrate-optimizer | `workspace/skills/substrate-optimizer/` | Optimization |
| creation-engine | `workspace/skills/creation-engine/` | Asset creation |
| moat-artifact | `workspace/skills/moat-artifact-20260323152440/` | Repeated lessons |

### 9.2 System Files
| File | Purpose |
|---|---|
| `system/SUBSTRATE-LAW.md` | Operating rules |
| `system/UNHEARD-OF-DOCTRINE.md` | No novelty theater |
| `system/STRATEGIC-REFUSAL-CHARTER.md` | Strategic boundaries |

---

## DEPENDENCY GRAPH

```
CHARTER (build-charter.json)
    │
    ▼
FRONTIER SELECTION (unheard-of-threshold-charter.json)
    │
    ├──▶ Frontier-1: proof-spine-recursion (active)
    ├──▶ Frontier-2: honest-tier-lift (active)
    ├──▶ Frontier-3: governed-substrate-mutation (executed)
    │       └──▶ frontier_3_executor.py
    │               └──▶ CSMR ledger (sqlite)
    └──▶ Frontier-4: imitation-resistance (executed)
            └──▶ frontier_4_moat.py
                    └──▶ Skills artifacts

EXECUTION PIPELINE
    │
    ├──▶ checkpoint_contract.py
    │       └──▶ latest-checkpoint.json
    │
    ├──▶ auto_fallback_enforcer.py
    │       └──▶ openclaw-model-registry.json
    │       └──▶ autofallback-state.json
    │
    └──▶ unified_agent_controller.py
            ├──▶ edge_executor.py (System 1)
            ├──▶ cloud_reasoner.py (System 2)
            └──▶ screen_capture.py

SUPERVISOR LOOP
    │
    └──▶ unified_supervisor.py
            └──▶ degradation_policy.json
            └──▶ ecosystem-index.json

RECOVERY LOOP
    │
    └──▶ LaunchAgents (12)
            ├──▶ api-error-watchdog
            ├──▶ model-guardian
            ├──▶ autonomy.refresh
            └──▶ ... (9 more)
```

---

## FILE STATISTICS

| Category | Count |
|---|---|
| Python files | 931 |
| JSON configs | 54 |
| SQLite DBs | 1 |
| Skills | 6+ |
| LaunchAgents | 12 |
| CSMR events | 767 |
| Proposals | 39 |
| Applied mutations | 2 |

---

## EXECUTION FLOW

```
USER MESSAGE
    │
    ▼
SESSION BOOT (session-boot.py)
    │
    ├──▶ Load checkpoint → NEXT-ACTION.md
    │
    ▼
UNIFIED SUPERVISOR (health check)
    │
    ├──▶ Contradiction? → Gate evaluation
    │
    ▼
MODEL ROUTING
    │
    ├──▶ Primary: claude-sonnet-4-6
    ├──▶ Fallback chain: 5 models
    └──▶ API error → auto_fallback_enforcer.py
    │
    ▼
EXECUTION
    │
    ├──▶ Token budget check → token_budget_guard.py
    ├──▶ Degradation check → degradation_evaluator.py
    │
    ▼
CHECKPOINT (checkpoint_contract.py)
    │
    ├──▶ Save state → latest-checkpoint.json
    ├──▶ Log to CSMR ledger
    │
    ▼
CONTINUITY (HEARTBEAT.md)
    │
    └──▶ Background tasks (LaunchAgents)
```

---

## KEY ARTIFACTS

| Artifact | Path | Lines |
|---|---|---|
| Build Charter | `projects/xzenia/charter/build-charter.json` | ~200 |
| CSMR Constitution | `projects/xzenia/csmr/CONSTITUTION.md` | ~300 |
| Substrate Law | `workspace/system/SUBSTRATE-LAW.md` | ~150 |
| Unified Agent Architecture | `projects/xzenia/agents/XZENIA-UNIFIED-AGENT-ARCHITECTURE.md` | ~200 |
| Full System Snapshot | `projects/xzenia/reports/full-system-snapshot-20260323.md` | ~250 |

---

## HEALTH INDICATORS

| Indicator | Value | Status |
|---|---|---|
| Health Score | 0.7 | 🟡 |
| Disk Free | 19GB | 🟡 |
| CSMR Events | 767 | 🟢 |
| Proposals Applied | 2 | 🟢 |
| Active LaunchAgents | 12 | 🟢 |
| Model Fallback Chain | 5 models | 🟢 |
| Unified Agent | 5 components | 🟢 |

---

*End-to-end substrate mapped. 931 Python files, 12 LaunchAgents, 767 CSMR events, 2 mutations applied.*
*Xzenia compounds through governed self-improvement.*