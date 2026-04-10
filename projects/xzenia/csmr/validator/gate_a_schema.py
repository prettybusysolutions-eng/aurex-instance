#!/usr/bin/env python3
import json
import sys
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
SCHEMA_PATH = WORKSPACE / 'projects/xzenia/csmr/schemas/modification-proposal.schema.json'
CONSTITUTION_PATH = WORKSPACE / 'projects/xzenia/csmr/CONSTITUTION.md'
FORBIDDEN = {
    'model_endpoint', 'gateway_url', 'api_keys', 'memory_backend',
    'botToken', 'gateway.auth', 'credentials', 'memory_backend_url'
}
ALLOWED_CLASSES = {
    'soul_md_patch', 'routing_change', 'threshold_delta', 'fallback_order_change', 'prompt_guidance_change'
}


def validate(proposal):
    errors = []
    for field in ('proposal_id', 'mutation_class', 'target', 'change'):
        if field not in proposal:
            errors.append(f'missing:{field}')
    mutation_class = proposal.get('mutation_class')
    if mutation_class and mutation_class not in ALLOWED_CLASSES:
        errors.append(f'invalid_mutation_class:{mutation_class}')
    blob = json.dumps(proposal)
    for forbidden in FORBIDDEN:
        if forbidden in blob:
            errors.append(f'forbidden_surface:{forbidden}')
    if mutation_class == 'threshold_delta':
        delta = proposal.get('change', {}).get('delta')
        if isinstance(delta, (int, float)) and abs(delta) > 0.15:
            errors.append('threshold_delta_out_of_range')
    return errors


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: gate_a_schema.py <proposal.json>', file=sys.stderr)
        raise SystemExit(2)
    proposal = json.loads(Path(sys.argv[1]).read_text())
    errors = validate(proposal)
    if errors:
        print(json.dumps({'ok': False, 'errors': errors, 'constitution': str(CONSTITUTION_PATH)}, indent=2))
        raise SystemExit(1)
    print(json.dumps({'ok': True, 'constitution': str(CONSTITUTION_PATH), 'schema': str(SCHEMA_PATH)}, indent=2))
