import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

REPORTS_DIR = Path(os.environ.get("REPORTS_DIR", "./reports"))
NETWORKS_FILE = Path(os.environ.get("WATCH_NETWORKS_FILE", "./networks.json"))
WALLETS_FILE = Path(os.environ.get("WALLET_ADDRESSES_FILE", "./wallets.json"))
POLL_SECONDS = 900


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def rpc_call(rpc_url: str, method: str, params):
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    response = requests.post(rpc_url, json=payload, timeout=20)
    response.raise_for_status()
    data = response.json()
    if "error" in data:
        raise RuntimeError(data["error"])
    return data.get("result")


def get_gas_price_gwei(rpc_url: str):
    try:
        result = rpc_call(rpc_url, "eth_gasPrice", [])
        if not result:
            return None
        wei = int(result, 16)
        return wei / 1_000_000_000
    except Exception:
        return None


def get_balance_native(rpc_url: str, address: str):
    try:
        result = rpc_call(rpc_url, "eth_getBalance", [address, "latest"])
        if not result:
            return None
        wei = int(result, 16)
        return wei / 10**18
    except Exception:
        return None


def get_latest_block(rpc_url: str):
    try:
        result = rpc_call(rpc_url, "eth_blockNumber", [])
        return int(result, 16)
    except Exception:
        return None


def build_snapshot():
    networks = load_json(NETWORKS_FILE, [])
    wallets = load_json(WALLETS_FILE, [])
    snapshot = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "networks": [],
        "wallets": [],
    }

    for network in networks:
        rpc_url = network.get("rpc_url")
        if not rpc_url:
            continue
        snapshot["networks"].append(
            {
                "name": network.get("name", "unknown"),
                "rpc_url": rpc_url,
                "latest_block": get_latest_block(rpc_url),
                "gas_price_gwei": get_gas_price_gwei(rpc_url),
            }
        )

    for wallet in wallets:
        address = wallet.get("address")
        network_name = wallet.get("network")
        network = next((n for n in networks if n.get("name") == network_name), None)
        if not address or not network or not network.get("rpc_url"):
            continue
        snapshot["wallets"].append(
            {
                "label": wallet.get("label", address),
                "network": network_name,
                "address": address,
                "balance_native": get_balance_native(network["rpc_url"], address),
                "transaction_success_rate": None,
                "notes": "Success-rate tracking requires explorer/API integration per network.",
            }
        )

    return snapshot


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    while True:
        snapshot = build_snapshot()
        (REPORTS_DIR / "wallet-watch-latest.json").write_text(json.dumps(snapshot, indent=2))
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
