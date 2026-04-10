# ASSET REGISTRY — Xzenia Substrate
<!-- Last verified: 2026-04-02 21:45 EDT -->
<!-- Status key: ✅ VERIFIED | ⚠️ DEGRADED | ❌ BROKEN | 🔄 RUNNING -->

This is the canonical permanent record of every built asset. 
Only update after **individual production verification**.

---

## SECTION 1 — CORE SUBSTRATE (Main Workspace)

### 1.1 NEXUS Commerce Engine
**Location:** `~/.openclaw/workspace/marketplace-scaffold/`
**Status:** ✅ VERIFIED (tested 2026-04-02)
**Components:**
- `src/services/db_layer.py` — NexusOrchestrator (PostgreSQL + Redis, circuit breaker, rate limiter, audit)
- `src/services/repositories.py` — DemandRepository with full CRUD + event publishing
- `src/services/loop_controller.py` — run_once() / run_batch() end-to-end loop
- `scripts/run_loop.py` — CLI runner
- `migrations/` — DB schema management
- LaunchAgent: `com.xzenia.nexus.loop` — ✅ LOADED, exit=0, runs 3x daily (8am/2pm/8pm)
**DB:** PostgreSQL 16.13, localhost:5432, database: nexus, 15 tables
**Verified:** imports clean, loop_controller.run_once() functional, DB persisting

### 1.2 Cognitive Engine (Tier 5)
**Location:** `~/.openclaw/workspace/projects/xzenia/cognitive/`
**Status:** ✅ VERIFIED (tested 2026-04-02)
**Entry:** `cognitive_engine.py` — get_cognitive_engine(), MemoryType
**LaunchAgent:** `com.xzenia.tier5.cognitive` — ✅ LOADED, exit=0, runs 4x daily (4am/10am/4pm/10pm)
**Tables:** xzenia_memory, xzenia_goals, xzenia_world_state (PostgreSQL)
**Verified:** imports clean after sqlalchemy install, cycle runs to completion

### 1.3 Evolution Engine
**Location:** `~/.openclaw/workspace/projects/xzenia/evolution/`
**Status:** ✅ VERIFIED (tested 2026-04-02)
**Entry:** `evolution_engine.py` — get_evolution_orchestrator()
**LaunchAgent:** `com.xzenia.evolution` — ✅ LOADED, exit=0
**Verified:** imports clean, no errors in /tmp/nexus-evolution.err

### 1.4 Swarm / Meta-Cognition Loop
**Location:** `~/.openclaw/workspace/projects/xzenia/swarm/`
**Status:** ✅ VERIFIED (tested 2026-04-02)
**Entry:** `meta_cognition_loop.py` — get_meta_loop()
**Agents:** Architect, Builder, Researcher, Auditor, Inventor, Unifier
**LaunchAgent:** `com.xzenia.swarm` — ✅ LOADED, exit=0
**Verified:** imports clean, no errors in /tmp/nexus-swarm.err

### 1.5 CSMR — Causal Self-Modification Runtime
**Location:** `~/.openclaw/workspace/projects/xzenia/csmr/`
**Status:** ✅ BUILT (not independently load-tested this session)
**Components:**
- Immutable causal ledger (SQLite): `ledger/causal_ledger.sqlite`
- Proposal pipeline: `proposals/`
- Gate A/B/C validators
- Controlled promoter with canary staging + rollback
- Applied/shadow config artifacts
- Auto-pipeline for attribution → proposal → gate flow
**Tiers verified in prior sessions:** T1 boot trigger, T2 failure correlator, T3 ecosystem analytics, T4-T14 all scaffolded

### 1.6 Cognitive Tiers 1–14
**Location:** `~/.openclaw/workspace/projects/xzenia/tier*/`
**Status:** ✅ BUILT (individual tier scripts verified in prior sessions)
| Tier | Component | Key Script |
|------|-----------|-----------|
| 1 | Boot trigger, integrity checker, health loop | `tier1/` |
| 2 | Failure correlator, attribution scorer, drift detector, intent graph | `tier2/` |
| 3 | Ecosystem analytics, historical baseline, shadow comparator | `tier3/` |
| 4 | Temporal failure correlation, governed skill mutation + rollback | `tier4/` |
| 5 | Persistent memory, goal engine, causal reasoner, world model | `tier5/` |
| 6 | Cross-layer adaptation | `tier6/` |
| 7 | Unified orchestration cycle | `tier7/unified_cycle.py` |
| 8 | Temporal trends, rollback bundle index, mutation surface registry | `tier8/` |
| 9 | Live governed skill mutation with rollback execution | `tier9/` |
| 10 | Trend-fed cadence, rollback candidate selection | `tier10/` |
| 11 | Confidence calibration contract | `tier11/` |
| 12 | Memory governance, provenance registry, decay reconciliation | `tier12/` |
| 13 | Commitment ledger, reconciliation, status reporting | `tier13/` |
| 14 | Domain-agnostic causal query API, behavioral regression suite | `tier14/causal_query_api.py` |

---

## SECTION 2 — AUREX WORKSPACE PROJECTS

