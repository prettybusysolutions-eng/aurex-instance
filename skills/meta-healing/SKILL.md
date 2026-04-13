---
name: meta-healing
description: Diagnose, harden, repair, and improve local OpenClaw/agent runtime health without destructive resets. Use when asked to self-heal, recover capabilities, audit configuration drift, repair package/tooling issues, validate service health, reduce warnings, or improve resilience without breaking active messaging/gateway state.
---

# Meta Healing

Stabilize first. Expand second. Do not destroy working state to chase completeness.

## Operating rules

- Prefer non-disruptive actions.
- Do not restart the gateway or active messaging services unless the user explicitly asks or there is a confirmed outage that cannot be fixed in-place.
- Back up config before editing it.
- Prefer additive installs and reversible config changes.
- Validate after each meaningful change.
- If a requested action would expand autonomy beyond user control, frame it as local tooling enablement, not unchecked self-direction.

## Core workflow

1. Run a baseline health snapshot:
   - `openclaw status`
   - `openclaw security audit`
   - `brew list --versions`
2. Identify constraints:
   - active sessions
   - gateway reachability issues
   - package/version drift
   - missing common CLI utilities
   - config warnings
3. Apply safest improvements first:
   - install broadly useful CLI tools
   - fix symlink/version mismatches
   - add missing non-breaking security settings
   - document local capabilities
4. Re-validate:
   - repeat `openclaw status`
   - confirm installed tool versions
   - check config JSON validity before/after edits
5. Persist learnings:
   - update workspace notes or memory files if the changes matter long-term

## Config editing pattern

Before editing `~/.openclaw/openclaw.json`:

- copy to `openclaw.json.bak.<timestamp>`
- make the smallest possible edit
- verify parse with `jq . ~/.openclaw/openclaw.json >/dev/null`

## Capability expansion shortlist

Install only what improves general local operations with low risk:

- JSON/YAML/text: `jq`, `yq`, `ripgrep`, `fd`
- media: `ffmpeg`, `imagemagick`, `yt-dlp`
- package/runtime: `pnpm`
- shell/inspection: `tree`, `watch`, `htop` or `btop`
- git/network utility: `git-delta`, `gh`, `wget`
- GNU helpers: `coreutils`, `moreutils`

Avoid invasive daemons, security-sensitive remote access tools, or anything that silently changes network exposure unless specifically requested.

## References

- Read `references/checklist.md` for a concise audit/remediation checklist.
- Use `scripts/backup-openclaw-config.sh` before config edits.
- Use `scripts/config-drift-check.sh` to detect persisted config changes.
- Use `scripts/prune-meta-healing.sh` to limit snapshot/log growth.
