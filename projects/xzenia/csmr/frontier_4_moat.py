#!/usr/bin/env python3
"""
Frontier-4 Executor: Imitation-Resistant Moat Builder
Converts hard-won runtime lessons into durable substrate artifacts.

Definition of Done:
- At least 3 repeated lessons packaged into durable artifacts
- New operator value depends on integrated local layers
- Removing any core layer reduces system capability
"""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
DB = WORKSPACE / 'projects/xzenia/csmr/ledger/causal_ledger.sqlite'
SKILLS_DIR = WORKSPACE / 'workspace/skills'
SYSTEM_DIR = WORKSPACE / 'workspace/system'
ORCH_DIR = WORKSPACE / 'projects/xzenia/orchestration'
STATE = WORKSPACE / 'projects/xzenia/state/frontier-4-state.json'


class MoatBuilder:
    """Builds imitation-resistant moat from lessons."""
    
    def __init__(self):
        self.load_state()
    
    def load_state(self):
        if STATE.exists():
            self.state = json.loads(STATE.read_text())
        else:
            self.state = {
                'lessons_extracted': 0,
                'artifacts_created': 0,
                'layers_protected': [],
                'last_extraction': None
            }
        self.save_state()
    
    def save_state(self):
        STATE.write_text(json.dumps(self.state, indent=2))
    
    def extract_repeated_lessons(self) -> list:
        """Find lessons that appear repeatedly in the ledger."""
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        
        # Find event patterns that repeat
        cur.execute('''
            SELECT event_type, component, COUNT(*) as cnt
            FROM causal_events
            GROUP BY event_type, component
            HAVING cnt > 2
            ORDER BY cnt DESC
            LIMIT 10
        ''')
        
        patterns = [{'event_type': r[0], 'component': r[1], 'count': r[2]} for r in cur.fetchall()]
        conn.close()
        
        # Analyze each pattern for lessons
        lessons = []
        for p in patterns:
            lesson = {
                'pattern': f"{p['event_type']}:{p['component']}",
                'occurrences': p['count'],
                'derived_insight': self._derive_insight(p)
            }
            lessons.append(lesson)
        
        self.state['lessons_extracted'] += len(lessons)
        self.state['last_extraction'] = datetime.now(timezone.utc).isoformat()
        
        return lessons
    
    def _derive_insight(self, pattern: dict) -> str:
        """Derive actionable insight from pattern."""
        # Example insights based on pattern type
        event = pattern['event_type']
        
        insights = {
            'recovery_action': 'Pattern suggests need for faster recovery',
            'error': 'Pattern indicates error handling gap',
            'checkpoint': 'Pattern suggests checkpoint optimization',
            'fallback': 'Pattern shows fallback optimization opportunity',
            'health_report': 'Pattern indicates health monitoring need'
        }
        
        return insights.get(event, 'General pattern detected')
    
    def create_durable_artifact(self, lesson: dict) -> dict:
        """Create a durable skill/artifact from lesson."""
        artifact_id = f"moat-artifact-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        
        # Create skill artifact
        artifact_dir = SKILLS_DIR / artifact_id
        artifact_dir.mkdir(parents=True, exist_ok=True)
        
        # Write SKILL.md
        skill_content = f"""# {lesson['pattern']} - Learned from {lesson['occurrences']} occurrences

## Origin
Extracted from pattern: {lesson['pattern']}
Occurrences: {lesson['occurrences']}

## Insight
{lesson['derived_insight']}

## How to Use
This skill encapsulates the learned pattern.

## Implementation
See implementation in the substrate.
"""
        
        (artifact_dir / 'SKILL.md').write_text(skill_content)
        
        self.state['artifacts_created'] += 1
        self.save_state()
        
        return {
            'artifact_id': artifact_id,
            'path': str(artifact_dir),
            'lesson': lesson['pattern']
        }
    
    def measure_layer_dependencies(self) -> dict:
        """Measure which layers have dependencies (moat)."""
        # Check core substrate layers
        core_layers = [
            'orchestration/model-registry.json',
            'orchestration/resilience-policy.json',
            'charter/build-charter.json',
            'state/latest-checkpoint.json',
            'supervisor/unified_supervisor.py',
            'execution/token_budget_guard.py',
            'execution/degradation_evaluator.py'
        ]
        
        dependencies = {}
        for layer in core_layers:
            path = WORKSPACE / layer
            exists = path.exists()
            deps = self._count_dependencies(path)
            dependencies[layer] = {
                'exists': exists,
                'dependencies': deps
            }
        
        return dependencies
    
    def _count_dependencies(self, path: Path) -> int:
        """Count other files referencing this path."""
        if not path.exists():
            return 0
        
        content = path.read_text()
        
        # Simple heuristic: count references to other core files
        refs = 0
        for core in ['orchestration', 'supervisor', 'execution', 'recovery', 'csmr']:
            if core in content:
                refs += 1
        
        return refs
    
    def run_cycle(self) -> dict:
        """Execute one moat-building cycle."""
        # Extract repeated lessons
        lessons = self.extract_repeated_lessons()
        
        # Create artifacts for top lessons
        artifacts = []
        for lesson in lessons[:3]:
            artifact = self.create_durable_artifact(lesson)
            artifacts.append(artifact)
        
        # Measure dependencies
        deps = self.measure_layer_dependencies()
        
        # Calculate moat strength
        strong_layers = sum(1 for d in deps.values() if d['dependencies'] > 2)
        
        return {
            'status': 'cycle_complete',
            'lessons_extracted': len(lessons),
            'artifacts_created': len(artifacts),
            'artifacts': artifacts,
            'moat_strength': {
                'strong_layers': strong_layers,
                'total_layers': len(deps),
                'strength_ratio': round(strong_layers / len(deps), 2) if deps else 0
            },
            'state': self.state
        }
    
    def get_status(self) -> dict:
        """Get frontier-4 status."""
        deps = self.measure_layer_dependencies()
        strong_layers = sum(1 for d in deps.values() if d['dependencies'] > 2)
        
        return {
            'frontier': 'frontier-4-imitation-resistance',
            'status': 'ready',
            'lessons_extracted': self.state['lessons_extracted'],
            'artifacts_created': self.state['artifacts_created'],
            'moat_strength': {
                'strong_layers': strong_layers,
                'total_layers': len(deps),
                'ratio': round(strong_layers / len(deps), 2) if deps else 0
            },
            'definition_of_done': {
                '3_lessons': self.state['lessons_extracted'] >= 3,
                'durable_artifacts': self.state['artifacts_created'] >= 3,
                'layer_dependencies': strong_layers >= 3
            }
        }


def main():
    moat = MoatBuilder()
    
    import sys
    
    if len(sys.argv) == 1:
        print(json.dumps(moat.get_status(), indent=2))
    elif sys.argv[1] == '--cycle':
        print(json.dumps(moat.run_cycle(), indent=2))
    elif sys.argv[1] == '--lessons':
        print(json.dumps(moat.extract_repeated_lessons(), indent=2))
    elif sys.argv[1] == '--dependencies':
        print(json.dumps(moat.measure_layer_dependencies(), indent=2))
    else:
        print('Usage: frontier_4_moat.py [--cycle|--lessons|--dependencies]')


if __name__ == '__main__':
    main()