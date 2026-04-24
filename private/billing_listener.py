#!/usr/bin/env python3
import hmac
import hashlib
import json
import mimetypes
import os
import secrets
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import unquote

LEDGER = Path('/Users/marcuscoarchitect/.openclaw/workspace/private/billing-ledger.jsonl')
ASSET_DIR = Path('/Users/marcuscoarchitect/.openclaw/workspace/private/assets')
TOKEN_TTL_SECONDS = 24 * 60 * 60
LEDGER_LOCK = threading.Lock()
PRODUCT_ASSETS = {
    'revops_kit_core': ASSET_DIR / 'Sovereign_RevOps_Kit.zip',
    'privacy_migration_kit': ASSET_DIR / 'Privacy_Migration_Kit.zip',
    'home_lab_master_kit': ASSET_DIR / 'Home_Lab_Master_Kit.zip',
    'review_bundle': ASSET_DIR / 'review_bundle.zip',
    'sovereign_diagnostic_engine': ASSET_DIR / 'sovereign-diagnostic-engine-kit.zip',
}


def verify_signature(raw_body, signature, secret):
    if not signature or not secret:
        return False
    expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def _read_rows_unlocked():
    if not LEDGER.exists():
        return []
    rows = []
    for line in LEDGER.read_text(errors='ignore').splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def append_ledger(row):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER_LOCK:
        with LEDGER.open('a') as f:
            f.write(json.dumps(row) + '\n')


def seen_event(event_id):
    with LEDGER_LOCK:
        for row in _read_rows_unlocked():
            if row.get('event_id') == event_id:
                return True
    return False


def get_token_row(token):
    with LEDGER_LOCK:
        rows = _read_rows_unlocked()
    for row in reversed(rows):
        if row.get('kind') == 'download_token' and row.get('token') == token:
            return row
    return None


def mark_token_consumed(token):
    row = get_token_row(token)
    if not row or row.get('status') != 'active':
        return False
    append_ledger({
        'kind': 'download_token_consumed',
        'token': token,
        'consumed_at': int(time.time()),
        'event_id': row.get('event_id'),
        'product_key': row.get('product_key'),
    })
    return True


def token_consumed(token):
    with LEDGER_LOCK:
        rows = _read_rows_unlocked()
    for row in reversed(rows):
        if row.get('token') != token:
            continue
        if row.get('kind') == 'download_token_consumed':
            return True
        if row.get('kind') == 'download_token':
            return False
    return False


def mint_download_token():
    return secrets.token_urlsafe(32)


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if not self.path.startswith('/download/'):
            self.send_response(404)
            self.end_headers()
            return

        token = unquote(self.path[len('/download/'):]).strip()
        if not token:
            self._send_json(400, {'ok': False, 'error': 'missing_token'})
            return

        row = get_token_row(token)
        if not row:
            self._send_json(404, {'ok': False, 'error': 'token_not_found'})
            return
        if row.get('status') != 'active':
            self._send_json(403, {'ok': False, 'error': 'token_inactive'})
            return
        if int(time.time()) > int(row.get('expires_at', 0)):
            self._send_json(403, {'ok': False, 'error': 'token_expired'})
            return
        if token_consumed(token):
            self._send_json(403, {'ok': False, 'error': 'token_consumed'})
            return

        asset_path = Path(row.get('asset_path', ''))
        if not asset_path.exists():
            self._send_json(410, {'ok': False, 'error': 'asset_missing'})
            return

        data = asset_path.read_bytes()
        mime = mimetypes.guess_type(asset_path.name)[0] or 'application/octet-stream'
        self.send_response(200)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Content-Disposition', f'attachment; filename="{asset_path.name}"')
        self.end_headers()
        self.wfile.write(data)
        mark_token_consumed(token)

    def do_POST(self):
        if self.path != '/stripe/webhook':
            self.send_response(404)
            self.end_headers()
            return

        raw = self.rfile.read(int(self.headers.get('Content-Length', '0')))
        sig = self.headers.get('X-Webhook-Signature', '')
        secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')
        if not verify_signature(raw, sig, secret):
            self._send_json(400, {'ok': False, 'error': 'invalid_signature'})
            return

        event = json.loads(raw.decode('utf-8'))
        event_id = event.get('id')
        if seen_event(event_id):
            self._send_json(200, {'ok': True, 'duplicate': True})
            return

        obj = event.get('data', {}).get('object', {})
        amount = obj.get('amount_total', 0)
        paid = obj.get('payment_status') == 'paid'
        product = obj.get('metadata', {}).get('product_key', '')
        asset_path = PRODUCT_ASSETS.get(product)

        debug = str(event_id).startswith('evt_test_') or str(obj.get('metadata', {}).get('debug', '')).lower() in {'1', 'true', 'yes', 'debug'}
        token = None
        expires_at = None
        download_url = None
        granted = False

        if paid and amount >= 200 and asset_path and asset_path.exists():
            token = mint_download_token()
            expires_at = int(time.time()) + TOKEN_TTL_SECONDS
            download_url = f"http://127.0.0.1:{int(os.getenv('BILLING_LISTENER_PORT', '8787'))}/download/{token}"
            granted = True

        event_row = {
            'kind': 'billing_event',
            'event_id': event_id,
            'debug': debug,
            'paid': paid,
            'amount_total': amount,
            'product_key': product,
            'granted': granted,
            'asset_path': str(asset_path) if asset_path else None,
        }
        append_ledger(event_row)

        if granted:
            append_ledger({
                'kind': 'download_token',
                'event_id': event_id,
                'token': token,
                'product_key': product,
                'asset_path': str(asset_path),
                'status': 'active',
                'issued_at': int(time.time()),
                'expires_at': expires_at,
                'single_use': True,
            })

        self._send_json(200, {
            'ok': True,
            'granted': granted,
            'token': token,
            'expires_at': expires_at,
            'download_url': download_url,
        })


if __name__ == '__main__':
    port = int(os.getenv('BILLING_LISTENER_PORT', '8787'))
    server = HTTPServer(('127.0.0.1', port), Handler)
    print(f'billing listener running on http://127.0.0.1:{port}/stripe/webhook')
    server.serve_forever()