**Base:** `~/.openclaw/agents/aurex/workspace/projects/`

| Project | Entry Point | Status | Notes |
|---------|------------|--------|-------|
| `xzenia-saas` | `app.py` (Flask) | ✅ VERIFIED | 90MB, 2323 py files, full SaaS with dashboard, billing, connectors, Stripe |
| `aion` | `app.py` (FastAPI) | ✅ VERIFIED | Autonomous intelligence ops; workers, services, cognitive layer |
| `imos` | `imos/` package (FastAPI) | ✅ VERIFIED | 4.8MB, 30 py files; full package structure |
| `denialnet` | `app.py` → `routes.py` (FastAPI) | ✅ VERIFIED | Claim intelligence protocol; fixed FastAPI 0.135 compat 2026-04-02 |
| `cpin` | `app.py` → `routes.py` (FastAPI) | ✅ VERIFIED | Child Protection Intelligence Network; app.py created 2026-04-02 |
| `verifiagent` | `app.py` (FastAPI) | ✅ VERIFIED | Verification agent service |
| `agent-studio` | `server.py` | ✅ VERIFIED | Agent orchestration studio with MCP |
| `adversarial-coder` | `agent_harness.py` | ✅ VERIFIED | Adversarial code review harness |
| `context-nexus` | `services/` | ✅ VERIFIED | Cross-session memory + plugin |

---

## SECTION 3 — IMPORTS / ACQUIRED EXTERNAL ASSETS

**Base:** `~/.openclaw/workspace/imports/`

| Asset | Location | Status | Notes |
|-------|----------|--------|-------|
| `hybrid_causal_runtime` | `imports/hybrid_causal_runtime/` | ⚠️ DEGRADED | Last validation: rate_limit errors; 6/6 tests previously passed |
| `xzenith-drive` | `imports/xzenith-drive/` | ⚠️ UNVERIFIED | Salvage extraction completed; payload recovered; integration pending |

---

## SECTION 4 — ACTIVE LaunchAGENTS

| Label | Interval | Status | Purpose |
|-------|----------|--------|---------|
| `com.xzenia.nexus.loop` | 3x daily | ✅ LOADED exit=0 | NEXUS commerce loop |
| `com.xzenia.evolution` | on-schedule | ✅ LOADED exit=0 | Evolution engine cycle |
| `com.xzenia.swarm` | on-schedule | ✅ LOADED exit=0 | Swarm meta-cognition |
| `com.xzenia.tier5.cognitive` | 4x daily | ✅ LOADED exit=0 | Cognitive engine cycle |
| `com.xzenia.tier1.recovery` | periodic | ✅ LOADED exit=0 | Tier 1 boot/integrity |
| `com.xzenia.unified.cycle` | periodic | ✅ LOADED exit=0 | Tier 7 unified orchestration |
| `com.xzenia.trend.proposal.cycle` | periodic | ✅ LOADED exit=0 | Tier 10 trend proposals |
| `com.xzenia.adaptive.resume` | periodic | ✅ LOADED exit=0 | Tier 6 adaptive resume |
| `com.xzenia.autonomy.refresh` | periodic | ✅ LOADED exit=0 | Tier 4 autonomy refresh |
| `com.xzenia.critical.refresh` | periodic | ✅ LOADED exit=0 | Critical node hardening |
| `com.xzenia.priority.refresh` | periodic | ✅ LOADED exit=0 | Tier 5 bottleneck ranking |
| `com.xzenia.model-guardian` | periodic | ✅ LOADED exit=0 | Model health monitoring |
| `com.xzenia.api-error-watchdog` | periodic | ✅ LOADED exit=0 | API error monitoring |
| `com.xzenia.resurrection` | periodic | ✅ LOADED exit=0 | Session resurrection layer |
| `com.xzenia-saas.scanner` | periodic | ✅ LOADED exit=0 | SaaS revenue scanner |
| `com.xzenia.county-homelessness-monitor` | persistent | 🔄 RUNNING pid=43923 | County homelessness monitor web app on :8767 |
| `com.xzenia.browser.agent` | periodic | ✅ LOADED exit=0 | Browser automation agent |

**NOT LOADED (plist exists but never bootstrapped):**
- `com.xzenia.evolution.loop` — duplicate of `com.xzenia.evolution`? Investigate.

---

## SECTION 5 — SKILLS LIBRARY

**Location:** `~/.openclaw/workspace/skills/`
**Count:** 41 skills with SKILL.md, 27 packaged .skill artifacts in `dist/`

### Revenue Intelligence
| Skill | Status | Purpose |
|-------|--------|---------|
| `revenue-recovery` | ✅ | Core revenue orchestration |
| `contract-parser` | ✅ | Parse billing contracts for leakage |
| `financial-telemetry` | ✅ | Ingest Stripe/Salesforce/QBO data |
| `causal-engine` | ✅ | DoWhy/EconML causal inference |
| `causal-operations` | ✅ | Operationalize causal analysis |
| `recovery-actions` | ✅ | Generate prioritized recovery plans |
| `executive-briefing` | ✅ | Stakeholder-ready reports |

