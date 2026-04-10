"""
AUTO-INSTRUMENTATION LAYER v1.0

Wraps HandlerRegistry to automatically emit causal observations on every
handler execution. No manual seeding required. Learning compounds automatically.

Usage:
    from sovereign_handlers import HandlerRegistry, PRETTY_BUSY_CLEANING
    from auto_instrumentation import instrument_handlers
    
    registry = HandlerRegistry(PRETTY_BUSY_CLEANING)
    instrumented = instrument_handlers(registry)
    
    # Every call now auto-emits observations
    result = instrumented.execute("identify_gaps")
    # → Causal observation already written to causal_observations
"""

import json
import time
import logging
from datetime import datetime, timezone
from typing import Any, Optional, Callable
from functools import wraps

logger = logging.getLogger("sovereign.instrumentation")


class HandlerObserver:
    """
    Auto-instrumentation layer that wraps handler execution.
    Every handler call automatically emits structured observations
    into the causal engine without manual seeding.
    """
    
    def __init__(self, registry, db_connection=None):
        self.registry = registry
        self.db = db_connection
        self._observations_buffer = []
        self._execution_history = []
    
    def _get_db(self):
        """Lazy database connection."""
        if self.db is None:
            import psycopg2
            self.db = psycopg2.connect(dbname="nexus", host="localhost")
        return self.db
    
    def execute(self, action: str, params: dict = None, context: dict = None) -> dict:
        """
        Execute handler with automatic observation emission.
        Wraps the original handler to capture input/output/timing.
        """
        start_time = time.time()
        params = params or {}
        
        # Capture input state
        input_snapshot = {
            "action": action,
            "params": params,
            "context_keys": list((context or {}).keys()) if context else [],
            "domain": getattr(self.registry.config, 'name', 'unknown')
        }
        
        # Execute handler
        try:
            result = self.registry.execute(action, params, context)
            success = result.get("status") in ("success", "simulated")
            error = None
        except Exception as e:
            result = {"status": "failed", "error": str(e)}
            success = False
            error = str(e)
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        # Capture output state
        output_snapshot = self._extract_metrics(action, result)
        
        # Build causal observation
        observation = {
            "handler_action": action,
            "domain": input_snapshot["domain"],
            "success": success,
            "elapsed_ms": round(elapsed_ms, 2),
            "input_keys": list(params.keys()) if params else [],
            "output_keys": list(result.keys()) if result else [],
            "metrics": output_snapshot,
            "error": error
        }
        
        # Add action-specific metrics
        if action == "identify_gaps":
            observation["gaps_found"] = result.get("total_count", 0)
            observation["total_value"] = result.get("total_value", 0)
            observation["by_status"] = result.get("by_status", {})
            observation["by_location"] = result.get("by_location", {})
            
        elif action == "prioritize_fixes":
            top = result.get("top_opportunity", {})
            observation["ranked_count"] = result.get("count", 0)
            observation["top_score"] = top.get("_score", 0)
            observation["top_budget"] = top.get("budget", 0)
            observation["top_location"] = top.get("location", "unknown")
            
        elif action == "execute_recovery":
            observation["dispatched_count"] = result.get("total_dispatched", 0)
            observation["dispatched_value"] = result.get("total_value", 0)
            
        elif action == "verify_recovery":
            observation["verified_count"] = result.get("verified", 0)
            observation["revenue_captured"] = result.get("total_revenue", 0)
            observation["pending_count"] = result.get("pending", 0)
        
        # Emit observation to database
        self._emit_observation(observation)
        
        # Store in execution history
        self._execution_history.append({
            "action": action,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": success,
            "elapsed_ms": round(elapsed_ms, 2),
            "metrics": output_snapshot
        })
        
        return result
    
    def _extract_metrics(self, action: str, result: dict) -> dict:
        """Extract domain-specific metrics from handler result."""
        metrics = {}
        
        # Common metrics
        if "status" in result:
            metrics["status"] = result["status"]
        
        # Numeric metrics
        for key in ["total_count", "total_value", "total_dispatched", 
                    "verified", "total_revenue", "count"]:
            if key in result:
                metrics[key] = result[key]
        
        # Breakdown metrics
        if "_score_breakdown" in result:
            metrics["score_breakdown"] = result["_score_breakdown"]
        
        return metrics
    
    def _emit_observation(self, observation: dict):
        """Write observation to causal_observations table."""
        try:
            conn = self._get_db()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO causal_observations (variables, observed_at, source)
                VALUES (%s, %s, %s)
            """, (
                json.dumps(observation),
                datetime.now(timezone.utc).isoformat(),
                "handler_instrumentation"
            ))
            
            conn.commit()
            cur.close()
            
            logger.debug(f"Emitted observation: {observation['handler_action']} - {observation.get('success')}")
            
        except Exception as e:
            logger.warning(f"Observation emission failed: {e}")
    
    def get_execution_history(self) -> list:
        """Return recent execution history."""
        return self._execution_history[-20:]
    
    def get_observation_count(self) -> int:
        """Return total observations emitted."""
        try:
            conn = self._get_db()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM causal_observations WHERE source = 'handler_instrumentation'")
            count = cur.fetchone()[0]
            cur.close()
            return count
        except:
            return 0


def instrument_handlers(registry):
    """
    Wrap a HandlerRegistry with auto-instrumentation.
    
    Usage:
        from sovereign_handlers import HandlerRegistry, PRETTY_BUSY_CLEANING
        from auto_instrumentation import instrument_handlers
        
        registry = HandlerRegistry(PRETTY_BUSY_CLEANING)
        instrumented = instrument_handlers(registry)
        
        result = instrumented.execute("identify_gaps")
    """
    return HandlerObserver(registry)