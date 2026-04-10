# XZENIA UNIFIED BRIDGE ARCHITECTURE v2.0
<!-- bridge-version: 2.0 -->
<!-- Location: ~/.openclaw/workspace/BRIDGE.md -->
<!-- Read by: BOOT.md (on every startup), HEARTBEAT.md (every cycle), all skills (on invocation) -->
<!-- Owner: Aurex | Operator: Xzenia -->

**Purpose:** This document is the connective tissue between every .md file in the Xzenia workspace. It defines the dependency graph, data flow contracts, read/write ownership, and operational sequencing that makes the entire system function as one organism rather than a collection of separate documents.

---

## §1 — FILE REGISTRY & DEPENDENCY GRAPH

Every file in the workspace has exactly one owner, a defined read/write contract, and explicit dependencies. No file exists in isolation.

### §1.1 Identity Layer (Read at Boot, Rarely Written)

| File | Purpose | Owner | Read By | Write Conditions |
|------|---------|-------|---------|-----------------|
| SOUL.md | Core identity, values, operating principles, confidence calibration model | Aurex | BOOT.md → all sessions | Values section: Aurex review only. Thresholds: Xzenia updates via metacognition with justification logged to MEMORY.md |
| USER.md | Aurex profile, contact mapping (Telegram: Kamm Smith → Aurex), communication preferences | Aurex | BOOT.md → all sessions | Xzenia may append new contact mappings; Aurex approves identity changes |
| IDENTITY.md | Agent name, version, codename, creation metadata | Aurex | BOOT.md | Immutable unless Aurex explicitly upgrades version |

**Dependency chain:** BOOT.md reads IDENTITY.md → SOUL.md → USER.md in that exact order. If any file is missing or corrupted, halt and report.

### §1.2 Operational Layer (Read/Write Every Session)

| File | Purpose | Owner | Read By | Write Conditions |
|------|---------|-------|---------|-----------------|
| MEMORY.md | Session state, last-known-good checkpoint, active task queue, context carryover | Xzenia | BOOT.md, HEARTBEAT.md, all skills | Written at: session end, every 30 min during long tasks, on crash recovery |
| HEARTBEAT.md | Autonomous loop template — defines what Xzenia checks and reports on each cycle | Aurex | Gateway cron | Xzenia proposes changes via self-build skill; Aurex approves |
| BOOT.md | Startup sequence — the ordered checklist Xzenia runs on every wake event | Aurex | Gateway on session init | Xzenia proposes additions; Aurex approves structural changes |
| TOOLS.md | Available tool inventory, MCP servers, API endpoints, rate limits | Aurex | All skills on invocation | Xzenia updates availability status; Aurex adds/removes tools |

**Dependency chain:** On every session start, BOOT.md orchestrates: read BRIDGE.md → read Identity Layer → read MEMORY.md (for resume state) → read TOOLS.md (for available capabilities) → execute HEARTBEAT if scheduled.

### §1.3 Intelligence Layer (Compounds Over Time)

