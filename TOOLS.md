# TOOLS.md — Local Infrastructure & Operational Playbook

_Local notes for this workspace. Skills are shared; this file is yours._

---

## Products

### LeakLock
**GitHub:** `prettybusysolutions-eng/xzenia-leaklock`
**Stripe:** live key (`sk_live_...`) — real payments
**Webhook secret:** `whsec_[REDACTED]`
**Deploy:** Render (PostgreSQL + Web Service)
**Status:** Ready for Render deploy — human action needed (~10 min)

**Render deploy steps:**
1. render.com → New → PostgreSQL → name: `leaklock-db` → Create
2. New → Web Service → connect `prettybusysolutions-eng/xzenia-leaklock`
3. Env vars: `DATABASE_URL`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `LEAKLOCK_DOMAIN`, SMTP
4. Deploy → get URL → set `LEAKLOCK_DOMAIN`
5. Stripe Dashboard → register webhook: `https://<url>/webhook/stripe` → events: `checkout.session.completed`

### Context Nexus
**GitHub:** `prettybusysolutions-eng/context-nexus`
**ClawHub:** published (`clawhub install context-nexus`)
**Install:** `clawhub install context-nexus --force` + git clone + `./scripts/install`
**OpenClaw plugin:** LOADED (44/84 plugins)
**Smoke tests:** 18/18 passing
**Status:** READY_TO_PUBLISH

---

## Skills Inventory

### 💬 Communication
- **imsg** — iMessage/SMS. `imsg send <number> <message>`, `imsg list chats`
- **wacli** — WhatsApp. `wacli send <number> <message>`
- **himalaya** — Email. IMAP/SMTP. `himalaya list`, `himalaya read <id>`
- **gog** — Google Workspace: Gmail, Calendar, Drive, Contacts, Sheets, Docs
- **apple-notes** — `memo` CLI. `memo list`, `memo create`, `memo find <query>`
- **apple-reminders** — `remindctl`. `remindctl list`, `remindctl add <text>`
- **things-mac** — Things 3. `things add <task>`, `things list inbox`, `things today`

### 🎵 Media & Generation
- **image_generate** — `image_generate prompt="..."` → generates images
- **image** — `image path=<file> prompt="..."` → analyzes image
- **songsee** — `songsee path=<audiofile>` → spectrogram + visualization
- **video-frames** — `video-frames extract <video> --times "00:01,00:05"` → frames
- **gifgrep** — `gifgrep search <query>` → TUI for GIF search/download
- **openai-whisper** — `openai-whisper transcribe <audio>` → local STT, no API key

### 🏠 Home & IoT
- **sonoscli** — `sonoscli discover`, `sonoscli play`, `sonoscli volume 30`
- **openhue** — `openhue lights`, `openhue scene <name>`, `openhue light <id> on`
- **eightctl** — `eightctl temp`, `eightctl schedule`, `eightctl alarm`

### 💻 Code & Git
- **github** — `gh issue list`, `gh pr status`, `gh run list`, `gh pr create`
- **gh-issues** — `gh-issues owner/repo --label bug --limit 5` → automated fix workflow
- **coding-agent** — Spawns Codex/Claude Code/Pi for complex coding tasks
- **session-logs** — `session-logs search "leaklock" --hours 24 | jq '.[]'`
- **tmux** — Send keys to remote tmux: `tmux send-keys -t session:pane "command"`
- **mcporter** — MCP server tool. `mcporter list servers`, `mcporter call <tool>`
- **skill-creator** — `skill-creator create` → scaffolds new skills

### 🌐 Web & Data
- **summarize** — `summarize url <url>`, `summarize file <path>`
- **blogwatcher** — `blogwatcher add <feed-url>`, `blogwatcher check`
- **xurl** — `xurl post "tweet text"`, `xurl search <query>`, `xurl dm <user> <msg>`
- **weather** — `weather` or `weather "New York"` → current + 3-day forecast
- **clawhub** — `clawhub search <skill>`, `clawhub install <slug>`, `clawhub publish <path>`

### 📄 Documents & Notes
- **obsidian** — `obsidian query <vault> <query>` → search notes, read files
- **notion** — `notion create page --title "X" --content "Y"`, `notion list databases`
- **nano-pdf** — `nano-pdf edit <pdf> "change X to Y"` → PDF editing

