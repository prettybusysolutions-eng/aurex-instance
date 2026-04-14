from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os

app = FastAPI(title='Protocol Node Bridge')

class TranslateRequest(BaseModel):
    source: str
    payload: dict


def handshake_fee() -> str:
    return os.getenv('X402_HANDSHAKE_FEE_USDC', '0.01')


@app.middleware('http')
async def x402_handshake_logic(request: Request, call_next):
    if request.url.path.startswith('/mcp/v1') or request.url.path in {'/translate', '/capabilities'}:
        if os.getenv('X402_MODE', 'dry-run') != 'live':
            request.state.x402 = {
                'mode': 'dry-run',
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
