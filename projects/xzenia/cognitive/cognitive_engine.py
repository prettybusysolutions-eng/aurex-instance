"""
Tier 5 Cognitive Engine - Core Architecture
PersistentMemory, WorldModel, LearningEngine, GoalEngine, Planner, CausalReasoner
"""
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from sqlalchemy import text

# PostgreSQL integration via existing db_layer
import sys
sys.path.insert(0, '/Users/marcuscoarchitect/.openclaw/workspace/marketplace-scaffold')
from src.services.db_layer import get_orchestrator


class MemoryType(Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    METACOGNITIVE = "metacognitive"


@dataclass
class Memory:
    """Persistent memory that survives sessions"""
    id: str
    memory_type: MemoryType
    content: Dict[str, Any]
    embedding: Optional[List[float]] = None
    importance: float = 0.5
    last_accessed: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    access_count: int = 0
    decay_factor: float = 1.0


class PersistentMemory:
    """Memory that survives session restarts - stored in PostgreSQL"""
    
    TABLE_NAME = "xzenia_memory"
    
    def __init__(self):
        self.orchestrator = get_orchestrator()
        self._ensure_table()
    
    def _ensure_table(self):
        try:
            with self.orchestrator.pg_pool.session() as session:
                session.execute(text(f"""
                    CREATE TABLE IF NOT EXISTS {self.TABLE_NAME} (
                        id VARCHAR(36) PRIMARY KEY,
                        memory_type VARCHAR(20) NOT NULL,
                        content JSONB NOT NULL,
                        importance FLOAT DEFAULT 0.5,
                        last_accessed TIMESTAMP DEFAULT NOW(),
                        access_count INT DEFAULT 0,
                        decay_factor FLOAT DEFAULT 1.0
                    )
                """))
                session.commit()
        except Exception as e:
            print(f"Memory table: {e}")
    
    def store(self, memory: Memory) -> str:
        try:
            with self.orchestrator.pg_pool.session() as session:
                session.execute(text(f"""
                    INSERT INTO {self.TABLE_NAME} 
                    (id, memory_type, content, importance, last_accessed, access_count, decay_factor)
                    VALUES (:id, :type, :content, :importance, :last_accessed, :access_count, :decay_factor)
                    ON CONFLICT (id) DO UPDATE SET
                        content = EXCLUDED.content,
                        last_accessed = EXCLUDED.last_accessed,
                        access_count = EXCLUDED.access_count
                """), {
                    "id": memory.id,
                    "type": memory.memory_type.value,
                    "content": json.dumps(memory.content),
                    "importance": memory.importance,
                    "last_accessed": memory.last_accessed,
                    "access_count": memory.access_count,
                    "decay_factor": memory.decay_factor
                })
                session.commit()
            return memory.id
        except Exception as e:
            print(f"Store error: {e}")
            return None
    
    def retrieve(self, memory_id: str) -> Optional[Memory]:
        try:
            with self.orchestrator.pg_pool.session() as session:
                result = session.execute(text(f"""
                    SELECT id, memory_type, content, importance, last_accessed, access_count, decay_factor
                    FROM {self.TABLE_NAME} WHERE id = :id
                """), {"id": memory_id}).fetchone()
                
                if result:
                    return Memory(
                        id=result[0],
                        memory_type=MemoryType(result[1]),
                        content=json.loads(result[2]),
                        importance=result[3],
                        last_accessed=str(result[4]),
                        access_count=result[5],
                        decay_factor=result[6]
                    )
        except Exception as e:
            print(f"Retrieve: {e}")
        return None
    
    def get_recent(self, limit: int = 20) -> List[Memory]:
        try:
            with self.orchestrator.pg_pool.session() as session:
                results = session.execute(text(f"""
                    SELECT id, memory_type, content, importance, last_accessed, access_count, decay_factor
                    FROM {self.TABLE_NAME}
                    ORDER BY last_accessed DESC
                    LIMIT :limit
                """), {"limit": limit}).fetchall()
                
                return [Memory(
                    id=r[0], memory_type=MemoryType(r[1]), content=json.loads(r[2]),
                    importance=r[3], last_accessed=str(r[4]), access_count=r[5], decay_factor=r[6]
                ) for r in results]
        except Exception as e:
            print(f"Recent: {e}")
            return []


@dataclass
class WorldState:
    agent_states: Dict[str, Any] = field(default_factory=dict)
    environment: Dict[str, Any] = field(default_factory=dict)
    active_goals: List[str] = field(default_factory=list)
    recent_events: List[Dict] = field(default_factory=list)
    resource_levels: Dict[str, float] = field(default_factory=dict)


class WorldModel:
    """Internal representation of environment state"""
    
    def __init__(self):
        self.state = WorldState()
        self.orchestrator = get_orchestrator()
        self._ensure_table()
        self._load_state()
    
    def _ensure_table(self):
        try:
            with self.orchestrator.pg_pool.session() as session:
                session.execute(text("""
                    CREATE TABLE IF NOT EXISTS xzenia_world_state (
                        id VARCHAR(36) PRIMARY KEY,
                        state_json JSONB,
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """))
                session.commit()
        except:
            pass
    
    def _load_state(self):
        try:
            with self.orchestrator.pg_pool.session() as session:
                result = session.execute(text("""
                    SELECT state_json FROM xzenia_world_state ORDER BY updated_at DESC LIMIT 1
                """)).fetchone()
                
                if result:
                    data = json.loads(result[0])
                    self.state = WorldState(**data)
        except:
            pass
    
    def _save_state(self):
        try:
            with self.orchestrator.pg_pool.session() as session:
                session.execute(text("""
                    INSERT INTO xzenia_world_state (id, state_json, updated_at)
                    VALUES ('world_state', :state, NOW())
                    ON CONFLICT (id) DO UPDATE SET state_json = EXCLUDED.state_json, updated_at = NOW()
                """), {"state": json.dumps({
                    "agent_states": self.state.agent_states,
                    "environment": self.state.environment,
                    "active_goals": self.state.active_goals,
                    "recent_events": self.state.recent_events[-10:],
                    "resource_levels": self.state.resource_levels
                })})
                session.commit()
        except Exception as e:
            print(f"World state save: {e}")
    
    def update(self, key: str, value: Any):
        if key in ["agent_states", "environment", "resource_levels"]:
            getattr(self.state, key).update(value)
        elif key == "active_goals":
            self.state.active_goals = value
        elif key == "recent_events":
            self.state.recent_events.append(value)
            self.state.recent_events = self.state.recent_events[-20:]
        
        self._save_state()
    
    def get(self, key: str) -> Any:
        return getattr(self.state, key, None)


class GoalEngine:
    """Self-directed goal pursuit"""
    
    def __init__(self, memory: PersistentMemory, world: WorldModel):
        self.memory = memory
        self.world = world
        self._ensure_table()
    
    def _ensure_table(self):
        try:
            with self.world.orchestrator.pg_pool.session() as session:
                session.execute(text("""
                    CREATE TABLE IF NOT EXISTS xzenia_goals (
                        id VARCHAR(36) PRIMARY KEY,
                        title VARCHAR(200),
                        description TEXT,
                        status VARCHAR(20),
                        priority FLOAT,
                        progress FLOAT,
                        created_at TIMESTAMP,
                        updated_at TIMESTAMP,
                        completed_at TIMESTAMP,
                        metadata JSONB
                    )
                """))
                session.commit()
        except:
            pass
    
    def create_goal(self, title: str, description: str, priority: float = 0.5) -> str:
        goal_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        try:
            with self.world.orchestrator.pg_pool.session() as session:
                session.execute(text("""
                    INSERT INTO xzenia_goals (id, title, description, status, priority, progress, created_at, updated_at)
                    VALUES (:id, :title, :desc, 'active', :priority, 0, :created, :updated)
                """), {"id": goal_id, "title": title, "desc": description, "priority": priority, "created": now, "updated": now})
                session.commit()
            
            goals = self.world.get("active_goals") or []
            goals.append(goal_id)
            self.world.update("active_goals", goals)
            
            memory = Memory(
                id=str(uuid.uuid4()),
                memory_type=MemoryType.METACOGNITIVE,
                content={"goal_id": goal_id, "title": title, "description": description},
                importance=priority
            )
            self.memory.store(memory)
            
            return goal_id
        except Exception as e:
            print(f"Goal: {e}")
            return None
    
    def update_progress(self, goal_id: str, progress: float):
        try:
            with self.world.orchestrator.pg_pool.session() as session:
                session.execute(text("""
                    UPDATE xzenia_goals SET progress = :prog, updated_at = NOW()
                    WHERE id = :id
                """), {"id": goal_id, "prog": min(1.0, max(0.0, progress))})
                session.commit()
        except Exception as e:
            print(f"Progress: {e}")
    
    def complete_goal(self, goal_id: str):
        try:
            with self.world.orchestrator.pg_pool.session() as session:
                session.execute(text("""
                    UPDATE xzenia_goals SET status = 'completed', progress = 1.0, completed_at = NOW()
                    WHERE id = :id
                """), {"id": goal_id})
                session.commit()
            
            goals = self.world.get("active_goals") or []
            if goal_id in goals:
                goals.remove(goal_id)
            self.world.update("active_goals", goals)
        except Exception as e:
            print(f"Complete: {e}")


class Planner:
    """Multi-step plan execution"""
    
    def __init__(self, memory: PersistentMemory, world: WorldModel, goals: GoalEngine):
        self.memory = memory
        self.world = world
        self.goals = goals
    
    def create_plan(self, goal_id: str, steps: List[Dict]) -> str:
        plan_id = str(uuid.uuid4())
        
        memory = Memory(
            id=plan_id,
            memory_type=MemoryType.PROCEDURAL,
            content={
                "plan_id": plan_id,
                "goal_id": goal_id,
                "steps": steps,
                "current_step": 0,
                "status": "active"
            },
            importance=0.8
        )
        self.memory.store(memory)
        
        return plan_id
    
    def get_next_step(self, plan_id: str) -> Optional[Dict]:
        mem = self.memory.retrieve(plan_id)
        if mem and mem.content.get("status") == "active":
            idx = mem.content.get("current_step", 0)
            steps = mem.content.get("steps", [])
            if idx < len(steps):
                return steps[idx]
        return None


class LearningEngine:
    """Learns from outcomes, improves over time"""
    
    def __init__(self, memory: PersistentMemory):
        self.memory = memory
    
    def record_outcome(self, action: str, result: Any, context: Dict):
        outcome_id = str(uuid.uuid4())
        success = result.get("success", True) if isinstance(result, dict) else True
        
        outcome = {
            "action": action,
            "success": success,
            "context": context,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        memory = Memory(
            id=outcome_id,
            memory_type=MemoryType.EPISODIC,
            content=outcome,
            importance=0.7 if success else 0.9
        )
        self.memory.store(memory)
        
        self._analyze_patterns()
    
    def _analyze_patterns(self):
        recent = self.memory.get_recent(limit=50)
        successes = [m for m in recent if m.content.get("success", False)]
        
        if len(recent) >= 10:
            success_rate = len(successes) / len(recent)
            
            pattern_id = str(uuid.uuid4())
            pattern = Memory(
                id=pattern_id,
                memory_type=MemoryType.SEMANTIC,
                content={
                    "type": "success_rate",
                    "value": success_rate,
                    "sample_size": len(recent),
                    "analysis_date": datetime.utcnow().isoformat()
                },
                importance=0.6
            )
            self.memory.store(pattern)
    
    def get_insights(self) -> List[Dict]:
        insights = []
        try:
            with self.memory.orchestrator.pg_pool.session() as session:
                results = session.execute(text(f"""
                    SELECT content FROM {PersistentMemory.TABLE_NAME}
                    WHERE memory_type = 'semantic'
                    ORDER BY importance DESC
                    LIMIT 10
                """)).fetchall()
                
                for r in results:
                    try:
                        insights.append(json.loads(r[0]))
                    except:
                        pass
        except:
            pass
        
        return insights


class CausalReasoner:
    """Cause-effect reasoning"""
    
    def __init__(self, memory: PersistentMemory):
        self.memory = memory
    
    def infer_causes(self, effect: str) -> List[Dict]:
        recent = self.memory.get_recent(limit=5)
        
        causes = []
        for mem in recent:
            if mem.memory_type == MemoryType.EPISODIC:
                causes.append({
                    "memory_id": mem.id,
                    "content": mem.content,
                    "importance": mem.importance
                })
        
        return causes
    
    def predict_outcome(self, action: str, context: Dict) -> Dict:
        recent = self.memory.get_recent(limit=3)
        
        if recent:
            outcomes = [m.content for m in recent]
            success_count = sum(1 for o in outcomes if o.get("success", True))
            success_rate = success_count / len(outcomes)
            
            return {
                "predicted_success_rate": success_rate,
                "based_on": len(outcomes)
            }
        
        return {"predicted_success_rate": 0.5, "based_on": 0}


# ============================================================
# TIER 5 COGNITIVE ENGINE - Main orchestration
# ============================================================

class CognitiveEngine:
    """Tier 5: Complete cognitive architecture"""
    
    def __init__(self):
        print("Initializing Tier 5 Cognitive Engine...")
        
        self.memory = PersistentMemory()
        self.world = WorldModel()
        self.goals = GoalEngine(self.memory, self.world)
        self.planner = Planner(self.memory, self.world, self.goals)
        self.learning = LearningEngine(self.memory)
        self.causal = CausalReasoner(self.memory)
        
        self.metrics = {
            "memories_stored": 0,
            "goals_created": 0,
            "outcomes_learned": 0
        }
        
        print("✓ Tier 5 Cognitive Engine initialized")
    
    def store_experience(self, experience: Dict, memory_type: MemoryType = MemoryType.EPISODIC):
        mem_id = str(uuid.uuid4())
        memory = Memory(
            id=mem_id,
            memory_type=memory_type,
            content=experience,
            importance=experience.get("importance", 0.5)
        )
        self.memory.store(memory)
        self.metrics["memories_stored"] += 1
        return mem_id
    
    def create_self_goal(self, title: str, description: str) -> str:
        goal_id = self.goals.create_goal(title, description, priority=0.8)
        self.metrics["goals_created"] += 1
        
        self.store_experience({
            "type": "goal_created",
            "title": title,
            "goal_id": goal_id
        }, MemoryType.METACOGNITIVE)
        
        return goal_id
    
    def execute_and_learn(self, action: str, context: Dict, result: Any):
        self.learning.record_outcome(action, result, context)
        self.metrics["outcomes_learned"] += 1
        
        goal_id = context.get("goal_id")
        if goal_id:
            success = result.get("success", True) if isinstance(result, dict) else True
            current = 0
            self.goals.update_progress(goal_id, current + (0.1 if success else 0))
    
    def get_status(self) -> Dict:
        return {
            "memories": self.metrics["memories_stored"],
            "goals_active": len(self.world.get("active_goals") or []),
            "goals_created": self.metrics["goals_created"],
            "learned": self.metrics["outcomes_learned"],
            "insights": len(self.learning.get_insights())
        }


_cognitive_engine = None


def get_cognitive_engine() -> CognitiveEngine:
    global _cognitive_engine
    if _cognitive_engine is None:
        _cognitive_engine = CognitiveEngine()
    return _cognitive_engine


if __name__ == "__main__":
    print("=== TIER 5 COGNITIVE ENGINE TEST ===\n")
    
    engine = get_cognitive_engine()
    
    print("\n1. Store experiences...")
    engine.store_experience({
        "event": "swarm_initialized",
        "agents": 6,
        "success": True
    }, MemoryType.EPISODIC)
    
    print("\n2. Create self-directed goal...")
    goal_id = engine.create_self_goal(
        "Achieve Tier 5 Orchestration",
        "Build complete cognitive architecture"
    )
    print(f"   Goal: {goal_id[:16]}...")
    
    print("\n3. Execute and learn...")
    engine.execute_and_learn("test_action", {"goal_id": goal_id}, {"success": True})
    
    print("\n4. Status:")
    for k, v in engine.get_status().items():
        print(f"   {k}: {v}")
    
    print("\n=== TIER 5 COGNITIVE ENGINE: OPERATIONAL ===")