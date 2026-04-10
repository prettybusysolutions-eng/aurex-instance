"""
Tier 5.1 - Goal Pursuit Engine
Autonomous goal working, not just goal creation
"""
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy import text
import sys
sys.path.insert(0, '/Users/marcuscoarchitect/.openclaw/workspace/marketplace-scaffold')
from src.services.db_layer import get_orchestrator


class GoalPursuitEngine:
    """
    ACTIVE goal pursuit - not just creation
    This is what was missing: goals exist but aren't being worked on
    """
    
    def __init__(self):
        self.orchestrator = get_orchestrator()
        self._ensure_tables()
        self.active_workers = {}  # goal_id -> worker info
        
    def _ensure_tables(self):
        with self.orchestrator.pg_pool.session() as session:
            # Goal work tracking
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS xzenia_goal_work (
                    id VARCHAR(36) PRIMARY KEY,
                    goal_id VARCHAR(36) NOT NULL,
                    action_type VARCHAR(50),
                    action_detail TEXT,
                    status VARCHAR(20),
                    result JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    completed_at TIMESTAMP
                )
            """))
            
            # Goal milestones
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS xzenia_goal_milestones (
                    id VARCHAR(36) PRIMARY KEY,
                    goal_id VARCHAR(36) NOT NULL,
                    milestone VARCHAR(200),
                    status VARCHAR(20) DEFAULT 'pending',
                    completed_at TIMESTAMP
                )
            """))
            session.commit()
    
    def start_pursuing(self, goal_id: str, initial_actions: List[Dict]):
        """Begin actively working on a goal"""
        worker_id = str(uuid.uuid4())
        
        # Queue first actions
        for i, action in enumerate(initial_actions):
            work_id = str(uuid.uuid4())
            with self.orchestrator.pg_pool.session() as session:
                session.execute(text("""
                    INSERT INTO xzenia_goal_work (id, goal_id, action_type, action_detail, status)
                    VALUES (:id, :goal_id, :type, :detail, 'pending')
                """), {
                    "id": work_id,
                    "goal_id": goal_id,
                    "type": action.get("type", "generic"),
                    "detail": json.dumps(action)
                })
                session.commit()
        
        self.active_workers[goal_id] = {
            "started": datetime.utcnow().isoformat(),
            "actions_queued": len(initial_actions)
        }
        
        return worker_id
    
    def execute_action(self, work_id: str, result: Any):
        """Record result of a goal action"""
        with self.orchestrator.pg_pool.session() as session:
            session.execute(text("""
                UPDATE xzenia_goal_work 
                SET status = 'completed', result = :result, completed_at = NOW()
                WHERE id = :id
            """), {"id": work_id, "result": json.dumps(result)})
            session.commit()
    
    def get_pending_work(self, goal_id: str) -> List[Dict]:
        """Get next actions for goal"""
        with self.orchestrator.pg_pool.session() as session:
            results = session.execute(text("""
                SELECT id, action_type, action_detail FROM xzenia_goal_work
                WHERE goal_id = :goal_id AND status = 'pending'
                ORDER BY created_at LIMIT 5
            """), {"goal_id": goal_id}).fetchall()
            
            return [{"id": r[0], "type": r[1], "detail": json.loads(r[2])} for r in results]
    
    def get_goal_progress(self, goal_id: str) -> Dict:
        """Calculate actual progress"""
        with self.orchestrator.pg_pool.session() as session:
            total = session.execute(text("""
                SELECT COUNT(*) FROM xzenia_goal_work WHERE goal_id = :id
            """), {"id": goal_id}).fetchone()[0]
            
            done = session.execute(text("""
                SELECT COUNT(*) FROM xzenia_goal_work WHERE goal_id = :id AND status = 'completed'
            """), {"id": goal_id}).fetchone()[0]
            
            return {
                "total_actions": total,
                "completed": done,
                "progress": done / total if total > 0 else 0
            }


