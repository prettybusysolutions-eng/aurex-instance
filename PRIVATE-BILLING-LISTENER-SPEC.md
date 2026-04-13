# Private Billing Listener Spec

Last updated: 2026-04-13 19:34 EDT
Status: READY

## Discovery result
- no workspace `.env` file found
- no workspace `secrets/` folder found
- `STRIPE_SECRET_KEY` not currently defined in those workspace paths
- `STRIPE_WEBHOOK_SECRET` not currently defined in those workspace paths
- `.gitignore` already ignores `.env` and `.env.*`

## Injection path
Recommended private path:
- `private/.env` (local only, never committed)

## Exact test command
```bash
export $(grep -v '^#' private/.env | xargs)
python3 private/billing_listener.py
```

Then in a second terminal:
```bash
python3 - <<'PY'
import json, hmac, hashlib, urllib.request
secret='whsec_replace_me'
body=json.dumps({
  'id':'evt_test_1',
  'data':{'object':{'payment_status':'paid','amount_total':500,'metadata':{'product_key':'runtime_doctor_pro'}}}
}).encode()
sig=hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
req=urllib.request.Request('http://127.0.0.1:8787/stripe/webhook', data=body, headers={'Content-Type':'application/json','X-Webhook-Signature':sig})
print(urllib.request.urlopen(req).read().decode())
PY
```

## Expected result
- listener accepts the event
- ledger row is written to `private/billing-ledger.jsonl`
- duplicate event ids are ignored on retry
