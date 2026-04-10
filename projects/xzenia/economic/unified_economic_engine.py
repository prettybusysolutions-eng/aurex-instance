#!/usr/bin/env python3
"""
UNIFIED ECONOMIC ENGINE
========================

Fuses External Value Loop + Real Consequence Feedback + Economic Intelligence
into a single economic optimization engine.

This creates the bridge between:
- Internal decisions (Decision Core)
- External value creation (Value Loop)
- Real consequences (Consequence Feedback)  
- Economic optimization (Economic Intelligence)

Returns ROI-driven decision recommendations.
"""
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
VALUE_LOOP = WORKSPACE / 'projects/xzenia/economic/external_value_loop.py'
CONSEQUENCE = WORKSPACE / 'projects/xzenia/economic/consequence_feedback.py'
ECONOMIC = WORKSPACE / 'projects/xzenia/economic/economic_intelligence.py'
UNIFIED_STATE = WORKSPACE / 'projects/xzenia/economic/unified-economic-state.json'


class UnifiedEconomicEngine:
    """
    Unified Economic Engine - fuses all economic components.
    
    The complete economic feedback loop:
    
    ┌────────────────────────────────────────────────────────────┐
    │                                                            │
    │   DECISION → VALUE_LOOP → CONSEQUENCE → ECONOMIC         │
    │       ↑                                              │    │
    │       └──────────────────────────────────────────────┘    │
    │                         │                                   │
    │                    OPTIMIZE                                │
    └────────────────────────────────────────────────────────────┘
    
    Every decision is measured for:
    - Expected value (before)
    - Actual value (after)
    - Prediction accuracy (feedback)
    - ROI optimization (learning)
    """
    
    def __init__(self):
        self.load_state()
    
    def load_state(self):
        if UNIFIED_STATE.exists():
            self.state = json.loads(UNIFIED_STATE.read_text())
        else:
            self.state = {
                'total_economic_cycles': 0,
                'decisions_optimized': 0,
                'value_created': 0.0,
                'net_value': 0.0,
                'avg_roi': 0.0,
                'prediction_accuracy': 0.0,
                'optimizations_made': 0,
                'last_cycle': None,
                'engine_status': 'initializing'
            }
        self.save_state()
    
    def save_state(self):
        UNIFIED_STATE.write_text(json.dumps(self.state, indent=2))
    
    def make_economic_decision(self, decision_id: str, task: str,
                                decision_type: str, component: str,
                                context: dict) -> dict:
        """Make a decision with full economic optimization."""
        cycle_start = time.time()
        
        # STEP 1: Analyze economic viability
        econ_result = self._run_component(ECONOMIC, '--analyze', 
                                          decision_id, decision_type, component, 
                                          json.dumps(context))
        
        if econ_result.get('economics', {}).get('is_economically_viable'):
            recommendation = 'proceed'
            confidence = econ_result['economics']['roi_percent'] / 100 + 0.5
        else:
            recommendation = 'reconsider'
            confidence = 0.3
        
        # STEP 2: Track for value measurement
        expected_value = econ_result['economics']['estimated_value']
        self._run_component(VALUE_LOOP, '--track', decision_id, 
                           json.dumps(context), str(expected_value))
        
        # STEP 3: Capture prediction for consequence tracking
        pred_id = f"pred-{decision_id}"
        self._run_component(CONSEQUENCE, '--predict', pred_id, decision_id,
                           recommendation, str(expected_value), component,
                           json.dumps(context))
        
        # Update state
        self.state['total_economic_cycles'] += 1
        self.state['decisions_optimized'] += 1
        self.state['last_cycle'] = datetime.now(timezone.utc).isoformat()
        self.state['engine_status'] = 'active'
        
        # Calculate overall metrics
        self._update_metrics()
        
        self.save_state()
        
        latency = int((time.time() - cycle_start) * 1000)
        
        return {
            'decision_id': decision_id,
            'task': task,
            'economic_analysis': econ_result,
            'recommendation': recommendation,
            'confidence': round(confidence, 2),
            'prediction_id': pred_id,
            'economic_state': {
                'value_created': self.state['value_created'],
                'net_value': self.state['net_value'],
                'avg_roi': self.state['avg_roi'],
                'prediction_accuracy': self.state['prediction_accuracy']
            },
            'cycle_latency_ms': latency
        }
    
    def record_outcome(self, prediction_id: str, decision_id: str,
                      actual_outcome: str, actual_value: float,
                      metrics: dict = None) -> dict:
        """Record the actual outcome and update economic model."""
        # STEP 1: Capture consequence
        consequence = self._run_component(CONSEQUENCE, '--capture',
                                         prediction_id, actual_outcome, 
                                         str(actual_value),
                                         json.dumps(metrics or {}))
        
        # STEP 2: Record actual value
        actual_cost = metrics.get('cost', 0.01) if metrics else 0.01
        economic = self._run_component(ECONOMIC, '--record',
                                       decision_id, str(actual_value),
                                       str(actual_cost))
        
        # STEP 3: Update value loop
        self._run_component(VALUE_LOOP, '--record', prediction_id,
                           actual_outcome, str(actual_value),
                           json.dumps(metrics or {}))
        
        # Update unified state
        self.state['net_value'] = economic.get('total_net_value', 0)
        
        # Get prediction accuracy
        acc_result = self._run_component(CONSEQUENCE, '--accuracy', 'all', '24')
        self.state['prediction_accuracy'] = acc_result.get('accuracy_percent', 0)
        
        self.save_state()
        
        return {
            'recorded': True,
            'consequence': consequence,
            'economic': economic,
            'value_loop': 'updated'
        }
    
    def get_optimization_recommendations(self) -> dict:
        """Get economic optimization recommendations."""
        # Get economic recommendations
        econ_recommend = self._run_component(ECONOMIC, '--recommend')
        
        # Get prediction accuracy by component
        acc_by_comp = {}
        for comp in ['decision_core', 'supervisor', 'csrm_governor']:
            acc = self._run_component(CONSEQUENCE, '--accuracy', comp, '24')
            if not acc.get('error'):
                acc_by_comp[comp] = acc['accuracy_percent']
        
        # Get value creation summary
        value_summary = self._run_component(VALUE_LOOP, '--calculate', '24')
        
        return {
            'economic_recommendations': econ_recommend,
            'prediction_accuracy_by_component': acc_by_comp,
            'value_creation_24h': value_summary,
            'engine_status': self.state['engine_status']
        }
    
    def _run_component(self, component_path: Path, *args) -> dict:
        """Run a subprocess component."""
        try:
            result = subprocess.run(
                ['python3', str(component_path)] + list(args),
                capture_output=True, text=True, timeout=30, cwd=str(WORKSPACE)
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except:
            pass
        return {}
    
    def _update_metrics(self):
        """Update aggregated metrics."""
        # Get current economic health
        health = self._run_component(ECONOMIC, '--health')
        
        self.state['value_created'] = health.get('total_value', 0)
        self.state['net_value'] = health.get('net_value', 0)
        self.state['avg_roi'] = health.get('roi_percent', 0)
        
        # Get prediction accuracy
        acc = self._run_component(CONSEQUENCE, '--accuracy', 'all', '24')
        self.state['prediction_accuracy'] = acc.get('accuracy_percent', 0)
    
    def get_full_economic_snapshot(self) -> dict:
        """Get complete economic snapshot."""
        health = self._run_component(ECONOMIC, '--health')
        roi = self._run_component(ECONOMIC, '--roi')
        value = self._run_component(VALUE_LOOP, '--calculate', '24')
        accuracy = self._run_component(CONSEQUENCE, '--accuracy', 'all', '24')
        
        return {
            'engine_status': self.state['engine_status'],
            'total_cycles': self.state['total_economic_cycles'],
            'health': health,
            'roi_by_type': roi,
            'value_24h': value,
            'prediction_accuracy': accuracy,
            'net_value': self.state['net_value'],
            'prediction_accuracy_percent': self.state['prediction_accuracy']
        }
    
    def get_status(self) -> dict:
        """Get unified engine status."""
        return {
            'status': self.state['engine_status'],
            'total_economic_cycles': self.state['total_economic_cycles'],
            'decisions_optimized': self.state['decisions_optimized'],
            'net_value': round(self.state['net_value'], 2),
            'avg_roi': self.state['avg_roi'],
            'prediction_accuracy': self.state['prediction_accuracy'],
            'optimizations_made': self.state['optimizations_made'],
            'last_cycle': self.state['last_cycle']
        }


def main():
    engine = UnifiedEconomicEngine()
    
    import sys
    
    if len(sys.argv) == 1:
        print(json.dumps(engine.get_status(), indent=2))
    
    elif sys.argv[1] == '--decide' and len(sys.argv) > 5:
        decision_id = sys.argv[2]
        task = sys.argv[3]
        decision_type = sys.argv[4]
        component = sys.argv[5]
        context = json.loads(sys.argv[6]) if len(sys.argv) > 6 else {}
        
        result = engine.make_economic_decision(decision_id, task, decision_type, component, context)
        print(json.dumps(result, indent=2))
    
    elif sys.argv[1] == '--record' and len(sys.argv) > 4:
        prediction_id = sys.argv[2]
        decision_id = sys.argv[3]
        outcome = sys.argv[4]
        value = float(sys.argv[5]) if len(sys.argv) > 5 else 10.0
        metrics = json.loads(sys.argv[6]) if len(sys.argv) > 6 else {}
        
        result = engine.record_outcome(prediction_id, decision_id, outcome, value, metrics)
        print(json.dumps(result, indent=2))
    
    elif sys.argv[1] == '--recommend':
        result = engine.get_optimization_recommendations()
        print(json.dumps(result, indent=2))
    
    elif sys.argv[1] == '--snapshot':
        result = engine.get_full_economic_snapshot()
        print(json.dumps(result, indent=2))
    
    else:
        print('Usage: unified_economic_engine.py [--decide decision_id task type component [context]]|--record prediction_id decision_id outcome value [metrics]|--recommend|--snapshot')


if __name__ == '__main__':
    main()