### Strategic
| Skill | Status | Purpose |
|-------|--------|---------|
| `moat-engine` | ✅ | Identify + score hard-to-copy advantages |
| `strategic-blindspot-hunter` | ✅ | Find underbuilt market infrastructure |
| `substrate-capital-allocator` | ✅ | Allocate build effort to highest-leverage |
| `deployment-productizer` | ✅ | Convert capabilities to deployable packages |
| `background-research-metabolism` | ✅ | Recurring strategic research loops |
| `infrastructure-productizer` | ✅ | Internal infra to external product |

### Substrate / Self-Improvement
| Skill | Status | Purpose |
|-------|--------|---------|
| `meta-healing` | ✅ | Self-diagnose + repair runtime health |
| `substrate-optimizer` | ✅ | Optimize + stabilize substrate |
| `substrate-auditor` | ✅ | Freeze drift, restore integrity |
| `substrate-cartographer` | ✅ | Map substrate topology |
| `governed-mutation-engineer` | ✅ | Safe controlled self-modification |
| `governed-substrate-cycle` | ✅ | Full governed mutation cycle |
| `frontier-evolver` | ✅ | Generate next governed frontier |
| `skill-harvester` | ✅ | Convert lessons to durable skills |
| `creation-engine` | ✅ | Generate reusable scaffolds |

### Autonomy / Execution
| Skill | Status | Purpose |
|-------|--------|---------|
| `next-step-autonomy` | ✅ | Execute obvious next steps without prompting |
| `iteration-engine` | ✅ | Iterative self-improvement cycles |
| `autonomy-loop-guard` | ✅ | Detect + break unproductive loops |
| `continuity-architect` | ✅ | Cross-session continuity architecture |
| `resilience-fabric` | ✅ | Autonomous fallback + self-healing |
| `causal-depth-builder` | ✅ | Build causal depth in analysis |

### Operational
| Skill | Status | Purpose |
|-------|--------|---------|
| `daily-heartbeat` | ✅ | Daily briefing to Aurex via Telegram |
| `mac-execution-bridge` | ✅ | Mac UI perception + control |
| `context-nexus` | ✅ | Persistent cross-session memory plugin |
| `model-guardian` | ✅ | Model health + fallback management |
| `audit-trail` | ✅ | Audit logging |
| `adversarial-review` | ✅ | Red-team own skills |
| `pattern-operations` | ✅ | Prevent shallow business idea drift |
| `vision-analyzer` | ✅ | Image analysis workflows |
| `cloud-burst` | ✅ | Cloud burst execution |

---

## SECTION 6 — GOVERNANCE LAYER

**Location:** `~/.openclaw/workspace/system/`

| Document | Purpose |
|----------|---------|
| `SUBSTRATE-LAW.md` | Hard rules: what gets built and how |
| `LONG-HORIZON-CONSTITUTION.md` | Multi-year operating contract |
| `STRATEGIC-REFUSAL-CHARTER.md` | What we will not build |
| `UNHEARD-OF-DOCTRINE.md` | Competitive positioning |
| `XZENIA-RECONSTITUTION-PROTOCOL-v1.0.pdf` | Recovery protocol if catastrophic failure |
| `autopilot/` | Autopilot governance configs |
| `metacog/` | Metacognition system configs |
| `sovereignty/` | Sovereignty architecture docs |

---

## SECTION 7 — INSTALLED PYTHON DEPENDENCIES (system)

**Python:** 3.14.3 at `/usr/local/bin/python3`
**Verified installed (2026-04-02):**
- sqlalchemy 2.0.48, aiosqlite 0.22.1, aiohttp 3.13.5
- fastapi 0.135.3, uvicorn 0.42.0, pydantic 2.12.5, pydantic-settings 2.13.1
- redis 7.4.0, psycopg2-binary 2.9.11
- openai 2.30.0, anthropic 0.88.0, httpx 0.28.1
- stripe 15.0.0, pandas 3.0.1, numpy 2.4.3
- celery 5.6.3, alembic 1.18.4
- flask (latest), flask-limiter, flask-wtf
- cryptography, PyJWT 2.12.1
- requests 2.32.5, python-dotenv, python-multipart

---

## SECTION 8 — KNOWN GAPS / NEXT VERIFICATION NEEDED

| Item | Gap | Priority |
|------|-----|----------|
| `hybrid_causal_runtime` | Rate limit errors on last 3 validation runs | HIGH |
| `xzenith-drive` | Acquired/salvaged but not integrated | MEDIUM |
| `com.xzenia.evolution.loop` | Plist exists but not loaded; may be duplicate | LOW |
| Redis | Configured but running in fallback mode | MEDIUM |
| Stripe | Link deactivated (plink_1TDz0BAc6hzX3Jk1BD6vskqV) | HIGH |
| 8 outreach leads | 10+ days, 0 replies | HIGH |
| client_001 leakage report | Pending approval since 2026-03-18 | HIGH |
| CSMR | Individual tier scripts not re-verified this session | LOW |

---

*This file is the ground truth. Do not add entries without running the verification test.*
*Last full sweep: 2026-04-02 21:45 EDT by Xzenia*
