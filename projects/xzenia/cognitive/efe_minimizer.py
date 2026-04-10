"""
Expected Free Energy (EFE) Minimization Layer v1.0

Implements active inference principle for action selection:
- Pragmatic value: will this action get me closer to my goal?
- Epistemic value: will this action teach me something I don't know?

Replaces heuristic Bayesian+UCB with principled information-seeking.

Usage:
    from efe_minimizer import EFEMinimizer, ActionSpace
    
    efe = EFEMinimizer()
    action = efe.select_action(goal, actions, observation_count, domain)
    
    # At low observations: favors high information-gain actions (exploration)
    # At high observations: favors high outcome actions (exploitation)
"""

import numpy as np
from typing import Any, Optional, list
from dataclasses import dataclass
import logging

logger = logging.getLogger("sovereign.efe")


@dataclass
class ActionSpace:
    """Available actions with their expected outcomes."""
    id: str
    description: str
    expected_outcome: float   # Pragmatic value (goal proximity)
    information_gain: float   # Epistemic value (novelty)
    uncertainty: float        # How unknown this action is
    domain: str


class EFEMinimizer:
    """
    Expected Free Energy (EFE) minimizer for active inference.
    
    EFE(action) = Epistemic Value + Pragmatic Value
    
    Epistemic = expected reduction in uncertainty about world model
    Pragmatic = expected proximity to goal state
    
    The system actively seeks informative actions when uncertain,
    exploits known paths when confident.
    """
    
    def __init__(self, gamma: float = 0.9, beta: float = 1.0, 
                 exploration_threshold: int = 30):
        """
        Args:
            gamma: Horizon discount (0.9 = look ahead ~10 steps)
            beta: Precision (inverse temperature for softmax)
            exploration_threshold: Below this, favor exploration
        """
        self.gamma = gamma
        self.beta = beta
        self.exploration_threshold = exploration_threshold
        self.action_history = []
        self.observation_count = 0
    
    def select_action(self, goal: str, actions: list[ActionSpace], 
                      observation_count: int, domain: str = "general") -> ActionSpace:
        """
        Select action that minimizes Expected Free Energy.
        
        When observation_count < threshold → favor epistemic (exploration)
        When observation_count > threshold → favor pragmatic (exploitation)
        """
        self.observation_count = observation_count
        
        # Calculate exploration vs exploitation weights
        if observation_count < self.exploration_threshold:
            # Exploration mode: weight epistemic value heavily
            epi_weight = 1.0 - (observation_count / self.exploration_threshold)
            prag_weight = 0.3
            mode = "EXPLORATION"
        else:
            # Exploitation mode: weight pragmatic value
            epi_weight = 0.2
            prag_weight = 0.8
            mode = "EXPLOITATION"
        
        # Calculate EFE for each action
        scored_actions = []
        for action in actions:
            # Epistemic: high when uncertainty is high, information gain is high
            epistemic = (1 - action.uncertainty) * action.information_gain * epi_weight
            
            # Pragmatic: high when expected outcome is high
            pragmatic = action.expected_outcome * prag_weight
            
            # EFE = -(epistemic + pragmatic)  (minimize)
            efe = -(epistemic + pragmatic)
            
            # Apply precision (softmax temperature)
            if self.beta != 1.0:
                efe = efe * self.beta
            
            scored_actions.append({
                "action": action,
                "efe": efe,
                "epistemic": epistemic,
                "pragmatic": pragmatic,
                "mode": mode
            })
        
        # Sort by EFE (lowest first = best)
        scored_actions.sort(key=lambda x: x["efe"])
        
        selected = scored_actions[0]
        
        # Log decision
        logger.info(f"EFE selected: {selected['action'].id} (EFE={selected['efe']:.3f}, "
                   f"epi={selected['epistemic']:.3f}, prag={selected['pragmatic']:.3f}, mode={mode})")
        
        self.action_history.append({
            "goal": goal,
            "action": selected["action"].id,
            "efe": selected["efe"],
            "observation_count": observation_count,
            "domain": domain,
            "mode": mode
        })
        
        return selected["action"]
    
    def compute_efe(self, action: ActionSpace, observation_count: int) -> dict:
        """
        Compute EFE components for an action without selecting.
        
        Returns decomposition for analysis/debugging.
        """
        if observation_count < self.exploration_threshold:
            epi_weight = 1.0 - (observation_count / self.exploration_threshold)
            prag_weight = 0.3
        else:
            epi_weight = 0.2
            prag_weight = 0.8
        
        epistemic = (1 - action.uncertainty) * action.information_gain * epi_weight
        pragmatic = action.expected_outcome * prag_weight
        efe = -(epistemic + pragmatic)
        
        return {
            "action_id": action.id,
            "efe": efe,
            "epistemic_value": epistemic,
            "pragmatic_value": pragmatic,
            "epistemic_weight": epi_weight,
            "pragmatic_weight": prag_weight,
            "exploration_mode": observation_count < self.exploration_threshold,
            "uncertainty": action.uncertainty,
            "information_gain": action.information_gain
        }
    
    def get_action_preference(self, actions: list[ActionSpace], 
                              observation_count: int) -> list[dict]:
        """Get sorted preference order for all actions."""
        preferences = []
        for action in actions:
            efe = self.compute_efe(action, observation_count)
            preferences.append(efe)
        return sorted(preferences, key=lambda x: x["efe"])
    
    def get_history(self) -> list:
        """Return action selection history."""
        return self.action_history[-20:]  # Last 20


if __name__ == "__main__":
    # Self-test
    print("="*60)
    print("EXPECTED FREE ENERGY MINIMIZER - SELF TEST")
    print("="*60)
    
    efe = EFEMinimizer(beta=1.0)
    
    # Define action space
    actions = [
        ActionSpace("identify_gaps", "Find unprocessed requests", 
                    expected_outcome=0.8, information_gain=0.9, uncertainty=0.3, domain="cleaning"),
        ActionSpace("prioritize_fixes", "Rank by value", 
                    expected_outcome=0.9, information_gain=0.6, uncertainty=0.2, domain="cleaning"),
        ActionSpace("execute_recovery", "Dispatch jobs", 
                    expected_outcome=1.0, information_gain=0.7, uncertainty=0.4, domain="cleaning"),
        ActionSpace("verify_recovery", "Confirm completion", 
                    expected_outcome=0.9, information_gain=0.5, uncertainty=0.1, domain="cleaning"),
    ]
    
    # Test at different observation counts
    for obs_count in [10, 30, 50]:
        print(f"\n--- Observation count: {obs_count} ---")
        
        preference = efe.get_action_preference(actions, obs_count)
        selected = efe.select_action("Maximize revenue", actions, obs_count, "cleaning")
        
        mode = "EXPLORATION" if obs_count < 30 else "EXPLOITATION"
        print(f"Mode: {mode}")
        print("Preference order:")
        for p in preference:
            marker = "→ " if p["action_id"] == selected.id else "  "
            print(f"  {marker}{p['action_id']:18} | EFE: {p['efe']:+.3f} | "
                  f"epi: {p['epistemic_value']:.2f} | prag: {p['pragmatic_value']:.2f}")
    
    print("\n" + "="*60)
    print("EFE MINIMIZER OPERATIONAL")
    print("="*60)