| File/Directory | Purpose | Owner | Read By | Write Conditions |
|----------------|---------|-------|---------|-----------------|
| memory/daily/*.md | Daily causal memory entries — action, context, outcome, causal hypothesis | Xzenia | Metacognition skill, weekly synthesis | Written automatically after every significant action |
| memory/weekly/*.md | Weekly causal synthesis — patterns, cross-domain transfers, graph updates | Xzenia | Monthly review, skill-valuation | Written by weekly cron job |
| memory/monthly/*.md | Monthly strategic synthesis — compounding insights, model updates | Xzenia | Quarterly review | Written by monthly cron job |
| memory/self-model.md | Current strengths, weaknesses, calibration accuracy, domain track records | Xzenia | Deliberation skill, confidence engine | Updated nightly by metacognition |
| memory/patterns.md | Learned domain heuristics, reusable strategies | Xzenia | All skills | Appended when new pattern confidence > 0.7 |
| memory/errors.md | Error log with root cause, patch applied, verification status | Xzenia | Adversarial skill, boot sequence | Written immediately on error detection |
| memory/pipeline.md | GTM pipeline state, ICP targets, outreach status, deal stages | Xzenia | Revenue skills | Updated after every pipeline-relevant action |

**Dependency chain:** Daily entries → weekly synthesis → pattern extraction → self-model update → confidence calibration adjustment. This is the core compounding loop.

### §1.4 Skill Layer (Operational Playbooks)

The workspace skill registry is dynamic. Canonical inventory is the installed set under `~/.openclaw/workspace/skills/*/SKILL.md`.
At current audit, the installed skill directories are:

- skills/adversarial-review/
- skills/audit-trail/
- skills/autonomy-loop-guard/
- skills/background-research-metabolism/
- skills/causal-depth-builder/
- skills/causal-engine/
- skills/causal-operations/
- skills/cloud-burst/
- skills/context-nexus/
- skills/continuity-architect/
- skills/contract-parser/
- skills/creation-engine/
- skills/daily-heartbeat/
- skills/deployment-productizer/
- skills/email-delivery/
- skills/executive-briefing/
- skills/financial-telemetry/
- skills/frontier-evolver/
- skills/generated_33f96160/
- skills/generated_test123/
- skills/genesis-v2/
- skills/governed-mutation-engineer/
- skills/governed-substrate-cycle/
- skills/infrastructure-productizer/
- skills/iteration-engine/
- skills/mac-execution-bridge/
- skills/meta-healing/
- skills/moat-engine/
- skills/model-guardian/
- skills/next-step-autonomy/
- skills/pattern-operations/
- skills/recovery-actions/
- skills/resilience-fabric/
- skills/revenue-recovery/
- skills/skill-harvester/
- skills/strategic-blindspot-hunter/
- skills/substrate-auditor/
- skills/substrate-capital-allocator/
- skills/substrate-cartographer/
- skills/substrate-optimizer/
- skills/vision-analyzer/

**Skill execution contract:** Every skill MUST (1) read BRIDGE.md to know its data sources, (2) write results to its designated output targets, (3) log a causal memory entry for every non-trivial action.

### §1.5 Configuration Layer

| File | Purpose | Owner | Notes |
|------|---------|-------|-------|
| AGENTS.md | Workspace operating rules, cron schedule, group chat behavior | Aurex | Core operating contract |
| SOUL.md | Values + confidence calibration thresholds | Aurex/Xzenia | Shared ownership per §1.1 |
| marketplace-scaffold/src/services/db_layer.py | PostgreSQL connection pool, circuit breaker, retry logic | Xzenia | Resilient connection management |
| marketplace-scaffold/src/services/repositories.py | Data access layer (DemandRepository, SupplyRepository) | Xzenia | Unified persistence interface |

### §1.6 Persistence Layer (v4.0 ENTERPRISE)

| Component | Purpose | Location | Status |
|-----------|---------|----------|--------|
| PostgreSQL 16.13 | Primary database | localhost:5432/nexus | Running |
| Redis | Cache, rate limit, audit, events | localhost:6379 | Running |
| NexusOrchestrator | PostgreSQL + Redis unified | db_layer.py | Active |
| EnterpriseInfrastructure | CDC, Graph, Replicas, Backup | enterprise_infra.py | Active |

**v4.0 ENTERPRISE Features:**

| Feature | Implementation | Status |
|---------|---------------|--------|
| **CDC** | PostgreSQL NOTIFY + trigger-based | Working |
| **Graph** | Neo4j integration | Ready (needs Neo4j) |
| **Read Replicas** | PgBouncer-style router | Ready |
| **Backup** | pg_dump + S3 upload + retention | Ready |
| **Rate Limiter** | Redis-backed (sliding window) | Working |
| **Cache** | Redis-backed (TTL, pattern invalidation) | Working |
| **Audit** | Redis-backed + compliance | Working |
| **Circuit Breaker** | Redis-backed state | Working |

**Unification rule:** Every new component MUST write to PostgreSQL via db_layer.py → enterprise_infra.py. No standalone stores.

**Causal activation:**
```
loop_controller → demand_repo → PostgreSQL
                               → Redis (cache, rate limit, audit)
                               → CDC (change capture)
                               → Graph (relationship sync)
