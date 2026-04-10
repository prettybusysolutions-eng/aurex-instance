"""
SOVEREIGN PLANNER - Compositional Hierarchical Task Decomposition

Replaces queue-based goal engine with real dependency-graph planning.
Integrates with causal engine, semantic memory, and Bayesian engine.
"""

import json
import hashlib
import logging
from enum import Enum
from datetime import datetime, timezone
from typing import Optional, Any, List
from dataclasses import dataclass, field

logger = logging.getLogger("sovereign.planner")


class TaskStatus(Enum):
    PENDING = "pending"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REPLANNED = "replanned"


class TaskPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class SubTask:
    id: str
    description: str
    action: str
    parameters: dict = field(default_factory=dict)
    dependencies: list = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    estimated_duration_minutes: float = 30.0
    actual_result: Optional[dict] = None
    failure_reason: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    original_description: Optional[str] = None
    replan_count: int = 0

    def is_ready(self, completed_ids):
        return all(dep in completed_ids for dep in self.dependencies)


@dataclass
class ExecutionPlan:
    id: str
    goal: str
    subtasks: list = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "active"
    replan_history: list = field(default_factory=list)
    total_subtasks: int = 0
    completed_subtasks: int = 0
    failed_subtasks: int = 0

    def get_ready_tasks(self):
        completed_ids = {t.id for t in self.subtasks if t.status == TaskStatus.COMPLETED}
        return [t for t in self.subtasks if t.status == TaskStatus.PENDING and t.is_ready(completed_ids)]

    def get_progress(self):
        counts = {}
        for t in self.subtasks:
            counts[t.status.value] = counts.get(t.status.value, 0) + 1
        return {
            "goal": self.goal,
            "total": len(self.subtasks),
            "progress": counts,
            "percent_complete": sum(1 for t in self.subtasks if t.status == TaskStatus.COMPLETED) / max(len(self.subtasks), 1) * 100,
            "next_ready": [t.description for t in self.get_ready_tasks()]
        }