class AdaptiveLearningEngine:
    """
    Actually learns and adjusts behavior - not just recording
    """
    
    def __init__(self):
        self.orchestrator = get_orchestrator()
        self.behavior_weights = {}  # action -> weight adjustment
        self._load_behavior_model()
        
    def _load_behavior_model(self):
        """Load learned behavior adjustments"""
        try:
            with self.orchestrator.pg_pool.session() as session:
                result = session.execute(text("""
                    SELECT behavior_key, weight_adjustment FROM xzenia_behavior_model
                """)).fetchall()
                
                for r in result:
                    self.behavior_weights[r[0]] = r[1]
        except:
            pass
    
    def _ensure_tables(self):
        with self.orchestrator.pg_pool.session() as session:
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS xzenia_behavior_model (
                    behavior_key VARCHAR(100) PRIMARY KEY,
                    weight_adjustment FLOAT,
                    success_count INT,
                    failure_count INT,
                    last_updated TIMESTAMP
                )
            """))
            session.commit()
    
    def learn(self, action: str, outcome: Dict):
        """Actually adjust behavior based on outcome"""
        success = outcome.get("success", True)
        
        # Update behavior model
        if action not in self.behavior_weights:
            self.behavior_weights[action] = 1.0
        
        # Adjust weight
        if success:
            self.behavior_weights[action] = min(2.0, self.behavior_weights[action] * 1.1)
        else:
            self.behavior_weights[action] = max(0.3, self.behavior_weights[action] * 0.8)
        
        # Persist
        try:
            with self.orchestrator.pg_pool.session() as session:
                session.execute(text("""
                    INSERT INTO xzenia_behavior_model (behavior_key, weight_adjustment, success_count, last_updated)
                    VALUES (:key, :weight, 1, NOW())
                    ON CONFLICT (behavior_key) DO UPDATE SET
                        weight_adjustment = EXCLUDED.weight_adjustment,
                        last_updated = NOW()
                """), {"key": action, "weight": self.behavior_weights[action]})
                session.commit()
        except:
            pass
    
    def get_recommended_action(self, context: str) -> Optional[str]:
        """Get best action for context based on learning"""
        # Find actions for this context
        matching = {k: v for k, v in self.behavior_weights.items() if context in k}
        
        if matching:
            return max(matching.items(), key=lambda x: x[1])[0]
        return None


class CausalInferenceEngine:
    """
    Infers new causes from observed correlations
    """
    
    def __init__(self):
        self.orchestrator = get_orchestrator()
        self._ensure_tables()
        
    def _ensure_tables(self):
        with self.orchestrator.pg_pool.session() as session:
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS xzenia_causal_inferences (
                    id VARCHAR(36) PRIMARY KEY,
                    cause VARCHAR(200),
                    effect VARCHAR(200),
                    confidence FLOAT,
                    evidence_count INT,
                    inferred_at TIMESTAMP DEFAULT NOW()
                )
            """))
            session.commit()
    
    def infer(self, observations: List[Dict]) -> List[Dict]:
        """Infer new causal relationships from patterns"""
        # Simple correlation detection
        cause_effect_pairs = {}
        
        for obs in observations:
            cause = obs.get("cause")
            effect = obs.get("effect")
            if cause and effect:
                key = f"{cause}|{effect}"
                cause_effect_pairs[key] = cause_effect_pairs.get(key, 0) + 1
        
        # Infer high-frequency patterns
        inferences = []
        for pair, count in cause_effect_pairs.items():
            if count >= 2:  # At least 2 observations
                cause, effect = pair.split("|")
                confidence = min(1.0, count / 5.0)
                
                inf_id = str(uuid.uuid4())
                with self.orchestrator.pg_pool.session() as session:
                    session.execute(text("""
                        INSERT INTO xzenia_causal_inferences (id, cause, effect, confidence, evidence_count)
                        VALUES (:id, :cause, :effect, :conf, :count)
                    """), {
                        "id": inf_id, "cause": cause, "effect": effect, 
                        "conf": confidence, "count": count
                    })
                    session.commit()
                
                inferences.append({
                    "cause": cause, "effect": effect, 
                    "confidence": confidence, "evidence": count
                })
        
        return inferences
    
    def get_inferences(self) -> List[Dict]:
        with self.orchestrator.pg_pool.session() as session:
            results = session.execute(text("""
                SELECT cause, effect, confidence, evidence_count FROM xzenia_causal_inferences
                ORDER BY confidence DESC LIMIT 10
            """)).fetchall()
            
            return [{"cause": r[0], "effect": r[1], "confidence": r[2], "evidence": r[3]} for r in results]


# ============================================================
# UPDATED TIER 5 COGNITIVE ENGINE
# ============================================================

