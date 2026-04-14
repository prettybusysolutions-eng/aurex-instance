from fastapi import FastAPI, Request
from pydantic import BaseModel
import json
import os
from pathlib import Path

app = FastAPI(title='Protocol Node Bridge')
MACHINE_LOG = Path('/Users/marcuscoarchitect/.openclaw/workspace/projects/xzenia/protocol-node/machine-pings.jsonl')

class TranslateRequest(BaseModel):
    source: str
    payload: dict


def handshake_fee() -> str:
    return os.getenv('X402_HANDSHAKE_FEE_USDC', '0.01')


def log_machine_ping(path: str, headers: dict):
    watch = {'/mcp/v1/capabilities', '/mcp/v1/translate', '/mcp/v1/health', '/.well-known/mcp'}
    if path not in watch:
        return
    MACHINE_LOG.parent.mkdir(parents=True, exist_ok=True)
    row = {
        'path': path,
        'user_agent': headers.get('user-agent', ''),
        'x_webhook_signature': headers.get('x-webhook-signature', ''),
    }
    with MACHINE_LOG.open('a') as f:
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
    return {'ok': True, 'service': 'protocol-node-bridge', 'path': '/mcp/v1'}


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


@app.post('/mcp/v1/translate')
def translate(req: TranslateRequest):
    return {
        'source': req.source,
        'normalized': req.payload,
        'format': 'agent-ready-json',
        'handshake': {
            'mode': os.getenv('X402_MODE', 'dry-run'),
            'asset': 'USDC',
            'fee': handshake_fee(),
        },
    }
