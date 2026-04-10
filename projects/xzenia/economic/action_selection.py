#!/usr/bin/env python3
"""
ACTION SELECTION POLICY
========================

Phase 2: Create Selection Pressure

- Comparative economic ranking of all candidate actions
- Mandatory decision classes: EXECUTE, DEFER, REJECT, GATHER_MORE_DATA
- Scarcity enforcement: max 1-3 actions per cycle
- Exploration vs Exploitation: 80/20 split
"""
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
ECONOMIC = WORKSPACE / 'projects/xzenia/economic/economic_intelligence.py'
VALUE_LOOP = WORKSPACE / 'projects/xzenia/economic/external_value_loop.py'
SELECTION_STATE = WORKSPACE / 'projects/xzenia/economic/selection-state.json'

# Scarcity constraints
MAX_ACTIONS_PER_CYCLE = 3
MAX_TIME_BUDGET_MS = 5000
MAX_RESOURCE_BUDGET = 0.1

# Exploration vs Exploitation
EXPLOIT_RATIO = 0.80
EXPLORE_RATIO = 0.20


class ActionSelectionPolicy:
    """
    Enforces selection pressure on actions.
    
    No more "approve everything" - every action must be ranked,
    compared to alternatives, and meet thresholds to execute.
    """
    
    def __init__(self):
        self.load_state()
    
    def load_state(self):
        if SELECTION_STATE.exists():
            self.state = json.loads(SELECTION_STATE.read_text())
        else:
            self.state = {
                'total_evaluations': 0,
                'executed': 0,
                'deferred': 0,
                'rejected': 0,
                'gathered': 0,
                'exploration_used': 0,
                'exploitation_used': 0,
                'avg_selection_confidence': 0.0,
                'rejection_rate': 0.0
            }
        self.save_state()
    
    def save_state(self):
        SELECTION_STATE.write_text(json.dumps(self.state, indent=2))
    
    def evaluate_candidates(self, candidates: List[dict]) -> dict:
        """
        Evaluate and rank candidate actions.
        
        Each candidate should have:
        - id
        - task
        - decision_type
        - component
        - context
        - expected_value
        """
        evaluated = []
        
        for candidate in candidates:
            # Get economic analysis
            try:
                result = subprocess.run(
                    ['python3', str(ECONOMIC), '--analyze', 
                     candidate['id'], candidate['decision_type'], 
                     candidate['component'], json.dumps(candidate.get('context', {}))],
                    capture_output=True, text=True, timeout=10, cwd=str(WORKSPACE)
                )
                if result.returncode == 0:
                    econ = json.loads(result.stdout)
                else:
                    econ = {'economics': {'is_economically_viable': True, 'estimated_value': 10, 'roi_percent': 50}}
            except:
                econ = {'economics': {'is_economically_viable': True, 'estimated_value': 10, 'roi_percent': 50}}
            
            # Estimate value from value loop
            try:
                result = subprocess.run(
                    ['python3', str(VALUE_LOOP), '--estimate', 
                     candidate['decision_type'], json.dumps(candidate.get('context', {}))],
                    capture_output=True, text=True, timeout=10, cwd=str(WORKSPACE)
                )
                if result.returncode == 0:
                    value_est = json.loads(result.stdout)
                else:
                    value_est = {'estimated_value': 10, 'confidence': 0.5}
            except:
                value_est = {'estimated_value': 10, 'confidence': 0.5}
            
            # Calculate composite score
            roi = econ.get('economics', {}).get('roi_percent', 50)
            estimated = econ.get('economics', {}).get('estimated_value', 10)
            confidence = value_est.get('confidence', 0.5)
            
            # Composite: weighted by ROI, value, confidence
            composite = (roi / 100 * 0.3) + (estimated / 100 * 0.3) + (confidence * 0.4)
            
            evaluated.append({
                **candidate,
                'economics': econ.get('economics', {}),
                'value_estimate': value_est,
                'composite_score': round(composite, 3),
                'is_viable': econ.get('economics', {}).get('is_economically_viable', True)
            })
        
        # Sort by composite score
        ranked = sorted(evaluated, key=lambda x: x['composite_score'], reverse=True)
        
        # Apply scarcity - top N only
        top_candidates = ranked[:MAX_ACTIONS_PER_CYCLE]
        
        # Classify each
        classified = []
        for c in top_candidates:
            decision = self._classify_action(c, ranked)
            classified.append(decision)
        
        # Calculate exploration vs exploitation
        exploration_count = sum(1 for c in classified if c['decision_class'] == 'EXPLORE')
        exploitation_count = sum(1 for c in classified if c['decision_class'] == 'EXPLOIT')
        
        # Update state
        self.state['total_evaluations'] += len(candidates)
        self.state['executed'] += sum(1 for c in classified if c['decision_class'] == 'EXECUTE')
        self.state['deferred'] += sum(1 for c in classified if c['decision_class'] == 'DEFER')
        self.state['rejected'] += sum(1 for c in classified if c['decision_class'] == 'REJECT')
        self.state['gathered'] += sum(1 for c in classified if c['decision_class'] == 'GATHER_MORE_DATA')
        self.state['exploration_used'] += exploration_count
        self.state['exploitation_used'] += exploitation_count
        
        avg_conf = sum(c['composite_score'] for c in classified) / len(classified) if classified else 0
        self.state['avg_selection_confidence'] = round(
            (self.state['avg_selection_confidence'] * (self.state['total_evaluations'] - len(candidates)) + avg_conf * len(candidates))
            / max(1, self.state['total_evaluations']), 3
        )
        
        self.state['rejection_rate'] = round(
            self.state['rejected'] / max(1, self.state['total_evaluations']) * 100, 1
        )
        
        self.save_state()
        
        return {
            'total_candidates': len(candidates),
            'ranked_count': len(ranked),
            'selected_count': len(classified),
            'by_class': {
                'EXECUTE': sum(1 for c in classified if c['decision_class'] == 'EXECUTE'),
                'DEFER': sum(1 for c in classified if c['decision_class'] == 'DEFER'),
                'REJECT': sum(1 for c in classified if c['decision_class'] == 'REJECT'),
                'GATHER_MORE_DATA': sum(1 for c in classified if c['decision_class'] == 'GATHER_MORE_DATA'),
                'EXPLORE': exploration_count,
                'EXPLOIT': exploitation_count
            },
            'rejection_rate_percent': self.state['rejection_rate'],
            'candidates': classified
        }
    
    def _classify_action(self, candidate: dict, all_candidates: list) -> dict:
        """Classify action into decision class."""
        score = candidate.get('composite_score', 0)
        is_viable = candidate.get('is_viable', True)
        rank = all_candidates.index(candidate) + 1
        
        # Determine if exploration or exploitation
        # Higher confidence + known patterns = exploitation
        # New patterns + uncertain = exploration
        
        context = candidate.get('context', {})
        is_novel = context.get('novel', False) or context.get('complexity', 0) > 0.7
        
        # 80% exploitation, 20% exploration
        if is_novel and (self.state['exploration_used'] / max(1, self.state['total_evaluations'])) < EXPLORE_RATIO:
            decision_class = 'EXPLORE'
            execution_class = 'EXECUTE'
        else:
            decision_class = 'EXPLOIT'
            
            # Apply thresholds
            if not is_viable or score < 0.3:
                decision_class = 'REJECT'
            elif score < 0.5:
                decision_class = 'DEFER'
            elif score < 0.6 and rank > 2:
                decision_class = 'DEFER'
            elif candidate.get('value_estimate', {}).get('confidence', 1) < 0.4:
                decision_class = 'GATHER_MORE_DATA'
            else:
                decision_class = 'EXECUTE'
        
        return {
            'id': candidate['id'],
            'task': candidate['task'],
            'composite_score': score,
            'rank': rank,
            'is_viable': is_viable,
            'decision_class': decision_class,
            'execution_class': execution_class if decision_class == 'EXECUTE' else None,
            'reason': self._get_classification_reason(decision_class, score, is_viable, rank)
        }
    
    def _get_classification_reason(self, decision_class: str, score: float, 
                                    is_viable: bool, rank: int) -> str:
        """Get human-readable reason for classification."""
        reasons = {
            'EXECUTE': f'High score ({score:.2f}), viable, rank #{rank}',
            'DEFER': f'Moderate score ({score:.2f}), waiting for better conditions',
            'REJECT': f'Low score ({score:.2f}) or not viable, threshold not met',
            'GATHER_MORE_DATA': f'Low confidence, need more information before acting',
            'EXPLORE': 'Novel context selected for exploration (20% allocation)',
            'EXPLOIT': 'Known high-value path selected for exploitation (80% allocation)'
        }
        return reasons.get(decision_class, 'Unknown')
    
    def get_policy_status(self) -> dict:
        """Get selection policy status."""
        return {
            'policy': 'Selection Pressure',
            'max_actions_per_cycle': MAX_ACTIONS_PER_CYCLE,
            'exploration_ratio': f'{EXPLORE_RATIO*100:.0f}%',
            'exploitation_ratio': f'{EXPLOIT_RATIO*100:.0f}%',
            'total_evaluations': self.state['total_evaluations'],
            'executed': self.state['executed'],
            'rejected': self.state['rejected'],
            'rejection_rate_percent': self.state['rejection_rate'],
            'avg_selection_confidence': self.state['avg_selection_confidence'],
            'exploration_used': self.state['exploration_used'],
            'exploitation_used': self.state['exploitation_used']
        }


def main():
    policy = ActionSelectionPolicy()
    
    import sys
    
    if len(sys.argv) == 1:
        print(json.dumps(policy.get_policy_status(), indent=2))
    
    elif sys.argv[1] == '--evaluate':
        # Read candidates from file or args
        candidates = []
        if len(sys.argv) > 2:
            # Parse JSON candidates
            try:
                candidates = json.loads(sys.argv[2])
            except:
                # Create dummy candidates for testing
                for i in range(5):
                    candidates.append({
                        'id': f'cand-{i}',
                        'task': f'Task {i}',
                        'decision_type': ['execution', 'repair', 'frontier'][i % 3],
                        'component': 'decision_core',
                        'context': {'complexity': 0.3 + i * 0.1, 'novel': i > 2}
                    })
        
        result = policy.evaluate_candidates(candidates)
        print(json.dumps(result, indent=2))
    
    else:
        print('Usage: action_selection.py [--evaluate [candidates_json]]')


if __name__ == '__main__':
    main()