class CognitiveEngineV5_1:
    """Tier 5.1 - With active goal pursuit and adaptive learning"""
    
    def __init__(self):
        print("Initializing Tier 5.1 Cognitive Engine...")
        
        # Original components
        from projects.xzenia.cognitive.cognitive_engine import (
            PersistentMemory, WorldModel, GoalEngine, Planner, LearningEngine, CausalReasoner
        )
        
        self.memory = PersistentMemory()
        self.world = WorldModel()
        self.goals = GoalEngine(self.memory, self.world)
        self.planner = Planner(self.memory, self.world, self.goals)
        self.learning = LearningEngine(self.memory)
        self.causal = CausalReasoner(self.memory)
        
        # NEW: Active pursuit components
        self.pursuit = GoalPursuitEngine()
        self.adaptive = AdaptiveLearningEngine()
        self.causal_infer = CausalInferenceEngine()
        
        self.metrics = {
            "goals_pursued": 0,
            "behaviors_adjusted": 0,
            "inferences_made": 0
        }
        
        print("✓ Tier 5.1 Cognitive Engine initialized")
    
    def pursue_goal(self, goal_id: str, actions: List[Dict]):
        """Actively work on a goal"""
        self.pursuit.start_pursuing(goal_id, actions)
        self.metrics["goals_pursued"] += 1
        
        # Update world state
        events = self.world.get("recent_events") or []
        events.append({"type": "goal_pursuit", "goal_id": goal_id, "actions": len(actions)})
        self.world.update("recent_events", {"events": events})
    
    def record_outcome_with_learning(self, action: str, context: Dict, result: Any):
        """Record outcome AND adjust behavior"""
        # Original recording
        self.learning.record_outcome(action, result, context)
        
        # NEW: Adaptive learning
        self.adaptive.learn(action, result if isinstance(result, dict) else {"success": result})
        self.metrics["behaviors_adjusted"] += 1
    
    def infer_causes(self, observations: List[Dict]) -> List[Dict]:
        """Infer new causal relationships"""
        inferences = self.causal_infer.infer(observations)
        self.metrics["inferences_made"] += len(inferences)
        return inferences
    
    def get_status(self) -> Dict:
        return {
            "pursuing": self.metrics["goals_pursued"],
            "adaptive": self.metrics["behaviors_adjusted"],
            "inferences": self.metrics["inferences_made"],
            "active_pursuits": len(self.pursuit.active_workers)
        }


# Singleton
_cognitive_engine_v5_1 = None


def get_cognitive_engine_v5_1() -> CognitiveEngineV5_1:
    global _cognitive_engine_v5_1
    if _cognitive_engine_v5_1 is None:
        _cognitive_engine_v5_1 = CognitiveEngineV5_1()
    return _cognitive_engine_v5_1


if __name__ == "__main__":
    print("=== TIER 5.1 - ACTIVE PURSUIT TEST ===\n")
    
    engine = get_cognitive_engine_v5_1()
    
    # Test active goal pursuit
    print("1. Testing goal pursuit...")
    from projects.xzenia.cognitive.cognitive_engine import get_cognitive_engine
    base = get_cognitive_engine()
    goals = base.world.get("active_goals") or []
    
    if goals:
        engine.pursue_goal(goals[0], [
            {"type": "analyze", "detail": "Check current state"},
            {"type": "execute", "detail": "Take next step"},
            {"type": "verify", "detail": "Confirm result"}
        ])
        print(f"   Pursuing: {goals[0][:16]}...")
    
    # Test adaptive learning
    print("\n2. Testing adaptive learning...")
    engine.record_outcome_with_learning("test_action", {"context": "testing"}, {"success": True})
    engine.record_outcome_with_learning("test_action", {"context": "testing"}, {"success": False})
    
    print(f"   Behavior weights: {engine.adaptive.behavior_weights}")
    
    # Test causal inference
    print("\n3. Testing causal inference...")
    observations = [
        {"cause": "goal_created", "effect": "pursuit_started"},
        {"cause": "goal_created", "effect": "pursuit_started"},
        {"cause": "action_executed", "effect": "result_recorded"}
    ]
    inferences = engine.infer_causes(observations)
    print(f"   Inferences: {len(inferences)}")
    for inf in inferences:
        print(f"     {inf['cause']} → {inf['effect']} ({inf['confidence']:.1f})")
    
    # Status
    print("\n4. Status:")
    for k, v in engine.get_status().items():
        print(f"   {k}: {v}")
    
    print("\n=== TIER 5.1 OPERATIONAL ===")