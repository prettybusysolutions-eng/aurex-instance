#!/usr/bin/env python3
"""
REAL CONSEQUENCE FEEDBACK
==========================

Measures real-world impact of Xzenia's decisions.
Unlike internal metrics, this tracks:
- Did the decision actually work?
- What was the actual outcome?
- What can be learned for next time?

This creates a closed loop between decisions and reality.
"""
import json
import sqlite3
import subprocess
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
DB = WORKSPACE / 'projects/xzenia/csmr/ledger/causal_ledger.sqlite'
CONSEQUENCE_LOG = WORKSPACE / 'projects/xzenia/economic/consequence-log.json'
CONSEQUENCE_STATE = WORKSPACE / 'projects/xzenia/economic/consequence-state.json'

# Consequence types
CONSEQUENCE_TYPES = [
    'task_completion',
    'time_efficiency',
    'quality_output',
    'resource_savings',
    'error_prevention',
    'revenue_impact',
    'cost_avoidance',
    'user_satisfaction'
]


class RealConsequenceFeedback:
    """
    Real Consequence Feedback - measures actual impact.
    
    Key insight: Internal metrics (confidence, health scores) 
    don't always match external reality. This layer bridges that gap.
    
    It captures:
    - What was predicted
    - What actually happened
    - The delta (prediction error)
    - Learning for future
    """
    
    def __init__(self):
        self.load_state()
    
    def load_state(self):
        if CONSEQUENCE_STATE.exists():
            self.state = json.loads(CONSEQUENCE_STATE.read_text())
        else:
            self.state = {
                'total_consequences_captured': 0,
                'predictions_made': 0,
                'predictions_correct': 0,
                'prediction_error_total': 0.0,
                'by_type': {t: {'captured': 0, 'correct': 0, 'error': 0} for t in CONSEQUENCE_TYPES},
                'by_component': {},
                'corrections_learned': 0,
                'last_capture': None
            }
        self.save_state()
    
    def save_state(self):
        CONSEQUENCE_STATE.write_text(json.dumps(self.state, indent=2))
    
    def capture_prediction(self, prediction_id: str, decision_id: str, 
                          predicted_outcome: str, predicted_value: float,
                          component: str, context: dict) -> str:
        """Capture a prediction for later consequence capture."""
        # Store prediction
        predictions = self._load_predictions()
        
        predictions[prediction_id] = {
            'prediction_id': prediction_id,
            'decision_id': decision_id,
            'predicted_outcome': predicted_outcome,
            'predicted_value': predicted_value,
            'component': component,
            'context': context,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'captured': False
        }
        
        self._save_predictions(predictions)
        
        self.state['predictions_made'] += 1
        self.save_state()
        
        return prediction_id
    
    def capture_consequence(self, prediction_id: str, actual_outcome: str, 
                           actual_value: float, evidence: dict = None) -> dict:
        """Capture the actual consequence of a prediction."""
        predictions = self._load_predictions()
        
        if prediction_id not in predictions:
            return {'error': 'Prediction not found'}
        
        prediction = predictions[prediction_id]
        
        # Calculate prediction error
        predicted_value = prediction.get('predicted_value', 0)
        error = actual_value - predicted_value
        error_percent = abs(error) / max(abs(predicted_value), 0.01) * 100
        
        # Determine if prediction was "correct" (within reasonable margin)
        is_correct = error_percent < 25  # Within 25% is considered correct
        
        # Build consequence record
        consequence = {
            'prediction_id': prediction_id,
            'decision_id': prediction.get('decision_id'),
            'component': prediction.get('component'),
            'predicted': {
                'outcome': prediction.get('predicted_outcome'),
                'value': predicted_value
            },
            'actual': {
                'outcome': actual_outcome,
                'value': actual_value
            },
            'error': {
                'absolute': round(error, 2),
                'percent': round(error_percent, 1),
                'direction': 'over' if error > 0 else 'under'
            },
            'correct': is_correct,
            'evidence': evidence or {},
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Store consequence
        consequences = self._load_consequences()
        consequences.append(consequence)
        
        # Keep last 1000
        if len(consequences) > 1000:
            consequences = consequences[-1000:]
        
        self._save_consequences(consequences)
        
        # Update state
        self.state['total_consequences_captured'] += 1
        
        if is_correct:
            self.state['predictions_correct'] += 1
        
        self.state['prediction_error_total'] += abs(error)
        
        # Update by type
        component = prediction.get('component', 'unknown')
        if component not in self.state['by_component']:
            self.state['by_component'][component] = {'captured': 0, 'correct': 0}
        
        self.state['by_component'][component]['captured'] += 1
        if is_correct:
            self.state['by_component'][component]['correct'] += 1
        
        self.state['last_capture'] = datetime.now(timezone.utc).isoformat()
        
        # Mark prediction as captured
        prediction['captured'] = True
        self._save_predictions(predictions)
        
        self.save_state()
        
        # Generate correction if needed
        if not is_correct and error_percent > 50:
            self._learn_correction(consequence)
        
        return consequence
    
    def _learn_correction(self, consequence: dict):
        """Learn from large prediction errors."""
        self.state['corrections_learned'] += 1
        
        # Store correction
        corrections = []
        corr_file = WORKSPACE / 'projects/xzenia/economic/corrections.json'
        
        if corr_file.exists():
            try:
                corrections = json.loads(corr_file.read_text())
            except:
                corrections = []
        
        corrections.append({
            'consequence_id': consequence['prediction_id'],
            'component': consequence['component'],
            'predicted': consequence['predicted'],
            'actual': consequence['actual'],
            'error_percent': consequence['error']['percent'],
            'learned_at': datetime.now(timezone.utc).isoformat()
        })
        
        if len(corrections) > 100:
            corrections = corrections[-100:]
        
        corr_file.write_text(json.dumps(corrections, indent=2))
    
    def get_prediction_accuracy(self, component: str = None, 
                               time_window_hours: int = 24) -> dict:
        """Get prediction accuracy statistics."""
        consequences = self._load_consequences()
        
        # Filter by time
        cutoff = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
        
        recent = [
            c for c in consequences 
            if datetime.fromisoformat(c['timestamp'].replace('Z', '+00:00')) > cutoff
        ]
        
        if component:
            recent = [c for c in recent if c.get('component') == component]
        
        if not recent:
            return {'error': 'No recent consequences'}
        
        correct = sum(1 for c in recent if c.get('correct'))
        total = len(recent)
        
        accuracy = (correct / total * 100) if total > 0 else 0
        
        # Calculate average error
        errors = [abs(c['error']['absolute']) for c in recent]
        avg_error = sum(errors) / len(errors) if errors else 0
        
        return {
            'time_window_hours': time_window_hours,
            'component': component or 'all',
            'total_consequences': total,
            'accuracy_percent': round(accuracy, 1),
            'correct': correct,
            'incorrect': total - correct,
            'average_error': round(avg_error, 2),
            'errors': {
                'over_predictions': sum(1 for c in recent if c['error']['direction'] == 'over'),
                'under_predictions': sum(1 for c in recent if c['error']['direction'] == 'under')
            }
        }
    
    def get_corrections(self, limit: int = 10) -> list:
        """Get recent corrections learned."""
        corr_file = WORKSPACE / 'projects/xzenia/economic/corrections.json'
        
        if not corr_file.exists():
            return []
        
        try:
            corrections = json.loads(corr_file.read_text())
            return corrections[-limit:]
        except:
            return []
    
    def _load_predictions(self) -> dict:
        """Load predictions storage."""
        pred_file = WORKSPACE / 'projects/xzenia/economic/predictions.json'
        if pred_file.exists():
            try:
                return json.loads(pred_file.read_text())
            except:
                return {}
        return {}
    
    def _save_predictions(self, predictions: dict):
        """Save predictions."""
        (WORKSPACE / 'projects/xzenia/economic/predictions.json').write_text(json.dumps(predictions))
    
    def _load_consequences(self) -> list:
        """Load consequences storage."""
        if CONSEQUENCE_LOG.exists():
            try:
                return json.loads(CONSEQUENCE_LOG.read_text())
            except:
                return []
        return []
    
    def _save_consequences(self, consequences: list):
        """Save consequences."""
        CONSEQUENCE_LOG.write_text(json.dumps(consequences, indent=2))
    
    def get_status(self) -> dict:
        """Get consequence feedback status."""
        total = self.state['total_consequences_captured']
        correct = self.state['predictions_correct']
        
        return {
            'status': 'active',
            'total_consequences': total,
            'total_predictions': self.state['predictions_made'],
            'prediction_accuracy': round((correct / total * 100) if total > 0 else 0, 1),
            'average_error': round(
                self.state['prediction_error_total'] / max(1, total), 2
            ),
            'corrections_learned': self.state['corrections_learned'],
            'by_component': {
                c: {
                    'captured': d['captured'],
                    'accuracy': round((d['correct'] / d['captured'] * 100) if d['captured'] > 0 else 0, 1)
                }
                for c, d in self.state['by_component'].items()
            }
        }


def main():
    feedback = RealConsequenceFeedback()
    
    import sys
    
    if len(sys.argv) == 1:
        print(json.dumps(feedback.get_status(), indent=2))
    
    elif sys.argv[1] == '--predict' and len(sys.argv) > 4:
        pred_id = sys.argv[2]
        decision_id = sys.argv[3]
        outcome = sys.argv[4]
        value = float(sys.argv[5]) if len(sys.argv) > 5 else 10.0
        component = sys.argv[6] if len(sys.argv) > 6 else 'decision_core'
        context = json.loads(sys.argv[7]) if len(sys.argv) > 7 else {}
        
        result = feedback.capture_prediction(pred_id, decision_id, outcome, value, component, context)
        print(json.dumps({'predicted': True, 'prediction_id': result}))
    
    elif sys.argv[1] == '--capture' and len(sys.argv) > 3:
        pred_id = sys.argv[2]
        actual_outcome = sys.argv[3]
        actual_value = float(sys.argv[4]) if len(sys.argv) > 4 else 10.0
        evidence = json.loads(sys.argv[5]) if len(sys.argv) > 5 else {}
        
        result = feedback.capture_consequence(pred_id, actual_outcome, actual_value, evidence)
        print(json.dumps(result, indent=2))
    
    elif sys.argv[1] == '--accuracy':
        component = sys.argv[2] if len(sys.argv) > 2 else None
        hours = int(sys.argv[3]) if len(sys.argv) > 3 else 24
        result = feedback.get_prediction_accuracy(component, hours)
        print(json.dumps(result, indent=2))
    
    elif sys.argv[1] == '--corrections':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        result = feedback.get_corrections(limit)
        print(json.dumps(result, indent=2))
    
    else:
        print('Usage: consequence_feedback.py [--predict pred_id decision_id outcome value [component] [context]]|--capture pred_id outcome value [evidence]|--accuracy [component] [hours]|--corrections [limit]')


if __name__ == '__main__':
    main()