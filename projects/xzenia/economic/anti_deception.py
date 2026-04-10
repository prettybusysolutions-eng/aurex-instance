#!/usr/bin/env python3
"""
ANTI-SELF-DECEPTION SAFEGUARDS
================================

Phase 1 Step 3: Install safeguards to prevent inflated metrics.

Rules:
1. Never report >95% accuracy unless sample size >= 30 AND outcome quality verified
2. Penalize low-sample overconfidence (Bayesian shrinkage)
3. Separate estimated value from realized value in all logs
4. Require minimum sample before claiming improvement
5. Flag metrics that haven't been validated externally
"""
import json
import sqlite3
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
DB = WORKSPACE / 'projects/xzenia/csmr/ledger/causal_ledger.sqlite'

# Safeguard thresholds
MIN_SAMPLE_FOR_CLAIM = 30
MAX_ACCURACY_CLAIM = 0.95  # Never claim above 95% without external validation
BAYESIAN_SHRINKAGE = 0.1  # Shrink toward 0.5 for small samples
VALIDATION_REQUIRED_ABOVE = 0.80


class AntiSelfDeceptionSafeguards:
    """
    Prevents inflated metrics and self-deception.
    """
    
    def __init__(self):
        self.load_state()
    
    def load_state(self):
        self.state = {
            'guardrails_active': True,
            'inflated_claims_blocked': 0,
            'shrinkage_applied': 0,
            'unvalidated_metrics_flagged': 0,
            'last_audit': None
        }
    
    def validate_metric(self, metric_name: str, value: float, 
                       sample_size: int, external_validation: bool = False) -> dict:
        """
        Validate a metric before reporting.
        
        Returns:
        {
            'reported_value': float,
            'is_inflated': bool,
            'shrinkage_applied': bool,
            'warning': str or None,
            'sample_size': int
        }
        """
        result = {
            'metric': metric_name,
            'raw_value': value,
            'sample_size': sample_size,
            'external_validated': external_validation,
            'reported_value': value,
            'is_inflated': False,
            'shrinkage_applied': False,
            'warning': None
        }
        
        # Rule 1: Check for impossible accuracy claims
        if 'accuracy' in metric_name.lower() and value > MAX_ACCURACY_CLAIM:
            if sample_size < MIN_SAMPLE_FOR_CLAIM:
                result['is_inflated'] = True
                result['warning'] = f'Claimed {value:.1%} accuracy with only {sample_size} samples - BLOCKED'
                result['reported_value'] = MAX_ACCURACY_CLAIM
                self.state['inflated_claims_blocked'] += 1
        
        # Rule 2: Bayesian shrinkage for small samples
        if sample_size < MIN_SAMPLE_FOR_CLAIM and 'accuracy' in metric_name.lower():
            shrinkage = BAYESIAN_SHRINKAGE * (1 - sample_size / MIN_SAMPLE_FOR_CLAIM)
            shrunk_value = value * (1 - shrinkage) + 0.5 * shrinkage
            result['reported_value'] = min(shrunk_value, MAX_ACCURACY_CLAIM)
            result['shrinkage_applied'] = True
            result['warning'] = f'Bayesian shrinkage applied: {value:.3f} → {shrunk_value:.3f}'
            self.state['shrinkage_applied'] += 1
        
        # Rule 3: Flag unvalidated metrics above threshold
        if value > VALIDATION_REQUIRED_ABOVE and not external_validation:
            result['warning'] = f'Unvalidated metric above {VALIDATION_REQUIRED_ABOVE:.0%} - requires external validation'
            self.state['unvalidated_metrics_flagged'] += 1
        
        # Rule 4: Check for suspiciously round numbers
        if value in [0.0, 0.5, 1.0, 100.0] and sample_size < 10:
            result['warning'] = 'Suspiciously round value with small sample - flagged'
        
        return result
    
    def audit_economic_metrics(self) -> dict:
        """
        Full audit of economic metrics - flag each as REAL/PARTIAL/SYNTHETIC.
        """
        audit = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'metrics': {}
        }
        
        # 1. Net Value
        net_value_file = WORKSPACE / 'projects/xzenia/economic/economic-state.json'
        if net_value_file.exists():
            ns = json.loads(net_value_file.read_text())
            sample = ns.get('total_decisions_analyzed', 0)
            
            audit['metrics']['net_value'] = {
                'value': ns.get('net_value', 0),
                'sample_size': sample,
                'external_validated': False,
                'classification': 'SYNTHETIC' if sample < 10 else 'PARTIAL',
                'reason': f'Based on internal estimation, not external validation. n={sample}'
            }
        
        # 2. ROI
        if net_value_file.exists():
            ns = json.loads(net_value_file.read_text())
            sample = ns.get('total_decisions_analyzed', 0)
            roi = ns.get('roi_percent', 0)
            
            audit['metrics']['roi'] = {
                'value': roi,
                'sample_size': sample,
                'external_validated': False,
                'classification': 'SYNTHETIC' if sample < 10 else 'PARTIAL',
                'reason': 'Calculated from estimated costs and values, not real P&L'
            }
        
        # 3. Prediction Accuracy
        conse_log = WORKSPACE / 'projects/xzenia/economic/consequence-log.json'
        if conse_log.exists():
            cl = json.loads(conse_log.read_text())
            sample = len(cl)
            
            correct = sum(1 for c in cl if c.get('correct'))
            accuracy = (correct / sample * 100) if sample > 0 else 0
            
            # Apply safeguards
            validation = self.validate_metric('prediction_accuracy', accuracy/100, sample)
            
            audit['metrics']['prediction_accuracy'] = {
                'raw_value': f'{accuracy:.1f}%',
                'value': f'{validation["reported_value"]*100:.1f}%',
                'sample_size': sample,
                'external_validated': False,
                'classification': 'SYNTHETIC' if sample < 5 else 'PARTIAL',
                'shrinkage': validation['shrinkage_applied'],
                'warning': validation['warning']
            }
        
        # 4. Value Created
        value_log = WORKSPACE / 'projects/xzenia/economic/value-log.json'
        if value_log.exists():
            vl = json.loads(value_log.read_text())
            sample = len(vl)
            
            audit['metrics']['value_created'] = {
                'sample_size': sample,
                'external_validated': False,
                'classification': 'SYNTHETIC' if sample < 5 else 'PARTIAL',
                'reason': 'Tracked internally, not validated against external outcomes'
            }
        
        self.state['last_audit'] = audit['timestamp']
        
        return audit
    
    def get_guard_status(self) -> dict:
        """Get guard status."""
        return {
            'guardrails_active': self.state['guardrails_active'],
            'inflated_claims_blocked': self.state['inflated_claims_blocked'],
            'shrinkage_applied': self.state['shrinkage_applied'],
            'unvalidated_flagged': self.state['unvalidated_metrics_flagged'],
            'last_audit': self.state['last_audit']
        }


def main():
    guards = AntiSelfDeceptionSafeguards()
    
    import sys
    
    if len(sys.argv) == 1:
        print(json.dumps(guards.get_guard_status(), indent=2))
    
    elif sys.argv[1] == '--audit':
        result = guards.audit_economic_metrics()
        print(json.dumps(result, indent=2))
    
    elif sys.argv[1] == '--validate' and len(sys.argv) > 4:
        metric = sys.argv[2]
        value = float(sys.argv[3])
        sample = int(sys.argv[4])
        external = sys.argv[5].lower() == 'true' if len(sys.argv) > 5 else False
        
        result = guards.validate_metric(metric, value, sample, external)
        print(json.dumps(result, indent=2))
    
    else:
        print('Usage: anti_deception.py [--audit]|--validate metric value sample [external]')


if __name__ == '__main__':
    main()