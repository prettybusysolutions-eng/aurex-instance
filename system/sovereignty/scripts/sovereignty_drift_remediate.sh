#!/usr/bin/env bash
set -euo pipefail

# Host-level drift remediation script (for SSM execution)
# Safe/idempotent checks only.

sudo systemctl daemon-reload || true

# Ensure security + telemetry agents stay on
sudo systemctl enable --now fail2ban || true
sudo systemctl enable --now amazon-cloudwatch-agent || true
sudo systemctl restart amazon-cloudwatch-agent || true

# Ensure firewall baseline
sudo ufw --force enable || true
sudo ufw default deny incoming || true
sudo ufw default allow outgoing || true
sudo ufw allow 22/tcp || true

# Ensure swap exists (4G minimum)
if ! swapon --show | grep -q .; then
  sudo fallocate -l 4G /swapfile || sudo dd if=/dev/zero of=/swapfile bs=1M count=4096
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  grep -q '^/swapfile ' /etc/fstab || echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

# Ensure unattended upgrades
sudo dpkg-reconfigure -f noninteractive unattended-upgrades || true

echo "SOV_DRIFT_REMEDIATE_OK"
