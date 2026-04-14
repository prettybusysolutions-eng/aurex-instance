#!/usr/bin/env python3
import json
import os
from pathlib import Path
import stripe

MACHINE_LEDGER = Path('/Users/marcuscoarchitect/.openclaw/workspace/private/machine-settlement-ledger.jsonl')
MIN_AMOUNT_CENTS = 1


def append_machine_ledger(row):
    MACHINE_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with MACHINE_LEDGER.open('a') as f:
        f.write(json.dumps(row) + '\n')


def intent_consumed(payment_intent_id: str) -> bool:
    if not MACHINE_LEDGER.exists():
        return False
    for line in MACHINE_LEDGER.read_text(errors='ignore').splitlines():
        try:
            row = json.loads(line)
        except Exception:
            continue
        if row.get('payment_intent_id') == payment_intent_id and row.get('status') == 'CONSUMED':
            return True
    return False


def verify_payment_intent(payment_intent_id: str):
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY', '')
    if not stripe.api_key:
        return {'ok': False, 'error': 'missing_stripe_secret'}
    if intent_consumed(payment_intent_id):
        return {'ok': False, 'error': 'intent_already_consumed'}
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    except Exception as e:
        return {'ok': False, 'error': 'stripe_retrieve_failed', 'detail': str(e)}
    amount = int(intent.get('amount', 0) or 0)
    currency = str(intent.get('currency', '') or '').lower()
    status = intent.get('status', '')
    if status != 'succeeded':
        return {'ok': False, 'error': 'intent_not_succeeded', 'status': status, 'amount': amount, 'currency': currency}
    if amount < MIN_AMOUNT_CENTS:
        return {'ok': False, 'error': 'amount_below_minimum', 'status': status, 'amount': amount, 'currency': currency}
    append_machine_ledger({
        'payment_intent_id': payment_intent_id,
        'status': 'CONSUMED',
        'amount': amount,
        'currency': currency,
    })
    return {'ok': True, 'status': status, 'amount': amount, 'currency': currency}
