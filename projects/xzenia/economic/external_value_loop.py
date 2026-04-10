#!/usr/bin/env python3
"""
EXTERNAL VALUE LOOP
===================

Tracks value creation outside the system.
Measures how Xzenia's decisions affect:
- Task completion
- Time saved
- Quality improvements
- Revenue impact
- Cost reduction

This connects internal decisions to external outcomes.
"""
import json
import sqlite3
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
DB = WORKSPACE / 'projects/xzenia/csmr/ledger/causal_ledger.sqlite'
VALUE_LOG = WORKSPACE / 'projects/xzenia/economic/value-log.json'
VALUE_STATE = WORKSPACE / 'projects/xzenia/economic/value-state.json'


class ExternalValueLoop:
    """
    External Value Loop - tracks value created outside the system.
    
    Measures:
    - Task completion rate
    - Time saved vs manual
    - Quality improvements
    - Revenue/cost impact
    
    This is the bridge between internal decisions and external outcomes.
    """
    
    def __init__(self):
        self.load_state()
    
    def load_state(self):
        if VALUE_STATE.exists():
            self.state = json.loads(VALUE_STATE.read_text())
        else:
            self.state = {
                'total_decisions_tracked': 0,
                'total_value_created': 0.0,
                'tasks_completed': 0,
                'tasks_failed': 0,
                'time_saved_minutes': 0,
                'quality_improvements': 0,
                'revenue_impact': 0.0,
                'cost_saved': 0.0,
                'by_component': {},
                'by_outcome_type': {}
            }
        self.save_state()
    
    def save_state(self):
        VALUE_STATE.write_text(json.dumps(self.state, indent=2))
    
    def track_decision(self, decision_id: str, context: dict, expected_value: float) -> str:
        """Track a decision for value measurement."""
        track_id = f"value-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        
        # Store in value log
        self._log_value_event(track_id, decision_id, context, expected_value, 'pending')
        
        return track_id
    
    def record_outcome(self, track_id: str, outcome: str, actual_value: float, metrics: dict):
        """Record the actual outcome of a tracked decision."""
        self.state['total_decisions_tracked'] += 1
        
        # Update by outcome type
        outcome_type = outcome  # success, failure, partial
        self.state['by_outcome_type'][outcome_type] = self.state['by_outcome_type'].get(outcome_type, 0) + 1
        
        if outcome == 'success':
            self.state['tasks_completed'] += 1
            self.state['total_value_created'] += actual_value
            
            # Extract metrics
            if metrics.get('time_saved'):
                self.state['time_saved_minutes'] += metrics['time_saved']
            
            if metrics.get('quality_boost'):
                self.state['quality_improvements'] += metrics['quality_boost']
            
            if metrics.get('revenue_impact'):
                self.state['revenue_impact'] += metrics['revenue_impact']
            
            if metrics.get('cost_saved'):
                self.state['cost_saved'] += metrics['cost_saved']
        
        elif outcome == 'failure':
            self.state['tasks_failed'] += 1
        
        # Log the outcome
        self._log_value_event(track_id, None, None, actual_value, outcome, metrics)
        
        self.save_state()
    
    def _log_value_event(self, track_id: str, decision_id: str, context: dict, 
                         value: float, status: str, metrics: dict = None):
        """Log value event."""
        events = []
        if VALUE_LOG.exists():
            try:
                events = json.loads(VALUE_LOG.read_text())
            except:
                events = []
        
        events.append({
            'track_id': track_id,
            'decision_id': decision_id,
            'context': context,
            'value': value,
            'status': status,
            'metrics': metrics or {},
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
        # Keep last 1000
        if len(events) > 1000:
            events = events[-1000:]
        
        VALUE_LOG.write_text(json.dumps(events, indent=2))
    
    def calculate_value_creation(self, time_window_hours: int = 24) -> dict:
        """Calculate value creation over time window."""
        # Get recent decisions
        events = []
        if VALUE_LOG.exists():
            try:
                events = json.loads(VALUE_LOG.read_text())
            except: pass
        
        # Filter by time
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
        
        recent = [e for e in events if datetime.fromisoformat(e['timestamp'].replace('Z', '+00:00')) > cutoff]
        
        # Calculate metrics
        completed = sum(1 for e in recent if e['status'] == 'success')
        failed = sum(1 for e in recent if e['status'] == 'failure')
        total = completed + failed
        
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        # Sum values
        total_value = sum(e['value'] for e in recent)
        
        # Extract metrics
        time_saved = sum(e.get('metrics', {}).get('time_saved', 0) for e in recent)
        quality = sum(e.get('metrics', {}).get('quality_boost', 0) for e in recent)
        revenue = sum(e.get('metrics', {}).get('revenue_impact', 0) for e in recent)
        costs = sum(e.get('metrics', {}).get('cost_saved', 0) for e in recent)
        
        return {
            'time_window_hours': time_window_hours,
            'decisions_tracked': len(recent),
            'completion_rate': round(completion_rate, 1),
            'completed': completed,
            'failed': failed,
            'total_value_created': round(total_value, 2),
            'metrics': {
                'time_saved_minutes': time_saved,
                'quality_improvements': quality,
                'revenue_impact': revenue,
                'cost_saved': costs
            }
        }
    
    def estimate_decision_value(self, decision_type: str, context: dict) -> dict:
        """Estimate potential value of a decision."""
        # Base values by decision type
        base_values = {
            'execution': {'time_saved': 5, 'value': 10},
            'repair': {'time_saved': 15, 'value': 30},
            'frontier': {'time_saved': 30, 'value': 100},
            'analysis': {'time_saved': 10, 'value': 20},
            'deliberation': {'time_saved': 5, 'value': 10}
        }
        
        base = base_values.get(decision_type, {'time_saved': 5, 'value': 10})
        
        # Adjust based on context
        # (In production: would use ML model)
        complexity_factor = context.get('complexity', 0.5)
        
        estimated = {
            'decision_type': decision_type,
            'estimated_time_saved': base['time_saved'] * (0.5 + complexity_factor),
            'estimated_value': base['value'] * (0.5 + complexity_factor),
            'confidence': 0.6
        }
        
        return estimated
    
    def get_status(self) -> dict:
        """Get value loop status."""
        return {
            'status': 'active',
            'total_tracked': self.state['total_decisions_tracked'],
            'completion_rate': round(
                self.state['tasks_completed'] / max(1, self.state['tasks_completed'] + self.state['tasks_failed']) * 100, 1
            ),
            'total_value': round(self.state['total_value_created'], 2),
            'time_saved_minutes': self.state['time_saved_minutes'],
            'revenue_impact': round(self.state['revenue_impact'], 2),
            'cost_saved': round(self.state['cost_saved'], 2)
        }


def main():
    loop = ExternalValueLoop()
    
    import sys
    
    if len(sys.argv) == 1:
        print(json.dumps(loop.get_status(), indent=2))
    
    elif sys.argv[1] == '--track' and len(sys.argv) > 2:
        decision_id = sys.argv[2]
        context = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        value = float(sys.argv[4]) if len(sys.argv) > 4 else 10.0
        track_id = loop.track_decision(decision_id, context, value)
        print(json.dumps({'tracked': True, 'track_id': track_id}))
    
    elif sys.argv[1] == '--record' and len(sys.argv) > 3:
        track_id = sys.argv[2]
        outcome = sys.argv[3]  # success, failure, partial
        value = float(sys.argv[4]) if len(sys.argv) > 4 else 10.0
        metrics = json.loads(sys.argv[5]) if len(sys.argv) > 5 else {}
        loop.record_outcome(track_id, outcome, value, metrics)
        print(json.dumps({'recorded': True}))
    
    elif sys.argv[1] == '--calculate':
        hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
        result = loop.calculate_value_creation(hours)
        print(json.dumps(result, indent=2))
    
    elif sys.argv[1] == '--estimate' and len(sys.argv) > 2:
        decision_type = sys.argv[2]
        context = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        result = loop.estimate_decision_value(decision_type, context)
        print(json.dumps(result, indent=2))
    
    else:
        print('Usage: external_value_loop.py [--track decision_id [context] [value]]|--record track_id outcome value [metrics]|--calculate [hours]|--estimate decision_type [context]')


if __name__ == '__main__':
    main()