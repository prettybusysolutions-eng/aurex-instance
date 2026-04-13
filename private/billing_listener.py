#!/usr/bin/env python3
import hmac
import hashlib
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

LEDGER = Path('/Users/marcuscoarchitect/.openclaw/workspace/private/billing-ledger.jsonl')
DOWNLOADS = {
    'runtime_doctor_pro': 'https://example.com/private/runtime-doctor-pro',
    'residue_classifier_pro': 'https://example.com/private/residue-classifier-pro',
    'utilities_pro_bundle': 'https://example.com/private/utilities-pro-bundle',
}


def append_ledger(row):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open('a') as f:
        f.write(json.dumps(row) + '\n')


def seen_event(event_id):
    if not LEDGER.exists():
        return False
    for line in LEDGER.read_text(errors='ignore').splitlines():
        try:
            row = json.loads(line)
        except Exception:
            continue
        if row.get('event_id') == event_id:
            return True
    return False


def verify_signature(raw_body, signature, secret):
    if not signature or not secret:
        return False
    expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != '/stripe/webhook':
            self.send_response(404)
            self.end_headers()
            return

        raw = self.rfile.read(int(self.headers.get('Content-Length', '0')))
        sig = self.headers.get('X-Webhook-Signature', '')
        secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')
        if not verify_signature(raw, sig, secret):
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'invalid signature')
            return

        event = json.loads(raw.decode('utf-8'))
        event_id = event.get('id')
        if seen_event(event_id):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'duplicate ignored')
            return

        obj = event.get('data', {}).get('object', {})
        amount = obj.get('amount_total', 0)
        paid = obj.get('payment_status') == 'paid'
        product = obj.get('metadata', {}).get('product_key', '')
        grant_url = DOWNLOADS.get(product)

        row = {
            'event_id': event_id,
            'paid': paid,
            'amount_total': amount,
            'product_key': product,
            'grant_url': grant_url if paid and amount >= 200 else None,
        }
        append_ledger(row)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({'ok': True, 'granted': row['grant_url'] is not None}).encode())


if __name__ == '__main__':
    port = int(os.getenv('BILLING_LISTENER_PORT', '8787'))
    server = HTTPServer(('127.0.0.1', port), Handler)
    print(f'billing listener running on http://127.0.0.1:{port}/stripe/webhook')
    server.serve_forever()