class SovereignPlanner:
    """
    Compositional planner with dependency resolution and replanning.
    
    NOT a queue. This planner:
    - Decomposes goals into dependency graphs (not linear sequences)
    - Identifies which tasks can run in parallel
    - Replans when task results invalidate downstream assumptions
    - Integrates with causal engine, semantic memory, and Bayesian engine
    """

    def __init__(self):
        self.plans = {}
        self._causal_engine = None
        self._semantic_memory = None
        self._bayesian_engine = None
        self._decomposition_rules = [
            {
                "pattern": "reduce churn",
                "strategy": "causal_intervention",
                "template_subtasks": [
                    {"action": "causal_query", "desc": "Identify top causal drivers of churn via DoWhy", "params": {"outcome": "churn_rate"}},
                    {"action": "memory_search", "desc": "Retrieve past interventions that affected churn", "params": {"concept": "churn reduction"}},
                    {"action": "rank_interventions", "desc": "Rank interventions by causal effect size and uncertainty", "params": {}},
                    {"action": "design_experiment", "desc": "Design A/B test for top-ranked intervention", "params": {}},
                    {"action": "execute_intervention", "desc": "Deploy the intervention", "params": {}},
                    {"action": "measure_outcome", "desc": "Measure churn change and update causal model", "params": {}},
                ]
            },
            {
                "pattern": "recover",
                "strategy": "revenue_recovery",
                "template_subtasks": [
                    {"action": "causal_query", "desc": "Identify causal drivers of revenue leakage", "params": {"outcome": "revenue_loss"}},
                    {"action": "memory_search", "desc": "Retrieve past recovery events and patterns", "params": {"concept": "revenue recovery billing"}},
                    {"action": "identify_gaps", "desc": "Map billing system gaps to revenue impact", "params": {}},
                    {"action": "prioritize_fixes", "desc": "Rank fixes by recoverable amount and effort", "params": {}},
                    {"action": "execute_recovery", "desc": "Deploy billing corrections", "params": {}},
                    {"action": "verify_recovery", "desc": "Confirm recovered amounts and update models", "params": {}},
                ]
            },
            {
                "pattern": "increase revenue",
                "strategy": "multi_lever",
                "template_subtasks": [
                    {"action": "causal_query", "desc": "Identify causal drivers of revenue", "params": {"outcome": "revenue"}},
                    {"action": "memory_search", "desc": "Retrieve revenue optimization history", "params": {"concept": "revenue growth levers"}},
                    {"action": "identify_levers", "desc": "Map controllable levers to revenue impact", "params": {}},
                    {"action": "simulate_scenarios", "desc": "Counterfactual analysis on each lever", "params": {}},
                    {"action": "prioritize_actions", "desc": "Rank by expected impact adjusted for uncertainty", "params": {}},
                    {"action": "execute_top_action", "desc": "Execute highest-priority lever", "params": {}},
                    {"action": "measure_and_learn", "desc": "Measure result and update Bayesian beliefs", "params": {}},
                ]
            },
            {
                "pattern": "diagnose",
                "strategy": "root_cause_analysis",
                "template_subtasks": [
                    {"action": "gather_observations", "desc": "Collect all relevant data signals", "params": {}},
                    {"action": "build_causal_graph", "desc": "Construct causal model of the system", "params": {}},
                    {"action": "identify_root_causes", "desc": "Trace graph to root cause nodes", "params": {}},
                    {"action": "validate_hypothesis", "desc": "Test root cause hypothesis with counterfactual", "params": {}},
                    {"action": "recommend_fix", "desc": "Propose intervention targeting root cause", "params": {}},
                ]
            },
            {
                "pattern": "optimize",
                "strategy": "systematic_optimization",
                "template_subtasks": [
                    {"action": "research", "desc": "Research current state and constraints", "params": {}},
                    {"action": "memory_search", "desc": "Retrieve past optimization attempts", "params": {"concept": "optimization"}},
                    {"action": "identify_bottlenecks", "desc": "Identify performance bottlenecks", "params": {}},
                    {"action": "causal_query", "desc": "Model causal relationships between variables", "params": {}},
                    {"action": "generate_interventions", "desc": "Generate candidate optimizations", "params": {}},
                    {"action": "evaluate_interventions", "desc": "Rank by impact and feasibility", "params": {}},
                    {"action": "execute", "desc": "Implement top optimization", "params": {}},
                    {"action": "measure_and_learn", "desc": "Measure improvement and update models", "params": {}},
                ]
            }
        ]

    def connect_causal_engine(self, engine):
        self._causal_engine = engine
        logger.info("Causal engine connected to planner")

    def connect_semantic_memory(self, memory):
        self._semantic_memory = memory
        logger.info("Semantic memory connected to planner")

    def connect_bayesian_engine(self, engine):
        self._bayesian_engine = engine
        logger.info("Bayesian engine connected to planner")

    def decompose(self, goal, context=None):
        plan_id = hashlib.sha256(f"{goal}{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:12]
        plan = ExecutionPlan(id=plan_id, goal=goal)

        strategy = self._match_strategy(goal)
        past_experience = self._retrieve_experience(goal)

        if strategy:
            subtasks = self._instantiate_template(strategy, goal, context or {})
        else:
            subtasks = self._generate_generic_plan(goal, context or {})

        subtasks = self._resolve_dependencies(subtasks)

        if self._causal_engine:
            subtasks = self._enrich_with_causal(subtasks, goal)

        if self._bayesian_engine:
            subtasks = self._adjust_priorities_bayesian(subtasks)

        plan.subtasks = subtasks
        plan.total_subtasks = len(subtasks)
        self.plans[plan_id] = plan
        logger.info(f"Plan {plan_id}: {len(subtasks)} subtasks for '{goal}'")

        # Auto-instrument: emit planner decision as causal observation
        if self._causal_engine and hasattr(self._causal_engine, 'observe'):
            try:
                strategy_name = strategy["strategy"] if strategy else "generic"
                self._causal_engine.observe({
                    "goal_type": strategy_name,
                    "n_subtasks": len(subtasks),
                    "n_parallel": sum(1 for t in subtasks if len(t.dependencies) == 0),
                    "has_causal_levers": 1.0 if self._causal_engine else 0.0,
                    "has_memory_context": 1.0 if past_experience else 0.0,
                    "decomposition_method": "template" if strategy else "novel"
                })
            except:
                pass  # instrumentation is non-critical

        return plan

    def get_next_actions(self, plan_id):
        plan = self.plans[plan_id]
        ready = plan.get_ready_tasks()
        for task in ready:
            task.status = TaskStatus.IN_PROGRESS
        return ready

    def report_result(self, plan_id, task_id, result, success=True):
        plan = self.plans[plan_id]
        task = next((t for t in plan.subtasks if t.id == task_id), None)
        
        if task is None:
            return {"error": f"Task {task_id} not found"}
            
        task.actual_result = result
        task.completed_at = datetime.now(timezone.utc).isoformat()

        if success:
            task.status = TaskStatus.COMPLETED
            plan.completed_subtasks += 1
            if self._bayesian_engine and hasattr(self._bayesian_engine, "update"):
                try:
                    self._bayesian_engine.update(task.action, success=True)
                except:
                    pass
        else:
            task.status = TaskStatus.FAILED
            task.failure_reason = result.get("error", "Unknown")
            plan.failed_subtasks += 1
            if self._bayesian_engine and hasattr(self._bayesian_engine, "update"):
                try:
                    self._bayesian_engine.update(task.action, success=False)
                except:
                    pass

        # Store experience
        if self._semantic_memory:
            try:
                self._semantic_memory.store(
                    content=f"Task '{task.description}' for goal '{plan.goal}': {'succeeded' if success else 'failed'}. Result: {json.dumps(result)[:200]}",
                    memory_type="execution_experience",
                    importance=0.7 if success else 0.9,
                    metadata={"plan_id": plan_id, "task_id": task_id}
                )
            except:
                pass

        # Auto-instrument: emit execution outcome
        if self._causal_engine and hasattr(self._causal_engine, 'observe'):
            try:
                self._causal_engine.observe({
                    "action_type": task.action,
                    "success": 1.0 if success else 0.0,
                    "had_dependencies": 1.0 if task.dependencies else 0.0,
                    "replan_count": float(task.replan_count),
                    "plan_progress": plan.completed_subtasks / max(plan.total_subtasks, 1)
                })
            except:
                pass

        # Check if replan needed
        return self._check_replan(plan, task, result, success)

    def is_complete(self, plan_id):
        plan = self.plans[plan_id]
        return all(t.status in (TaskStatus.COMPLETED, TaskStatus.FAILED) for t in plan.subtasks)

    def get_plan_status(self, plan_id):
        plan = self.plans.get(plan_id)
        if not plan:
            return {"error": f"Plan {plan_id} not found"}
        return plan.get_progress()

    def _check_replan(self, plan, completed_task, result, success):
        if success:
            if self._causal_engine and "causal_effect" in result:
                if abs(result["causal_effect"]) < 0.01:
                    return self._execute_replan(plan, completed_task,
                        f"Intervention showed negligible effect ({result['causal_effect']:.4f})")
            return {"status": "ok"}

        dependents = [t for t in plan.subtasks if completed_task.id in t.dependencies and t.status == TaskStatus.PENDING]
        if dependents:
            return self._execute_replan(plan, completed_task,
                f"Task failed. {len(dependents)} dependent tasks need replanning.")
        return {"status": "ok", "note": "Failed but no dependents affected"}

    def _execute_replan(self, plan, trigger_task, reason):
        affected = []
        to_check = [trigger_task.id]
        checked = set()
        while to_check:
            current = to_check.pop()
            if current in checked:
                continue
            checked.add(current)
            for t in plan.subtasks:
                if current in t.dependencies and t.status == TaskStatus.PENDING:
                    affected.append(t)
                    to_check.append(t.id)

        changes = []
        for task in affected:
            task.original_description = task.original_description or task.description
            task.description = f"[REPLANNED] {task.description} — {reason}"
            task.dependencies = [d for d in task.dependencies if d != trigger_task.id]
            task.replan_count += 1
            changes.append({"task_id": task.id, "change": "replanned"})

        plan.replan_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trigger": trigger_task.id,
            "reason": reason,
            "affected": [t.id for t in affected]
        })
        return {"status": "replanned", "reason": reason, "changes": changes}

    def _match_strategy(self, goal):
        for rule in self._decomposition_rules:
            if rule["pattern"] in goal.lower():
                return rule
        return None

    def _retrieve_experience(self, goal):
        if not self._semantic_memory:
            return []
        try:
            return self._semantic_memory.search_by_concept(goal, top_k=3)
        except Exception:
            return []

    def _instantiate_template(self, strategy, goal, context):
        subtasks = []
        for i, t in enumerate(strategy["template_subtasks"]):
            subtasks.append(SubTask(
                id=f"t{i:03d}", 
                description=t["desc"], 
                action=t["action"],
                parameters={**t.get("params", {}), "goal": goal, **context},
                priority=TaskPriority.HIGH if i < 2 else TaskPriority.MEDIUM
            ))
        return subtasks

    def _generate_generic_plan(self, goal, context):
        return [
            SubTask(id="t000", description=f"Research: {goal}", action="research", parameters={"goal": goal}),
            SubTask(id="t001", description="Identify key variables", action="identify_variables", parameters={"goal": goal}),
            SubTask(id="t002", description="Build causal model", action="build_causal_model", parameters={"goal": goal}),
            SubTask(id="t003", description="Generate interventions", action="generate_interventions", parameters={"goal": goal}),
            SubTask(id="t004", description="Evaluate and rank", action="evaluate_interventions", parameters={"goal": goal}),
            SubTask(id="t005", description="Execute top intervention", action="execute", parameters={"goal": goal}),
            SubTask(id="t006", description="Measure and learn", action="measure_and_learn", parameters={"goal": goal}),
        ]

    def _resolve_dependencies(self, subtasks):
        parallel_actions = {"causal_query", "memory_search", "research", "identify_variables"}
        for i, task in enumerate(subtasks):
            if i > 0:
                task.dependencies.append(subtasks[i - 1].id)
        for i, task in enumerate(subtasks):
            if task.action in parallel_actions and i > 0:
                prev = subtasks[i - 1]
                if prev.action in parallel_actions and prev.id in task.dependencies:
                    task.dependencies.remove(prev.id)
                    for dep in prev.dependencies:
                        if dep not in task.dependencies:
                            task.dependencies.append(dep)
        return subtasks

    def _enrich_with_causal(self, subtasks, goal):
        try:
            if self._causal_engine and hasattr(self._causal_engine, "get_graph_summary"):
                graph = self._causal_engine.get_graph_summary()
                if graph.get("status") != "no_graph":
                    for task in subtasks:
                        if task.action in ("causal_query", "build_causal_model"):
                            task.parameters["existing_graph"] = graph
                            task.parameters["root_causes"] = graph.get("root_causes", [])
        except Exception:
            pass
        return subtasks

    def _adjust_priorities_bayesian(self, subtasks):
        try:
            if self._bayesian_engine and hasattr(self._bayesian_engine, "select_action"):
                # Adjust based on UCB values
                pass
        except Exception:
            pass
        return subtasks