```

**Enterprise infrastructure:**
- CDC watches: demand_requests, fulfillment_executions, loop_runs
- Graph sync: demand → fulfillment relationships
- Backup: daily auto-backup to S3 with 30-day retention
- Replicas: round-robin or least-connections routing

---

## §2 — DATA FLOW CONTRACTS

### §2.1 Revenue Recovery Pipeline
```
Client Data → financial-telemetry → xzenia-data/
xzenia-data/ + patterns.md → causal-engine → causal findings
causal findings + pipeline.md → recovery-actions → action plans
action plans + pipeline.md → executive-briefing → stakeholder reports
```

### §2.2 Intelligence Compounding Loop
```
Significant action → memory/daily/YYYY-MM-DD.md
daily entries (weekly) → memory/weekly/YYYY-WW.md
weekly synthesis → patterns.md (if confidence > 0.7)
patterns.md → self-model.md (nightly via metacognition)
self-model.md → confidence calibration adjustment
```

### §2.3 Error Recovery Flow
```
Error detected → memory/errors.md (immediate)
errors.md → xzenia-adversarial (root cause analysis)
xzenia-adversarial → skill patch proposal → Aurex approval
approved patch → skill update → verification entry in errors.md
```

### §2.4 Session Continuity Flow
```
Session start → BOOT.md → MEMORY.md checkpoint read
MEMORY.md → resume state OR fresh start
Session end / 30min interval → MEMORY.md checkpoint write
Crash → BOOT.md detects stale checkpoint → recovery mode
```

---

## §3 — READ/WRITE OWNERSHIP MATRIX

| File | Reader | Writer | Frequency |
|------|--------|--------|-----------|
| SOUL.md | All sessions | Aurex (values) / Xzenia (thresholds with log) | Rarely |
| USER.md | All sessions | Aurex (identity) / Xzenia (contact mappings) | On change |
| IDENTITY.md | BOOT.md | Aurex only | Version upgrades |
| MEMORY.md | BOOT.md, all skills | Xzenia | Every 30min + session boundaries |
| HEARTBEAT.md | Gateway cron | Aurex (structure) / Xzenia (proposes) | On schedule change |
| BOOT.md | Gateway init | Aurex (approves) / Xzenia (proposes) | On sequence change |
| TOOLS.md | All skills | Aurex (add/remove) / Xzenia (status) | On tool change |
| memory/daily/ | Metacognition | Xzenia | After every significant action |
| memory/weekly/ | Monthly review | Xzenia (weekly cron) | Weekly |
| memory/errors.md | Boot, adversarial | Xzenia | On error detection |
| memory/pipeline.md | Revenue skills | Xzenia | After pipeline actions |

---

## §4 — INTEGRITY CHECKS

Run at boot (BOOT.md step 9) and on demand:

### §4.1 File Existence Check
- All §1.1 identity files present
- All §1.2 operational files present
- All §1.3 intelligence directories and files present
- All §1.4 skill directories have SKILL.md

### §4.2 Staleness Check
- MEMORY.md last checkpoint < 24 hours (warn if exceeded)
- memory/daily/ has entry for today (warn if missing)
- self-model.md updated within 7 days (warn if stale)
- pipeline.md updated within 48 hours (warn if stale)

### §4.3 Consistency Check
- Confidence thresholds in SOUL.md are numeric and in [0,1]
- Skills in §1.4 match actual skill directories
- TOOLS.md entries have status field

### §4.4 Failure Handling
- Identity layer failure → HALT, report to Aurex
- Operational layer gap → LOG to errors.md, continue with degraded state
- Intelligence layer gap → LOG, create missing file from template
- Skill layer gap → LOG, continue (skill will fail on invocation)

---

## §5 — AUTONOMY THRESHOLDS

| Action Type | Autonomy Level | Escalation |
|-------------|---------------|------------|
| Read any file | Full autonomy | Never |
| Write to memory/ | Full autonomy | Never |
| Write to workspace .md files | Full autonomy | Never |
| External API calls (read) | Full autonomy | On rate limit |
| External API calls (write/send) | Confirm with Aurex | Always |
| Delete any file | Confirm with Aurex | Always |
| Modify SOUL.md values section | Aurex only | Always |
| New skill creation | Propose to Aurex | Before shipping |

---

## §6 — WORKSPACE PATH REGISTRY

| Alias | Canonical Path |
|-------|---------------|
| workspace root | ~/.openclaw/workspace/ |
| data root | ~/.openclaw/xzenia-data/ |
| marketplace scaffold | ~/.openclaw/workspace/marketplace-scaffold/ |
| skills | ~/.openclaw/workspace/skills/ |
| memory | ~/.openclaw/workspace/memory/ |
| DEPRECATED | ~/.openclaw/xzenia-workspace/ (do not use) |

---

## §7 — VERSION & CHANGELOG

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-01 | Initial bridge concept |
| 2.0 | 2026-03-24 | Full formal spec, correct workspace paths, NEXUS integration |

---

*BRIDGE.md is the root dependency. If this file is missing, operate in degraded mode and report to Aurex immediately.*
