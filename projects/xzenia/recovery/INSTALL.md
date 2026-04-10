# Tier 1 Recovery Install

Install the LaunchAgent when ready:

```bash
chmod +x /Users/marcuscoarchitect/.openclaw/workspace/projects/xzenia/recovery/run_tier1_recovery.sh
mkdir -p ~/Library/LaunchAgents
cp /Users/marcuscoarchitect/.openclaw/workspace/projects/xzenia/recovery/com.xzenia.tier1.recovery.plist ~/Library/LaunchAgents/
launchctl unload ~/Library/LaunchAgents/com.xzenia.tier1.recovery.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/com.xzenia.tier1.recovery.plist
```

This runs Tier 1 recovery at load and every 15 minutes.
