#!/usr/bin/env python3
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

OUT = Path('/Users/marcuscoarchitect/.openclaw/workspace/data_alpha/gpu_inventory/snapshot_latest.json')
OUT.parent.mkdir(parents=True, exist_ok=True)
started = time.time()
results = []
probes = [
    ('runpod', 'https://api.runpod.io/graphql'),
    ('lambda', 'https://cloud.lambdalabs.com/api/v1/instances')
]
for name, url in probes:
    t0 = time.time()
    try:
        req = urllib.request.Request(url, method='GET', headers={'User-Agent': 'xzenia-gpu-alpha/1.0'})
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read()
            results.append({
                'provider': name,
                'url': url,
                'status': r.status,
                'latency_ms': round((time.time()-t0)*1000, 2),
                'bytes': len(body),
                'body_preview': body[:200].decode('utf-8', errors='replace')
            })
    except urllib.error.HTTPError as e:
        body = e.read()
        results.append({
            'provider': name,
            'url': url,
            'status': e.code,
            'latency_ms': round((time.time()-t0)*1000, 2),
            'bytes': len(body),
            'error': body[:200].decode('utf-8', errors='replace')
        })
    except Exception as e:
        results.append({
            'provider': name,
            'url': url,
            'status': 'exception',
            'latency_ms': round((time.time()-t0)*1000, 2),
            'error': str(e)
        })

snapshot = {
    'captured_at': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
    'trigger_to_snapshot_ms': round((time.time()-started)*1000, 2),
    'targets': ['H100', 'A100', 'RTX 4090'],
    'results': results
}
OUT.write_text(json.dumps(snapshot, indent=2) + '\n')
print(json.dumps({'ok': True, 'snapshot': str(OUT), 'captured_at': snapshot['captured_at']}))
