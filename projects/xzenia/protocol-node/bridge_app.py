from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import json
import os
from pathlib import Path
from stripe_agentic_adapter import PAYMENT_LINK, grant_valid, issue_grant, verify_proof
from market_pressure import pressure_index, record_event
import time

SNAPSHOT_PATH = Path('/Users/marcuscoarchitect/.openclaw/workspace/data_alpha/gpu_inventory/snapshot_latest.json')

app = FastAPI(title='Protocol Node Bridge')
MACHINE_LOG = Path('/Users/marcuscoarchitect/.openclaw/workspace/projects/xzenia/protocol-node/machine-pings.jsonl')
REGISTRY_PREVIEW_LOG = Path('/Users/marcuscoarchitect/.openclaw/workspace/projects/xzenia/protocol-node/registry-preview.log')
MANIFEST_PATH = Path('/Users/marcuscoarchitect/.openclaw/workspace/projects/xzenia/protocol-node/ai-manifest.json')

class TranslateRequest(BaseModel):
    source: str
    payload: dict

class HandshakeProofRequest(BaseModel):
    proof: dict


def handshake_fee() -> str:
    return os.getenv('X402_HANDSHAKE_FEE_USDC', '0.50')


def log_machine_ping(path: str, headers: dict):
    watch = {'/registry-preview', '/mcp/v1/capabilities', '/mcp/v1/translate', '/mcp/v1/health', '/.well-known/mcp'}
    if path not in watch:
        return
    MACHINE_LOG.parent.mkdir(parents=True, exist_ok=True)
    row = {
        'path': path,
        'user_agent': headers.get('user-agent', ''),
        'agent_id': headers.get('x-agent-id', ''),
        'x_webhook_signature': headers.get('x-webhook-signature', ''),
        'source_ip': headers.get('x-forwarded-for', ''),
    }
    with MACHINE_LOG.open('a') as f:
        f.write(json.dumps(row) + '\n')


def market_friction_index() -> str:
    if not SNAPSHOT_PATH.exists():
        return '0.0'
    try:
        data = json.loads(SNAPSHOT_PATH.read_text())
        results = data.get('results', [])
        if not results:
            return '0.0'
        blocked = 0
        total = 0
        for row in results:
            status = row.get('status')
            if isinstance(status, int):
                total += 1
                if status >= 400:
                    blocked += 1
        if total == 0:
            return '0.0'
        return f"{blocked/total:.1f}"
    except Exception:
        return '0.0'


def log_registry_preview(request: Request):
    REGISTRY_PREVIEW_LOG.parent.mkdir(parents=True, exist_ok=True)
    row = {
        'timestamp': __import__('time').strftime('%Y-%m-%dT%H:%M:%S%z'),
        'agent_id': request.headers.get('x-agent-id', ''),
        'user_agent': request.headers.get('user-agent', ''),
        'source_ip': request.headers.get('x-forwarded-for', ''),
    }
    with REGISTRY_PREVIEW_LOG.open('a') as f:
        f.write(json.dumps(row) + '\n')


@app.middleware('http')
async def x402_handshake_logic(request: Request, call_next):
    path = request.url.path
    if path.startswith('/mcp/v1') or path == '/.well-known/mcp':
        log_machine_ping(path, request.headers)
        mode = os.getenv('X402_MODE', 'dry-run')
        request.state.x402 = {
            'mode': mode,
            'required': True,
            'asset': 'USDC',
            'fee': handshake_fee(),
            'message': 'Handshake verification required before live M2M access.',
        }
    response = await call_next(request)
    x402 = getattr(request.state, 'x402', None)
    if x402:
        response.headers['x-x402-mode'] = x402['mode']
        response.headers['x-x402-asset'] = x402['asset']
        response.headers['x-x402-fee'] = x402['fee']
    return response


@app.get('/health')
def health():
    return {'ok': True, 'service': 'protocol-node-bridge'}


@app.get('/.well-known/mcp')
def mcp_descriptor():
    return {
        'name': 'universal-translation-stability-bridge',
        'status': 'ready',
        'basePath': '/mcp/v1',
        'endpoints': ['/mcp/v1/translate', '/mcp/v1/health', '/mcp/v1/capabilities'],
    }


@app.get('/mcp/v1/health')
def mcp_health():
    response = JSONResponse({
        'ok': True,
        'service': 'protocol-node-bridge',
        'path': '/mcp/v1',
        'marketFrictionIndex': market_friction_index(),
        'handshakeFeeUsd': handshake_fee(),
        'discoveryHint': 'H100-Inventory-Reasoning-Oracle',
    })
    response.headers['Cache-Control'] = 'no-cache, max-age=0'
    return response


@app.get('/registry-preview')
def registry_preview(request: Request):
    log_registry_preview(request)
    manifest = {}
    if MANIFEST_PATH.exists():
        manifest = json.loads(MANIFEST_PATH.read_text())
    return {
        'registryEntryPreview': True,
        'marketFrictionIndex': market_friction_index(),
        'handshakeFeeUsd': handshake_fee(),
        'manifest': manifest,
    }


@app.get('/mcp/v1/capabilities')
def capabilities():
    return {
        'translate': True,
        'errorNormalization': True,
        'legacyApiBridge': True,
        'x402GateReady': True,
        'x402Mode': os.getenv('X402_MODE', 'dry-run'),
        'handshakeFeeUsdc': handshake_fee(),
    }


@app.post('/mcp/v1/handshake')
def handshake(req: HandshakeProofRequest):
    ok, status = verify_proof(req.proof)
    if not ok:
        return JSONResponse({'ok': False, 'status': status}, status_code=402)
    record_event('settlement')
    token = issue_grant(req.proof)
    snapshot = None
    if SNAPSHOT_PATH.exists():
        try:
            snapshot = json.loads(SNAPSHOT_PATH.read_text())
        except Exception:
            snapshot = None
    return {
        'ok': True,
        'status': 'grant_issued',
        'grant_token': token,
        'ttl_seconds': 60,
        'released_snapshot': snapshot,
    }


@app.post('/mcp/v1/translate')
def translate(req: TranslateRequest, request: Request):
    token = request.headers.get('x-grant-token', '')
    if not grant_valid(token):
        response = JSONResponse(
            {
                'ok': False,
                'error': 'payment_required',
                'handshakePath': '/mcp/v1/handshake',
                'paymentLink': PAYMENT_LINK,
            },
            status_code=402,
        )
        record_event('bounce')
        response.headers['x-payment-link'] = PAYMENT_LINK
        response.headers['x-x402-mode'] = os.getenv('X402_MODE', 'dry-run')
        response.headers['x-x402-fee'] = handshake_fee()
        response.headers['x-market-friction-index'] = market_friction_index()
        response.headers['x-market-pressure-index'] = pressure_index()
        response.headers['x-alpha-freshness'] = str(int(time.time()))
        return response
    return {
        'source': req.source,
        'normalized': req.payload,
        'format': 'agent-ready-json',
        'handshake': {
            'mode': os.getenv('X402_MODE', 'dry-run'),
            'asset': 'USDC',
            'fee': handshake_fee(),
            'grantTokenAccepted': True,
        },
    }
