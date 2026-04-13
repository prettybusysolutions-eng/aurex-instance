# Private Billing Listener

Private local listener for Stripe webhook events.

## Secret injection
Create `private/.env` from `.env.example` and fill in:
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `BILLING_LISTENER_PORT`

Do not commit `private/.env`.

## Run
```bash
export $(grep -v '^#' private/.env | xargs)
python3 private/billing_listener.py
```

## Mock payment test
In another terminal:
```bash
python3 - <<'PY'
import json, hmac, hashlib, os, urllib.request
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
