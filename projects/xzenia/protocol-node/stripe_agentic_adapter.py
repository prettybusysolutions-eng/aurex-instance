#!/usr/bin/env python3
import json
import os
import time
from pathlib import Path
from stripe_payment_intent_verify import verify_payment_intent

LEDGER = Path('/Users/marcuscoarchitect/.openclaw/workspace/private/billing-ledger.jsonl')
GRANTS = Path('/Users/marcuscoarchitect/.openclaw/workspace/projects/xzenia/protocol-node/translate-grants.json')
PAYMENT_LINK = 'https://buy.stripe.com/fZuaEWa48ewz4RGewS0kE08'
TTL_SECONDS = 60


def _load_grants():
    if not GRANTS.exists():
        return {}
    try:
        return json.loads(GRANTS.read_text())
    except Exception:
        return {}


def _save_grants(data):
    GRANTS.write_text(json.dumps(data, indent=2) + '\n')


def proof_seen(payment_intent_id: str) -> bool:
    if LEDGER.exists():
        for line in LEDGER.read_text().splitlines():
            if payment_intent_id and payment_intent_id in line:
                return True
    grants = _load_grants()
    return payment_intent_id in grants


def verify_proof(proof: dict):
    required = ['payment_intent_id', 'timestamp', 'machine_signature']
    if not all(proof.get(k) for k in required):
        return False, 'missing_fields'
    if proof_seen(proof['payment_intent_id']):
        return False, 'replay_detected'
    if os.getenv('X402_SETTLEMENT_PROVIDER', 'dry-run') == 'stripe_agentic':
        result = verify_payment_intent(proof['payment_intent_id'])
        if not result.get('ok'):
            return False, result.get('error', 'verification_failed')
    return True, 'accepted_for_grant'


def issue_grant(proof: dict):
    grants = _load_grants()
    token = proof.get('grant_token') or proof['payment_intent_id']
    grants[token] = {
        'payment_intent_id': proof['payment_intent_id'],
        'expires_at': time.time() + TTL_SECONDS,
        'mode': os.getenv('X402_MODE', 'dry-run'),
    }
    _save_grants(grants)
    return token


def grant_valid(token: str) -> bool:
    grants = _load_grants()
    row = grants.get(token)
    if not row:
        return False
    return time.time() < float(row.get('expires_at', 0))
