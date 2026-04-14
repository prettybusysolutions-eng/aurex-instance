from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import httpx
import os
from bridge_app import mcp_descriptor, mcp_health, capabilities, translate, TranslateRequest

app = FastAPI(title='Protocol Node Multiplexer')
BILLING_BASE = os.getenv('BILLING_BASE_URL', 'http://127.0.0.1:8787')


@app.get('/health')
def health():
    return {'ok': True, 'service': 'protocol-node-multiplexer'}


@app.api_route('/stripe/{path:path}', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
async def stripe_proxy(path: str, request: Request):
    target = f"{BILLING_BASE}/stripe/{path}"
    body = await request.body()
    headers = {k: v for k, v in request.headers.items() if k.lower() != 'host'}
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.request(request.method, target, content=body, headers=headers)
    return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))


@app.get('/.well-known/mcp')
def well_known_mcp():
    descriptor = mcp_descriptor()
    descriptor['semanticKeywords'] = [
        'runtime stability',
        'gateway drift',
        'm2m handshake',
        'OpenClaw failure fix',
        'automatic runtime repair',
        'legacy api translation',
    ]
    descriptor['routing'] = {
        'machinePath': '/mcp/v1',
        'billingPath': '/stripe/webhook',
    }
    return JSONResponse(descriptor)


@app.get('/mcp/v1/health')
def routed_mcp_health():
    return mcp_health()


@app.get('/mcp/v1/capabilities')
def routed_mcp_capabilities():
    return capabilities()


@app.post('/mcp/v1/translate')
def routed_mcp_translate(req: TranslateRequest, request: Request):
    return translate(req, request)
