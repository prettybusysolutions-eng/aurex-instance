#!/usr/bin/env python3
"""
ECONOMIC INTELLIGENCE
======================

Optimizes decisions for economic value.
Combines:
- External value loop (what we created)
- Real consequence feedback (what actually happened)
- Economic models (costs, revenue, ROI)

This creates an intelligence layer that optimizes for VALUE,
not just task completion.
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
ECONOMIC_STATE = WORKSPACE / 'projects/xzenia/economic/economic-state.json'
VALUE_LOOP = WORKSPACE / 'projects/xzenia/economic/external_value_loop.py'
CONSEQUENCE = WORKSPACE / 'projects/xzenia/economic/consequence_feedback.py'

# Economic models
COST_PER_DECISION = 0.001  # Edge execution
COST_PER_CLOUD = 0.05      # Cloud execution
COST_PER_HOUR_IDLE = 0.1   # Opportunity cost

VALUE_TYPES = {
    'task_completion': 10.0,
    'time_saved': 0.5,     # Per minute
    'quality_improvement': 25.0,
    'error_prevention': 50.0,
    'revenue_impact': 100.0,
    'cost_avoidance': 75.0
}


class EconomicIntelligence:
    """
    Economic Intelligence - optimizes for value.
    
    Key insight: Not all decisions are equal in economic value.
    This layer:
    - Measures ROI of each decision
    - Predicts economic impact before acting
    - Adjusts decision thresholds based on value
    - Creates economic feedback loop
    """
    
    def __init__(self):
        self.load_state()
    
    def load_state(self):
        if ECONOMIC_STATE.exists():
            self.state = json.loads(ECONOMIC_STATE.read_text())
        else:
            self.state = {
                'total_decisions_analyzed': 0,
                'total_value_generated': 0.0,
                'total_cost_incurred': 0.0,
                'net_value': 0.0,
                'roi_percent': 0.0,
                'by_decision_type': {},
                'by_component': {},
                'economic_trends': [],
                'value_optimization_enabled': True,
                'last_optimization': None
            }
        self.save_state()
    
    def save_state(self):
        ECONOMIC_STATE.write_text(json.dumps(self.state, indent=2))
    
    def analyze_decision(self, decision_id: str, decision_type: str,
                        component: str, context: dict) -> dict:
        """Analyze the economic impact of a decision."""
        start_time = time.time()
        
        # Get cost
        cost = self._calculate_cost(decision_type, context)
        
        # Estimate value
        estimated_value = self._estimate_value(decision_type, context)
        
        # Calculate expected ROI
        roi = ((estimated_value - cost) / cost * 100) if cost > 0 else 0
        
        # Determine if economically justified
        is_economically_viable = estimated_value > cost * 1.5  # Need 50% margin
        
        # Build analysis
        analysis = {
            'decision_id': decision_id,
            'decision_type': decision_type,
            'component': component,
            'economics': {
                'cost': round(cost, 4),
                'estimated_value': round(estimated_value, 2),
                'net_expected_value': round(estimated_value - cost, 2),
                'roi_percent': round(roi, 1),
                'is_economically_viable': is_economically_viable
            },
            'recommendation': 'proceed' if is_economically_viable else 'reconsider',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Update state
        self.state['total_decisions_analyzed'] += 1
        self.state['total_cost_incurred'] += cost
        
        # Track by type
        if decision_type not in self.state['by_decision_type']:
            self.state['by_decision_type'][decision_type] = {
                'count': 0, 'total_cost': 0, 'total_value': 0
            }
        
        self.state['by_decision_type'][decision_type]['count'] += 1
        self.state['by_decision_type'][decision_type]['total_cost'] += cost
        
        # Track by component
        if component not in self.state['by_component']:
            self.state['by_component'][component] = {
                'count': 0, 'total_cost': 0, 'total_value': 0
            }
        
        self.state['by_component'][component]['count'] += 1
        self.state['by_component'][component]['total_cost'] += cost
        
        self.save_state()
        
        latency = int((time.time() - start_time) * 1000)
        analysis['latency_ms'] = latency
        
        return analysis
    
    def _calculate_cost(self, decision_type: str, context: dict) -> float:
        """Calculate the cost of a decision."""
        # Base cost by type
        costs = {
            'execution': 0.001,   # Edge execution
            'repair': 0.01,       # Repair takes resources
            'frontier': 0.05,     # Frontier execution
            'analysis': 0.02,     # Analysis cloud cost
            'deliberation': 0.03, # Thinking time
            'continue': 0.001,    # Minimal cost
            'think_deeper': 0.05  # Cloud reasoning
        }
        
        base_cost = costs.get(decision_type, 0.01)
        
        # Adjust by context
        context_multiplier = 1.0
        
        if context.get('complexity'):
            context_multiplier *= (1 + context['complexity'])
        
        if context.get('urgency', 0) > 0.7:
            context_multiplier *= 1.2  # Urgent costs more
        
        return base_cost * context_multiplier
    
    def _estimate_value(self, decision_type: str, context: dict) -> float:
        """Estimate value created by decision type."""
        base_values = {
            'execution': 10.0,
            'repair': 30.0,
            'frontier': 100.0,
            'analysis': 20.0,
            'deliberation': 15.0,
            'continue': 5.0,
            'think_deeper': 25.0
        }
        
        base_value = base_values.get(decision_type, 10.0)
        
        # Adjust by context
        if context.get('urgency', 0) > 0.7:
            base_value *= 1.3  # Urgent tasks more valuable
        
        if context.get('importance'):
            base_value *= (1 + context['importance'])
        
        return base_value
    
    def record_actual_value(self, decision_id: str, actual_value: float, 
                           actual_cost: float = None) -> dict:
        """Record actual value created."""
        if actual_cost is None:
            actual_cost = 0.01  # Default
        
        net_value = actual_value - actual_cost
        roi = ((actual_value - actual_cost) / actual_cost * 100) if actual_cost > 0 else 0
        
        # Update state
        self.state['total_value_generated'] += actual_value
        self.state['total_cost_incurred'] += actual_cost
        self.state['net_value'] += net_value
        
        if self.state['total_cost_incurred'] > 0:
            self.state['roi_percent'] = round(
                (self.state['total_value_generated'] / self.state['total_cost_incurred'] - 1) * 100, 1
            )
        
        self.state['last_optimization'] = datetime.now(timezone.utc).isoformat()
        self.save_state()
        
        return {
            'decision_id': decision_id,
            'actual_value': actual_value,
            'actual_cost': actual_cost,
            'net_value': net_value,
            'roi_percent': round(roi, 1),
            'total_net_value': round(self.state['net_value'], 2),
            'total_roi': self.state['roi_percent']
        }
    
    def get_roi_by_type(self) -> dict:
        """Get ROI breakdown by decision type."""
        roi_by_type = {}
        
        for dtype, data in self.state['by_decision_type'].items():
            if data['total_cost'] > 0:
                roi = ((data.get('total_value', data['total_cost'] * 2) - data['total_cost']) 
                       / data['total_cost'] * 100)
            else:
                roi = 0
            
            roi_by_type[dtype] = {
                'count': data['count'],
                'total_cost': round(data['total_cost'], 4),
                'total_value': round(data.get('total_value', data['total_cost'] * 2), 2),
                'roi_percent': round(roi, 1)
            }
        
        return roi_by_type
    
    def get_economic_health(self) -> dict:
        """Get overall economic health."""
        return {
            'status': 'healthy' if self.state['net_value'] > 0 else 'degraded',
            'total_decisions': self.state['total_decisions_analyzed'],
            'total_value': round(self.state['total_value_generated'], 2),
            'total_cost': round(self.state['total_cost_incurred'], 4),
            'net_value': round(self.state['net_value'], 2),
            'roi_percent': self.state['roi_percent'],
            'optimization_enabled': self.state['value_optimization_enabled'],
            'last_optimization': self.state['last_optimization']
        }
    
    def optimize_decision_threshold(self, current_threshold: float, 
                                   decision_type: str) -> float:
        """Optimize decision threshold based on economic performance."""
        # Get historical ROI for this decision type
        type_data = self.state['by_decision_type'].get(decision_type, {})
        
        if type_data.get('count', 0) < 5:
            return current_threshold  # Not enough data
        
        roi = 0
        if type_data.get('total_cost', 0) > 0:
            roi = ((type_data.get('total_value', type_data['total_cost'] * 2) - type_data['total_cost']) 
                   / type_data['total_cost'] * 100)
        
        # Adjust threshold based on ROI
        # High ROI = can be more confident (lower threshold)
        # Low ROI = need more evidence (higher threshold)
        
        if roi > 100:
            # Excellent ROI - can be very confident
            return max(0.5, current_threshold - 0.05)
        elif roi > 50:
            # Good ROI
            return max(0.5, current_threshold - 0.02)
        elif roi > 0:
            # Positive but low ROI
            return current_threshold
        elif roi > -25:
            # Negative ROI - be more careful
            return min(0.85, current_threshold + 0.03)
        else:
            # Strong negative - very careful
            return min(0.9, current_threshold + 0.05)
    
    def recommend_optimizations(self) -> List[dict]:
        """Recommend economic optimizations."""
        recommendations = []
        
        # Check decision types with negative ROI
        roi_by_type = self.get_roi_by_type()
        
        for dtype, data in roi_by_type.items():
            if data['roi_percent'] < 0:
                recommendations.append({
                    'type': 'reduce_decision_type',
                    'decision_type': dtype,
                    'reason': f"Negative ROI ({data['roi_percent']}%)",
                    'action': f"Consider increasing threshold for {dtype} decisions"
                })
        
        # Check if total net value is declining
        if len(self.state.get('economic_trends', [])) > 5:
            # Would analyze trend
        
        return recommendations
    
    def get_status(self) -> dict:
        """Get economic intelligence status."""
        return {
            'status': 'active',
            'optimization': self.state['value_optimization_enabled'],
            'decisions_analyzed': self.state['total_decisions_analyzed'],
            'total_value': round(self.state['total_value_generated'], 2),
            'total_cost': round(self.state['total_cost_incurred'], 4),
            'net_value': round(self.state['net_value'], 2),
            'roi': f"{self.state['roi_percent']}%",
            'decision_types_tracked': len(self.state['by_decision_type']),
            'components_tracked': len(self.state['by_component'])
        }


def main():
    intelligence = EconomicIntelligence()
    
    import sys
    
    if len(sys.argv) == 1:
        print(json.dumps(intelligence.get_status(), indent=2))
    
    elif sys.argv[1] == '--analyze' and len(sys.argv) > 4:
        decision_id = sys.argv[2]
        decision_type = sys.argv[3]
        component = sys.argv[4]
        context = json.loads(sys.argv[5]) if len(sys.argv) > 5 else {}
        
        result = intelligence.analyze_decision(decision_id, decision_type, component, context)
        print(json.dumps(result, indent=2))
    
    elif sys.argv[1] == '--record' and len(sys.argv) > 3:
        decision_id = sys.argv[2]
        value = float(sys.argv[3])
        cost = float(sys.argv[4]) if len(sys.argv) > 4 else None
        
        result = intelligence.record_actual_value(decision_id, value, cost)
        print(json.dumps(result, indent=2))
    
    elif sys.argv[1] == '--roi':
        print(json.dumps(intelligence.get_roi_by_type(), indent=2))
    
    elif sys.argv[1] == '--health':
        print(json.dumps(intelligence.get_economic_health(), indent=2))
    
    elif sys.argv[1] == '--recommend':
        result = intelligence.recommend_optimizations()
        print(json.dumps(result, indent=2))
    
    elif sys.argv[1] == '--optimize' and len(sys.argv) > 3:
        threshold = float(sys.argv[2])
        dtype = sys.argv[3]
        result = intelligence.optimize_decision_threshold(threshold, dtype)
        print(json.dumps({'original': threshold, 'optimized': result}))
    
    else:
        print('Usage: economic_intelligence.py [--analyze decision_id type component [context]]|--record decision_id value [cost]|--roi|--health|--recommend|--optimize threshold dtype]')


if __name__ == '__main__':
    main()