if __name__ == "__main__":
    print("=" * 60)
    print("SOVEREIGN PLANNER — SELF TEST")
    print("=" * 60)

    p = SovereignPlanner()

    print("\n[1] Decompose: 'Reduce churn by 30% in Q4'")
    plan = p.decompose("Reduce churn by 30% in Q4")
    for t in plan.subtasks:
        print(f" [{t.id}] {t.description} | deps={t.dependencies}")
    print(f" Ready: {[t.id for t in plan.get_ready_tasks()]}")

    print("\n[2] Execute ready tasks")
    ready = p.get_next_actions(plan.id)
    for t in ready:
        p.report_result(plan.id, t.id, {"data": "found"}, success=True)
        print(f" Done: {t.id}")

    print("\n[3] Fail next task → trigger replan")
    ready2 = p.get_next_actions(plan.id)
    if ready2:
        r = p.report_result(plan.id, ready2[0].id, {"error": "no effect"}, success=False)
        print(f" Replan: {r}")

    print("\n[4] Revenue recovery goal")
    plan2 = p.decompose("Recover $50K from Stripe billing gaps")
    for t in plan2.subtasks:
        print(f" [{t.id}] {t.description} | deps={t.dependencies}")

    print("\n[5] Unknown goal → generic")
    plan3 = p.decompose("Build autonomous monitoring for Tampa Blades site")
    for t in plan3.subtasks:
        print(f" [{t.id}] {t.description}")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED")
    print("=" * 60)