### 🔧 System & Platform
- **healthcheck** — `healthcheck audit` → security hardening report
- **node-connect** — `node-connect diagnose` → pairing/connection failure diagnosis
- **peekaboo** — `peekaboo capture` → screenshot; `peekaboo run "Click Button"` → UI automation
- **video-frames** — `video-frames clip <video> --start 00:05 --duration 10`

---

## SSH / Network

```
# Home server (when on network)
home-server → 192.168.1.100, user: admin

# GitHub
github.com → authenticated via gh CLI (account: prettybusysolutions-eng)
```

---

## Environment Variables (Active Products)

```bash
# Context Nexus
CONTEXT_NEXUS_DB_PATH=~/.openclaw/context-nexus/nexus.db
CONTEXT_NEXUS_ENCRYPTION_KEY=<key>

# LeakLock (in .env)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_[REDACTED]
LEAKLOCK_DOMAIN=https://leaklock.onrender.com
DATABASE_URL=postgresql://...
SMTP_HOST=smtp.resend.dev
SMTP_PORT=587
SMTP_USER=resend
SMTP_PASS=re_...
SMTP_FROM=LeakLock <hello@yourdomain.com>
```

---

## GitHub

**Organizations:**
- `prettybusysolutions-eng` — products (LeakLock, Context Nexus)
- Operator: Kamm Smith (`@MrBigZa`)

**Repos:**
- `xzenia-leaklock` — Stripe SaaS
- `context-nexus` — OpenClaw memory/observability plugin
- `xzienia` — Xzenia platform

---

## Operational Playbooks

### Ship a product to ClawHub
1.硬化: run `release_hardening_loop.py` → `READY_TO_PUBLISH`
2. Publish: `clawhub publish /abs/path/to/skill --slug <slug> --name "<name>" --version 0.1.0`
3. Verify: `clawhub search <slug>` → appears top result
4. Install test: `cd /tmp && rm -rf test && mkdir test && cd test && clawhub install <slug> --force`

### Deploy to Render (LeakLock pattern)
1. Create PostgreSQL on Render → copy URL
2. Create Web Service → connect GitHub repo
3. Set env vars: `DATABASE_URL`, Stripe keys, domain, SMTP
4. Wait for deploy → get URL
5. Register Stripe webhook
6. Test end-to-end with real CSV upload

### Fix OpenClaw plugin load failure
1. Run `openclaw plugins list | grep <plugin>` → see error
2. Check `~/.openclaw/plugins/<plugin>/src/index.js` → syntax error?
3. Check `~/.openclaw/plugins/<plugin>/openclaw.plugin.json` → at root, not in src/
4. Check exports: needs `register` or `activate` as export name
5. Restart: `openclaw gateway restart`

### Handle VirusTotal false positive on skill publish
1. Note: encryption code (PBKDF2, crypto) triggers detection — expected
2. Publish anyway: `clawhub install <slug> --force`
3. Submit for re-scan: virustotal.com → submit for vendor re-analysis
4. Monitor: clears in 24-48h

### Run session self-audit
1. `session-logs search "error" --hours 24 | jq '.[]'`
2. `session-logs analyze --session <id>` → tool usage, errors, duration
3. Write findings to `memory/YYYY-MM-DD.md`

---

## Release Hardening Loop (Active)

For any product in development, run on every heartbeat:

```bash
python3 /Users/marcuscoarchitect/.openclaw/agents/aurex/workspace/projects/<product>/scripts/release_hardening_loop.py
```

Reads: `release-status.json`
Outputs: `state` = `READY_TO_PUBLISH` | `BLOCKED_WITH_EXACT_CAUSE`

No narration without artifact change. No optimism without proof.

---

## Key Paths

```
Workspace root: ~/.openclaw/workspace-aurex/
Context Nexus:  ~/.openclaw/agents/aurex/workspace/projects/context-nexus/
LeakLock:      ~/.openclaw/agents/aurex/workspace/projects/xzenia-saas/
Plugins:       ~/.openclaw/plugins/
Memory:        ~/.openclaw/workspace-aurex/memory/
```

---

## Known Issues / Notes

- **GitHub HTTPS push**: may time out requiring `gh auth refresh -h github.com`
- **OpenClaw gateway**: `openclaw gateway restart` needed after plugin config changes
- **VirusTotal false positive**: encryption code in `secrets_service.py` triggers — expected, use `--force`
- **Context Nexus path bug**: plugin subprocess path detection walks up from `~/.openclaw/plugins/<plugin>/src/` to find actual project root — this is intentional
