# Drift Closure Matrix

Last updated: 2026-04-13 13:23 EDT
Status: ACTIVE

## Dirty tracked files
- `.gitignore` -> KEEP, inspect and normalize if still needed for thin-root policy
- `memory/errors.md` -> KEEP LOCAL, do not promote by default
- `projects/xzenia/state/resume-queue.json` -> KEEP CANONICAL if current state policy still treats it as promoted execution state
- `skills/genesis-v2/SKILL.md` -> REVIEW FOR PROMOTION or KEEP LOCAL until classified

## Root untracked files
- `SYSTEM-HEALTH-REPORT-20260318.md` -> ARCHIVE OR PROMOTE after authority check
- `SYSTEM-SCAN-FULL-20260318.md` -> ARCHIVE OR PROMOTE after authority check
- `claude-task*.txt` -> ARCHIVE/IGNORE, not canonical authority
- `create_video1.py`, `gen_*`, `generate_*`, `record_xzenia.sh`, `phase5_steps6to10.py`, `setup_stripe.py` -> MOVE to project-specific ownership or ignore/archive

## Root untracked directories
- `architecture/` -> REVIEW, possibly promote selected canonical docs only
- `automation/` -> REVIEW, likely move under system or project ownership

## Memory drift
- hidden cron/dream/archive files under `memory/` -> IGNORE/ARCHIVE, not root authority

## Xzenia subtree drift
- `projects/xzenia/**/__pycache__/` -> IGNORE
- logs, state dumps, benchmark reports, ui session files -> IGNORE unless specifically promoted
- agent json definitions and selected domain surfaces -> REVIEW FOR PROMOTION
- model guardian runtime logs/state/config backups -> IGNORE except canonical source files

## Skills subtree drift
- many untracked skill directories -> REVIEW FOR PROMOTION IN BATCH
- references/ directories -> IGNORE unless they are required canonical references
- generated skill test surfaces -> ARCHIVE or demote

## System subtree drift
- `system/autopilot/`, `system/metacog/`, `system/sovereignty/` -> REVIEW FOR PROMOTION
- protocol PDF -> ARCHIVE/REFERENCE, not default canonical authority

## Immediate safe tranche
1. ignore obvious caches/logs/generated runtime residue
2. write authority decisions for root loose files
3. stage only policy/report artifacts, not runtime dumps
