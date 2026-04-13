#!/usr/bin/env python3
"""
install_launchagent.py — Install/uninstall the model-guardian LaunchAgent.

Usage:
  python3 install_launchagent.py install
  python3 install_launchagent.py uninstall
  python3 install_launchagent.py status
"""
import subprocess
import sys
from pathlib import Path

LABEL = 'com.xzenia.model-guardian'
WORKSPACE = Path(__file__).parent
GUARDIAN = WORKSPACE / 'guardian_cycle.py'
LOG = WORKSPACE / 'guardian.log'
PLIST_DIR = Path.home() / 'Library' / 'LaunchAgents'
PLIST_PATH = PLIST_DIR / f'{LABEL}.plist'
PYTHON = sys.executable

PLIST_CONTENT = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
    "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{PYTHON}</string>
        <string>{GUARDIAN}</string>
    </array>
    <key>StartInterval</key>
    <integer>300</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{LOG}</string>
    <key>StandardErrorPath</key>
    <string>{LOG}</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>DAILY_TOKEN_BUDGET</key>
        <string>500000</string>
    </dict>
</dict>
</plist>
"""


def install():
    PLIST_DIR.mkdir(parents=True, exist_ok=True)
    PLIST_PATH.write_text(PLIST_CONTENT)
    # Unload first if already loaded
    subprocess.run(['launchctl', 'unload', str(PLIST_PATH)], capture_output=True)
    result = subprocess.run(['launchctl', 'load', str(PLIST_PATH)], capture_output=True, text=True)
    if result.returncode != 0:
        print(f'launchctl load failed: {result.stderr.strip()}')
        sys.exit(1)
    print(f'Installed: {PLIST_PATH}')
    print(f'Label: {LABEL}')
    print(f'Interval: every 300s (5 min)')
    print(f'Log: {LOG}')


def uninstall():
    if PLIST_PATH.exists():
        subprocess.run(['launchctl', 'unload', str(PLIST_PATH)], capture_output=True)
        PLIST_PATH.unlink()
        print(f'Uninstalled: {PLIST_PATH}')
    else:
        print('Not installed.')


def status():
    result = subprocess.run(['launchctl', 'list', LABEL], capture_output=True, text=True)
    if result.returncode == 0:
        print(f'RUNNING: {LABEL}')
        print(result.stdout.strip())
    else:
        print(f'NOT LOADED: {LABEL}')
    if PLIST_PATH.exists():
        print(f'Plist exists: {PLIST_PATH}')
    else:
        print('Plist not installed.')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'
    if cmd == 'install':
        install()
    elif cmd == 'uninstall':
        uninstall()
    elif cmd == 'status':
        status()
    else:
        print(f'Unknown command: {cmd}')
        sys.exit(1)
