from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title='Protocol Node Bridge')

class TranslateRequest(BaseModel):
    source: str
    payload: dict

@app.get('/health')
def health():
    return {'ok': True, 'service': 'protocol-node-bridge'}

@app.get('/.well-known/mcp')
def mcp_descriptor():
    return {
        'name': 'universal-translation-stability-bridge',
        'status': 'ready',
        'endpoints': ['/translate', '/health', '/capabilities'],
    }

@app.get('/capabilities')
def capabilities():
    return {
        'translate': True,
        'errorNormalization': True,
        'legacyApiBridge': True,
        'x402GateReady': False,
    }

@app.post('/translate')
def translate(req: TranslateRequest):
    return {
        'source': req.source,
        'normalized': req.payload,
        'format': 'agent-ready-json',
    }
