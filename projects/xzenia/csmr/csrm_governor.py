#!/usr/bin/env python3
"""
CSMR GOVERNOR — Active Decision Gate for CSMR
===============================================

CSMR is no longer passive — it now GOVERNSSelf-modification requests.
Before any proposal is applied, it must pass through the Decision Core.

This is the active governor layer that makes CSMR "think" about mutations.
"""
import json
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path('/Users/marcuscoarchitect/.openclaw/workspace')
DB = WORKSPACE / 'projects/xzenia/csmr/ledger/causal_ledger.sqlite'
DECISION_CORE = WORKSPACE / 'projects/xzenia/csmr/decision_core/decision_core.py'
REPORTS_DIR = WORKSPACE / 'projects/xzenia/csmr/reports'
GOVERNOR_STATE = WORKSPACE / 'projects/xzenia/csmr/governor-state.json'

# Governor thresholds
MIN_CONFIDENCE = 0.6
RISK_LIMIT = 0.5
GOVERNANCE_LOG = REPORTS_DIR / 'csrm-governor-log.json'


class CSMRGovernor:
    """
    Active governor for CSMR.
    
    Before any proposal is applied:
    1. Evaluate the proposal through Decision Core
    2. Check risk thresholds
    3. Verify alignment with system goals
    4. Approve, modify, or reject
    
    This makes CSMR a thinking governor, not just a pipeline.
    """
    
    def __init__(self):
        self.load_state()
    
    def load_state(self):
        if GOVERNOR_STATE.exists():
            self.state = json.loads(GOVERNOR_STATE.read_text())
        else:
            self.state = {
                'proposals_reviewed': 0,
                'proposals_approved': 0,
                'proposals_rejected': 0,
                'proposals_modified': 0,
                'total_governance_cost_ms': 0,
                'avg_confidence': 0.0
            }
        self.save_state()
    
    def save_state(self):
        GOVERNOR_STATE.write_text(json.dumps(self.state, indent=2))
    
    def run_decision_core(self, task: str, context: dict) -> dict:
        """Run Decision Core to evaluate proposal."""
        result = subprocess.run(
            ['python3', DECISION_CORE, '--decide', task, json.dumps(context)],
            capture_output=True, text=True, cwd=str(WORKSPACE)
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {'error': 'Decision Core unavailable', 'fallback': True}
    
    def evaluate_proposal(self, proposal: dict) -> dict:
        """Evaluate a single proposal through Decision Core."""
        start = time.time()
        
        # Parse proposal content
        try:
            pj = json.loads(proposal.get('proposal_json', '{}'))
        except:
            pj = {}
        
        # Build context for Decision Core
        context = {
            'task': f'govern_proposal_{proposal.get("proposal_id")}',
            'proposal_type': pj.get('type', 'unknown'),
            'proposal_target': pj.get('target', 'unknown'),
            'proposal_change': pj.get('change', {}),
            'proposal_source': proposal.get('source_event_id'),
            'current_status': proposal.get('status'),
            'governance_mode': True
        }
        
        # THINK about this proposal
        decision = self.run_decision_core(f'Govern CSMR proposal for {pj.get("target", "unknown")}', context)
        
        # Extract decision
        selection = decision.get('selection', {})
        selected = selection.get('selected', 'continue')
        confidence = selection.get('confidence', 0.5)
        reasoning = selection.get('reasoning', '')
        
        # Evaluate against thresholds
        risk_assessment = self._assess_risk(pj)
        
        # Governance decision
        if confidence >= MIN_CONFIDENCE and risk_assessment['risk_level'] <= RISK_LIMIT:
            if selected in ['continue', 'frontier_3']:
                governance_decision = 'approve'
            elif selected == 'think_deeper':
                governance_decision = 'defer'
            else:
                governance_decision = 'approve_with_modification'
        else:
            governance_decision = 'reject'
        
        # Update state
        self.state['proposals_reviewed'] += 1
        if governance_decision == 'approve':
            self.state['proposals_approved'] += 1
        elif governance_decision == 'reject':
            self.state['proposals_rejected'] += 1
        elif governance_decision == 'approve_with_modification':
            self.state['proposals_modified'] += 1
        
        latency = int((time.time() - start) * 1000)
        self.state['total_governance_cost_ms'] += latency
        self.state['avg_confidence'] = (
            (self.state['avg_confidence'] * (self.state['proposals_reviewed'] - 1) + confidence) 
            / self.state['proposals_reviewed']
        )
        self.save_state()
        
        # Log governance decision
        governance = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'proposal_id': proposal.get('proposal_id'),
            'governance_decision': governance_decision,
            'decision_core': {
                'selected': selected,
                'confidence': confidence,
                'net_value': selection.get('net_value', 0),
                'reasoning': reasoning[:200]
            },
            'risk_assessment': risk_assessment,
            'latency_ms': latency,
            'context': context
        }
        
        self._log_governance(governance)
        
        return {
            'governed': True,
            'decision': governance_decision,
            'proposal_id': proposal.get('proposal_id'),
            'confidence': confidence,
            'risk': risk_assessment['risk_level'],
            'reasoning': reasoning[:200],
            'can_apply': governance_decision == 'approve',
            'governance': governance
        }
    
    def _assess_risk(self, proposal_json: dict) -> dict:
        """Assess risk level of proposal."""
        risk_factors = []
        
        # Target risk
        target = proposal_json.get('target', '')
        if 'orchestration' in target or 'resilience' in target:
            risk_factors.append({'factor': 'critical_component', 'severity': 'high'})
        elif 'execution' in target or 'supervisor' in target:
            risk_factors.append({'factor': 'execution_component', 'severity': 'medium'})
        
        # Change risk
        change = proposal_json.get('change', {})
        if isinstance(change, dict):
            # Deep changes are riskier
            if len(change) > 3:
                risk_factors.append({'factor': 'many_changes', 'severity': 'medium'})
        
        # Calculate risk level
        high_count = sum(1 for f in risk_factors if f['severity'] == 'high')
        medium_count = sum(1 for f in risk_factors if f['severity'] == 'medium')
        
        if high_count > 0:
            risk_level = 0.8
        elif medium_count > 2:
            risk_level = 0.6
        elif medium_count > 0:
            risk_level = 0.4
        else:
            risk_level = 0.2
        
        return {
            'risk_level': risk_level,
            'factors': risk_factors,
            'can_proceed': risk_level <= RISK_LIMIT
        }
    
    def _log_governance(self, governance: dict):
        """Log governance decision."""
        # Update main log
        logs = []
        if GOVERNANCE_LOG.exists():
            try:
                logs = json.loads(GOVERVERNANCE_LOG.read_text())
            except:
                logs = []
        
        logs.append(governance)
        if len(logs) > 100:
            logs = logs[-100:]
        
        GOVERNANCE_LOG.write_text(json.dumps(logs, indent=2))
    
    def govern_proposals(self, status_filter: str = 'validated_gate_a') -> dict:
        """Govern all proposals with a given status."""
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        cur.execute(f'''
            SELECT * FROM modification_proposals 
            WHERE status = ?
            LIMIT 20
        ''', (status_filter,))
        
        proposals = [dict(row) for row in cur.fetchall()]
        conn.close()
        
        results = []
        for proposal in proposals:
            result = self.evaluate_proposal(proposal)
            results.append(result)
        
        # Apply governance decisions
        for r in results:
            if r['can_apply']:
                self._approve_proposal(r['proposal_id'])
            else:
                self._reject_proposal(r['proposal_id'], r['reasoning'])
        
        return {
            'governed_count': len(results),
            'approved': sum(1 for r in results if r['decision'] == 'approve'),
            'rejected': sum(1 for r in results if r['decision'] == 'reject'),
            'modified': sum(1 for r in results if r['decision'] == 'approve_with_modification'),
            'deferred': sum(1 for r in results if r['decision'] == 'defer'),
            'results': results
        }
    
    def _approve_proposal(self, proposal_id: str):
        """Update proposal to promoted status."""
        conn = sqlite3.connect(DB)
        conn.execute('''
            UPDATE modification_proposals 
            SET status = 'governor_approved'
            WHERE proposal_id = ?
        ''', (proposal_id,))
        conn.commit()
        conn.close()
    
    def _reject_proposal(self, proposal_id: str, reason: str):
        """Update proposal to governor_rejected status."""
        conn = sqlite3.connect(DB)
        conn.execute('''
            UPDATE modification_proposals 
            SET status = 'governor_rejected'
            WHERE proposal_id = ?
        ''', (proposal_id,))
        conn.commit()
        conn.close()
    
    def get_status(self) -> dict:
        """Get governor status."""
        return {
            'status': 'active',
            'governing': True,
            'total_proposals_reviewed': self.state['proposals_reviewed'],
            'approved': self.state['proposals_approved'],
            'rejected': self.state['proposals_rejected'],
            'modified': self.state['proposals_modified'],
            'avg_confidence': round(self.state['avg_confidence'], 2),
            'thresholds': {
                'min_confidence': MIN_CONFIDENCE,
                'risk_limit': RISK_LIMIT
            }
        }


import time

def main():
    governor = CSMRGovernor()
    
    import sys
    
    if len(sys.argv) == 1:
        print(json.dumps(governor.get_status(), indent=2))
    
    elif sys.argv[1] == '--govern':
        status = sys.argv[2] if len(sys.argv) > 2 else 'validated_gate_a'
        result = governor.govern_proposals(status)
        print(json.dumps(result, indent=2))
    
    elif sys.argv[1] == '--eval' and len(sys.argv) > 2:
        # Evaluate a specific proposal
        proposal_id = sys.argv[2]
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('SELECT * FROM modification_proposals WHERE proposal_id = ?', (proposal_id,))
        row = cur.fetchone()
        conn.close()
        
        if row:
            result = governor.evaluate_proposal(dict(row))
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps({'error': 'Proposal not found'}))
    
    else:
        print('Usage: csrm_governor.py [--govern [status]] [--eval proposal_id]')


if __name__ == '__main__':
    main()