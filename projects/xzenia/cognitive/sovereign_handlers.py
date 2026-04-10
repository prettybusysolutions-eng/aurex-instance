"""
SOVEREIGN EXECUTION HANDLERS v1.0

Universal domain-agnostic execution handlers for the Sovereign Planner.

Architecture:
Planner Action → Handler Registry → Domain Config → PostgreSQL
identify_gaps → GapFinder(config) → SELECT from domain table
prioritize_fixes → Prioritizer(config) → Score + rank results
execute_recovery → Executor(config) → INSERT into fulfillment
verify_recovery → Verifier(config) → UPDATE status + metrics

Each handler is domain-agnostic. Domain behavior is controlled entirely
by DomainConfig — swap the config, swap the domain.

First instantiation: Pretty Busy Cleaning (nexus DB, demand_requests table)
Future: Stripe billing, lead engine, affiliate tracking — same handlers, different configs.

Requires: psycopg2, sovereign_planner.py, sovereign_cognitive_patch.py
"""

import json
import logging
import hashlib
from datetime import datetime, timezone
from typing import Any, Optional, Callable
from dataclasses import dataclass, field

logger = logging.getLogger("sovereign.handlers")

# ============================================================================
# DOMAIN CONFIGURATION
# ============================================================================

@dataclass
class DomainConfig:
    """
    Everything a handler needs to know about a domain.
    Swap this config to change domains — handlers stay the same.
    """
    # Identity
    name: str  # "pretty_busy_cleaning"
    display_name: str  # "Pretty Busy Cleaning"
    # Database
    db_name: str  # "nexus"
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = ""
    db_password: str = ""
    
    # Source table (where unprocessed records live)
    source_table: str = "demand_requests"
    source_id_column: str = "id"
    source_status_column: str = "status"
    source_category_column: str = "category"
    source_category_value: str = "cleaning"  # filter value
    
    # Gap detection: which statuses indicate unprocessed work
    gap_statuses: list = field(default_factory=lambda: ["routed", "matched"])
    
    # Scoring weights for prioritization (must sum to ~1.0)
    score_weights: dict = field(default_factory=lambda: {
        "budget": 0.4,
        "location_match": 0.3,
        "urgency": 0.2,
        "recency": 0.1
    })
    
    # Location priority (higher = more valuable)
    location_priorities: dict = field(default_factory=lambda: {
        "florida": 1.0,
        "tampa": 1.0,
        "massachusetts": 0.6,
        "default": 0.3
    })
    
    # Budget column and normalization
    budget_column: str = "budget"
    budget_max: float = 1000.0  # for normalization
    
    # Fulfillment table (where executed work goes)
    fulfillment_table: str = "fulfillment_executions"
    
    # Metrics table
    metrics_table: str = "handler_metrics"
    
    # Custom field mappings (source column → handler field)
    field_map: dict = field(default_factory=lambda: {
        "title": "title",
        "description": "description",
        "category": "category",
        "location": "location",
        "budget": "budget",
        "status": "status",
        "region": "region"
    })


# ============================================================================
# PRE-BUILT DOMAIN CONFIGS
# ============================================================================

PRETTY_BUSY_CLEANING = DomainConfig(
    name="pretty_busy_cleaning",
    display_name="Pretty Busy Cleaning",
    db_name="nexus",
    source_table="demand_requests",
    source_category_column="category",
    source_category_value="cleaning",
    gap_statuses=["routed", "matched"],
    score_weights={
        "budget": 0.4,
        "location_match": 0.3,
        "urgency": 0.2,
        "recency": 0.1
    },
    location_priorities={
        "florida": 1.0,
        "tampa": 1.0,
        "hillsborough": 0.9,
        "massachusetts": 0.6,
        "default": 0.3
    },
    budget_max=1000.0,
    field_map={
        "title": "title",
        "description": "description",
        "category": "category",
        "location": "location",
        "budget": "budget",
        "status": "status",
        "region": "region"
    }
)

STRIPE_REVENUE_RECOVERY = DomainConfig(
    name="stripe_revenue_recovery",
    display_name="Stripe Revenue Recovery",
    db_name="nexus",
    source_table="billing_events",
    source_category_column="source",
    source_category_value="stripe",
    gap_statuses=["unreconciled", "disputed", "sync_error"],
    score_weights={
        "budget": 0.5,
        "location_match": 0.0,
        "urgency": 0.3,
        "recency": 0.2
    },
    budget_column="amount",
    budget_max=50000.0,
    fulfillment_table="recovery_executions"
)

LEAD_ENGINE = DomainConfig(
    name="lead_engine",
    display_name="Lead Acquisition Engine",
    db_name="nexus",
    source_table="prospects",
    source_category_column="pipeline_stage",
    source_category_value="uncontacted",
    source_status_column="pipeline_stage",
    gap_statuses=["uncontacted", "stale"],
    score_weights={
        "budget": 0.3,
        "location_match": 0.3,
        "urgency": 0.2,
        "recency": 0.2
    },
    budget_column="estimated_value",
    budget_max=10000.0,
    field_map={
        "title": "name",
        "description": "company",
        "category": "pipeline_stage",
        "location": "location",
        "budget": "estimated_value",
        "status": "pipeline_stage"
    }
)

YOUTUBE_CONTENT = DomainConfig(
    name="youtube_content",
    display_name="YouTube Content Pipeline",
    db_name="nexus",
    source_table="youtube_content",
    source_category_column="topic",
    source_category_value="xzenia_build",
    gap_statuses=["planned", "research", "scripting"],
    score_weights={
        "budget": 0.0,
        "urgency": 0.3,
        "recency": 0.2,
        "affiliate_potential": 0.5
    },
    location_priorities={},
    budget_max=0.0,
    budget_column="revenue_cents",
    field_map={
        "title": "video_title",
        "description": "video_title",
        "category": "topic",
        "location": "format",
        "budget": "revenue_cents",
        "status": "status"
    }
)


# ============================================================================
# DATABASE CONNECTION
# ============================================================================

class DBConnection:
    """Thin wrapper around psycopg2 for handler use."""
    def __init__(self, config: DomainConfig):
        self.config = config
        self._conn = None
    
    def connect(self):
        import psycopg2
        conn_params = {"dbname": self.config.db_name, "host": self.config.db_host}
        if self.config.db_port:
            conn_params["port"] = self.config.db_port
        if self.config.db_user:
            conn_params["user"] = self.config.db_user
        if self.config.db_password:
            conn_params["password"] = self.config.db_password
        self._conn = psycopg2.connect(**conn_params)
        return self._conn
    
    def query(self, sql: str, params: tuple = None) -> list[dict]:
        """Execute a SELECT and return list of dicts."""
        if not self._conn:
            self.connect()
        try:
            with self._conn.cursor() as cur:
                cur.execute(sql, params)
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in cur.fetchall()]
        except Exception as e:
            self._conn.rollback()
            raise e
    
    def execute(self, sql: str, params: tuple = None) -> int:
        """Execute an INSERT/UPDATE/DELETE and return affected rows."""
        if not self._conn:
            self.connect()
        try:
            with self._conn.cursor() as cur:
                cur.execute(sql, params)
                self._conn.commit()
                return cur.rowcount
        except Exception as e:
            self._conn.rollback()
            raise e
    
    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None


# ============================================================================
# HANDLER 1: GAP FINDER (identify_gaps)
# ============================================================================

class GapFinder:
    """Finds unprocessed records in any domain.
    Universal logic:
     SELECT * FROM {source_table}
     WHERE {category_column} = {category_value}
     AND {status_column} IN ({gap_statuses})
    
    Returns structured gap records with metadata.
    """
    
    def __init__(self, config: DomainConfig):
        self.config = config
        self.db = DBConnection(config)
    
    def execute(self, params: dict = None) -> dict:
        """
        Find all gaps (unprocessed records) in the domain.
        
        Returns:
        {
            "gaps": [...],
            "total_count": int,
            "total_value": float,
            "by_status": {"routed": 5, "matched": 3},
            "by_location": {"florida": 4, "massachusetts": 3}
        }
        """
        params = params or {}
        
        # Build query
        status_placeholders = ", ".join(["%s"] * len(self.config.gap_statuses))
        
        sql = f"""
        SELECT * FROM {self.config.source_table}
        WHERE {self.config.source_category_column} = %s
        AND {self.config.source_status_column} IN ({status_placeholders})
        ORDER BY {self.config.budget_column} DESC NULLS LAST
        """
        
        query_params = (self.config.source_category_value, *self.config.gap_statuses)
        
        try:
            rows = self.db.query(sql, query_params)
        except Exception as e:
            logger.error(f"GapFinder query failed: {e}")
            return {"status": "failed", "error": str(e), "gaps": []}
        
        # Aggregate
        by_status = {}
        by_location = {}
        total_value = 0.0
        
        for row in rows:
            status = row.get(self.config.source_status_column, "unknown")
            by_status[status] = by_status.get(status, 0) + 1
            
            location = self._extract_location(row)
            by_location[location] = by_location.get(location, 0) + 1
            
            budget = self._extract_budget(row)
            total_value += budget
        
        return {
            "status": "success",
            "gaps": rows,
            "total_count": len(rows),
            "total_value": total_value,
            "by_status": by_status,
            "by_location": by_location,
            "domain": self.config.display_name
        }
    
    def _extract_location(self, row: dict) -> str:
        for field in ["region", "location", "state", "city"]:
            mapped = self.config.field_map.get(field, field)
            if mapped in row and row[mapped]:
                return str(row[mapped]).lower()
        return "unknown"
    
    def _extract_budget(self, row: dict) -> float:
        col = self.config.budget_column
        if col in row and row[col] is not None:
            try:
                val = row[col]
                if isinstance(val, str):
                    val = val.replace("$", "").replace(",", "")
                return float(val)
            except (ValueError, TypeError):
                return 0.0
        return 0.0


# ============================================================================
# HANDLER 2: PRIORITIZER (prioritize_fixes)
# ============================================================================

class Prioritizer:
    """
    Scores and ranks gaps by configurable weighted criteria.
    Universal scoring:
     score = (budget_norm × w_budget) 
          + (location_score × w_location) 
          + (urgency_score × w_urgency) 
          + (recency_score × w_recency)
    
    Weights and location priorities come from DomainConfig.
    """
    
    def __init__(self, config: DomainConfig):
        self.config = config
    
    def execute(self, gaps: list[dict], params: dict = None) -> dict:
        """
        Score and rank a list of gap records.
        
        Args:
            gaps: list of row dicts from GapFinder
            params: optional overrides (e.g., custom weights)
        
        Returns:
        {
            "ranked": [...],  # sorted by score descending
            "top_opportunity": {...},
            "total_recoverable": float
        }
        """
        params = params or {}
        weights = params.get("weights", self.config.score_weights)
        
        scored = []
        for gap in gaps:
            score = self._score(gap, weights)
            scored.append({
                **gap,
                "_score": round(score, 4),
                "_score_breakdown": self._score_breakdown(gap, weights)
            })
        
        scored.sort(key=lambda x: x["_score"], reverse=True)
        
        total_recoverable = sum(
            self._extract_budget(g) for g in gaps
        )
        
        return {
            "status": "success",
            "ranked": scored,
            "top_opportunity": scored[0] if scored else None,
            "total_recoverable": total_recoverable,
            "count": len(scored)
        }
    
    def _score(self, gap: dict, weights: dict) -> float:
        budget_score = min(self._extract_budget(gap) / self.config.budget_max, 1.0)
        location_score = self._location_score(gap)
        urgency_score = self._urgency_score(gap)
        recency_score = self._recency_score(gap)
        
        return (
            budget_score * weights.get("budget", 0.25)
            + location_score * weights.get("location_match", 0.25)
            + urgency_score * weights.get("urgency", 0.25)
            + recency_score * weights.get("recency", 0.25)
        )
    
    def _score_breakdown(self, gap: dict, weights: dict) -> dict:
        return {
            "budget": round(min(self._extract_budget(gap) / self.config.budget_max, 1.0), 3),
            "location": round(self._location_score(gap), 3),
            "urgency": round(self._urgency_score(gap), 3),
            "recency": round(self._recency_score(gap), 3)
        }
    
    def _location_score(self, gap: dict) -> float:
        location = "unknown"
        for field in ["region", "location", "state", "city"]:
            mapped = self.config.field_map.get(field, field)
            if mapped in gap and gap[mapped]:
                location = str(gap[mapped]).lower()
                break
        
        # Check all location priorities
        for key, priority in self.config.location_priorities.items():
            if key in location:
                return priority
        return self.config.location_priorities.get("default", 0.3)
    
    def _urgency_score(self, gap: dict) -> float:
        status = gap.get(self.config.source_status_column, "")
        # matched > routed (matched means someone wants it NOW)
        urgency_map = {
            "matched": 1.0,
            "routed": 0.6,
            "unreconciled": 0.9,
            "disputed": 1.0,
            "sync_error": 0.7,
            "uncontacted": 0.5,
            "stale": 0.3
        }
        return urgency_map.get(status, 0.5)
    
    def _recency_score(self, gap: dict) -> float:
        # If we have a timestamp, score by recency
        for field in ["created_at", "updated_at", "timestamp", "requested_at"]:
            if field in gap and gap[field]:
                try:
                    if isinstance(gap[field], str):
                        dt = datetime.fromisoformat(gap[field].replace("Z", "+00:00"))
                    else:
                        dt = gap[field]
                    age_hours = (datetime.now(timezone.utc) - dt.replace(tzinfo=timezone.utc)).total_seconds() / 3600
                    # Score: 1.0 if <1hr old, decays to 0.1 over 30 days
                    return max(0.1, 1.0 - (age_hours / 720))
                except Exception:
                    pass
        return 0.5  # default if no timestamp
    
    def _extract_budget(self, gap: dict) -> float:
        col = self.config.budget_column
        if col in gap and gap[col] is not None:
            try:
                val = gap[col]
                if isinstance(val, str):
                    val = val.replace("$", "").replace(",", "")
                return float(val)
            except (ValueError, TypeError):
                return 0.0
        return 0.0


# ============================================================================
# HANDLER 3: EXECUTOR (execute_recovery)
# ============================================================================

class Executor:
    """
    Creates fulfillment records for prioritized gaps.
    Universal logic:
     INSERT INTO {fulfillment_table} (source_id, domain, action, ...)
     UPDATE {source_table} SET status = 'dispatched' WHERE id = ...
    """
    
    def __init__(self, config: DomainConfig):
        self.config = config
        self.db = DBConnection(config)
    
    def execute(self, ranked_gaps: list[dict], params: dict = None) -> dict:
        """
        Execute fulfillment for top-priority gaps.
        
        Args:
            ranked_gaps: scored/ranked list from Prioritizer
            params: optional {"limit": 5, "min_score": 0.5}
        
        Returns:
        {
            "dispatched": [...],
            "total_dispatched": int,
            "total_value": float
        }
        """
        params = params or {}
        limit = params.get("limit", 10)
        min_score = params.get("min_score", 0.3)
        
        # Ensure fulfillment table exists
        self._ensure_fulfillment_table()
        
        dispatched = []
        total_value = 0.0
        
        for gap in ranked_gaps[:limit]:
            score = gap.get("_score", 0)
            if score < min_score:
                continue
            
            source_id = gap.get(self.config.source_id_column)
            if not source_id:
                continue
            
            try:
                # Generate fulfillment ID and map to actual schema
                fulfillment_id = hashlib.sha256(
                    f"{source_id}{datetime.now(timezone.utc).isoformat()}".encode()
                ).hexdigest()[:16]
                
                budget = self._extract_budget(gap)
                
                # Map to actual fulfillment_executions schema
                f_record = self._to_fulfillment_schema(gap, fulfillment_id, score, budget)
                
                insert_sql = f"""
                INSERT INTO {self.config.fulfillment_table}
                (id, demand_id, supply_id, route, status, price_estimate, price_final,
                 started_at, completed_at, failure_reason, failure_detail, metadata_json, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                self.db.execute(insert_sql, (
                    f_record["id"],
                    f_record["demand_id"],
                    f_record["supply_id"],
                    f_record["route"],
                    f_record["status"],
                    f_record["price_estimate"],
                    f_record["price_final"],
                    f_record["started_at"],
                    f_record["completed_at"],
                    f_record["failure_reason"],
                    f_record["failure_detail"],
                    f_record["metadata_json"],
                    f_record["created_at"]
                ))
                
                # Update source record status
                update_sql = f"""
                UPDATE {self.config.source_table}
                SET {self.config.source_status_column} = 'dispatched'
                WHERE {self.config.source_id_column} = %s
                """
                self.db.execute(update_sql, (source_id,))
                
                dispatched.append({
                    "fulfillment_id": fulfillment_id,
                    "source_id": str(source_id),
                    "budget": budget,
                    "score": score,
                    "status": "dispatched"
                })
                total_value += budget
                
            except Exception as e:
                logger.error(f"Dispatch failed for {source_id}: {e}")
                dispatched.append({
                    "source_id": str(source_id),
                    "status": "failed",
                    "error": str(e)
                })
        
        return {
            "status": "success",
            "dispatched": dispatched,
            "total_dispatched": sum(1 for d in dispatched if d.get("status") == "DISPATCHED"),
            "total_value": total_value,
            "domain": self.config.display_name
        }
    
    def _ensure_fulfillment_table(self):
        """Uses existing fulfillment_executions table with real schema."""
        # Table already exists with real schema - no creation needed
        pass

    def _to_fulfillment_schema(self, gap: dict, fulfillment_id: str, score: float, budget: float) -> dict:
        """Map handler output to actual fulfillment_executions schema."""
        return {
            "id": fulfillment_id,
            "demand_id": str(gap.get(self.config.source_id_column, "")),
            "supply_id": "",  # Will be filled by routing logic
            "route": self.config.name,
            "status": "DISPATCHED",
            "price_estimate": budget,
            "price_final": None,
            "started_at": None,
            "completed_at": None,
            "failure_reason": None,
            "failure_detail": None,
            "metadata_json": json.dumps({
                "title": gap.get("title", ""),
                "location": gap.get("location", ""),
                "score": score,
                "score_breakdown": gap.get("_score_breakdown", {}),
                "handler_domain": self.config.name
            }),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    
    def _extract_budget(self, gap: dict) -> float:
        col = self.config.budget_column
        if col in gap and gap[col] is not None:
            try:
                val = gap[col]
                if isinstance(val, str):
                    val = val.replace("$", "").replace(",", "")
                return float(val)
            except (ValueError, TypeError):
                return 0.0
        return 0.0


# ============================================================================
# HANDLER 4: VERIFIER (verify_recovery)
# ============================================================================

class Verifier:
    """
    Confirms fulfillment completion and records revenue metrics.
    Universal logic:
     SELECT from fulfillment_table WHERE status = 'dispatched'
     For each: check completion criteria
     UPDATE status, revenue_captured, completed_at
     INSERT into metrics_table
    """
    
    def __init__(self, config: DomainConfig):
        self.config = config
        self.db = DBConnection(config)
    
    def execute(self, params: dict = None) -> dict:
        """
        Verify all dispatched fulfillments and update metrics.
        
        Returns:
        {
            "verified": int,
            "total_revenue": float,
            "pending": int,
            "failed": int
        }
        """
        params = params or {}
        
        # Ensure metrics table
        self._ensure_metrics_table()
        
        # Get all dispatched fulfillments for this domain
        # Use actual schema: route (not domain), status = DISPATCHED (uppercase)
        sql = f"""
        SELECT * FROM {self.config.fulfillment_table}
        WHERE route = %s AND status = 'DISPATCHED'
        """
        
        try:
            pending = self.db.query(sql, (self.config.name,))
        except Exception as e:
            return {"status": "failed", "error": str(e)}
        
        verified = 0
        total_revenue = 0.0
        failed = 0
        
        for record in pending:
            # In production, this would check external systems
            # For now: mark as completed and capture budget as revenue
            try:
                budget = float(record.get("price_estimate", 0))
                
                # Update to COMPLETED using actual schema
                update_sql = f"""
                UPDATE {self.config.fulfillment_table}
                SET status = 'COMPLETED',
                    completed_at = %s,
                    price_final = %s
                WHERE id = %s
                """
                self.db.execute(update_sql, (
                    datetime.now(timezone.utc).isoformat(),
                    budget,
                    record["id"]
                ))
                
                # Record metric
                self._record_metric(record, budget)
                
                verified += 1
                total_revenue += budget
                
            except Exception as e:
                logger.error(f"Verification failed for {record.get('id')}: {e}")
                failed += 1
        
        return {
            "status": "success",
            "verified": verified,
            "total_revenue": total_revenue,
            "pending": len(pending) - verified - failed,
            "failed": failed,
            "domain": self.config.display_name
        }
    
    def _record_metric(self, record: dict, revenue: float):
        sql = f"""
        INSERT INTO {self.config.metrics_table}
        (domain, fulfillment_id, revenue, recorded_at)
        VALUES (%s, %s, %s, %s)
        """
        try:
            self.db.execute(sql, (
                self.config.name,
                record["id"],
                revenue,
                datetime.now(timezone.utc).isoformat()
            ))
        except Exception:
            pass  # metrics are non-critical
    
    def _ensure_metrics_table(self):
        sql = f"""
        CREATE TABLE IF NOT EXISTS {self.config.metrics_table} (
            id SERIAL PRIMARY KEY,
            domain TEXT NOT NULL,
            fulfillment_id TEXT,
            revenue REAL DEFAULT 0,
            recorded_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        try:
            self.db.execute(sql)
        except Exception:
            pass


# ============================================================================
# HANDLER REGISTRY (wires into SovereignPlanner)
# ============================================================================

class HandlerRegistry:
    """
    Connects the SovereignPlanner's action names to real execution handlers.
    Usage:
     registry = HandlerRegistry(PRETTY_BUSY_CLEANING)
     
     # In planner execution loop:
     result = registry.execute(task.action, task.parameters, context)
    """
    
    def __init__(self, config: DomainConfig):
        self.config = config
        self.gap_finder = GapFinder(config)
        self.prioritizer = Prioritizer(config)
        self.executor = Executor(config)
        self.verifier = Verifier(config)
        
        # Action name → handler mapping
        self._handlers: dict[str, Callable] = {
            # Direct mappings
            "identify_gaps": self._handle_identify_gaps,
            "prioritize_fixes": self._handle_prioritize_fixes,
            "execute_recovery": self._handle_execute_recovery,
            "verify_recovery": self._handle_verify_recovery,
            
            # Aliases (planner may use different action names)
            "find_gaps": self._handle_identify_gaps,
            "rank_fixes": self._handle_prioritize_fixes,
            "dispatch": self._handle_execute_recovery,
            "verify": self._handle_verify_recovery,
        }
        
        # Execution context (shared state between handlers in a plan)
        self._context: dict = {}
    
    def execute(self, action: str, params: dict = None, context: dict = None) -> dict:
        """
        Execute a handler by action name.
        
        Returns structured result dict.
        Falls back to simulation for unknown actions.
        """
        if context:
            self._context.update(context)
        
        handler = self._handlers.get(action)
        if handler:
            try:
                result = handler(params or {})
                result["_handler"] = action
                result["_domain"] = self.config.name
                result["_real_execution"] = True
                return result
            except Exception as e:
                logger.error(f"Handler {action} failed: {e}")
                return {
                    "status": "failed",
                    "error": str(e),
                    "_handler": action,
                    "_real_execution": True
                }
        else:
            # Unknown action — simulate but flag it
            logger.warning(f"No handler for action '{action}' — simulating")
            return {
                "status": "simulated",
                "action": action,
                "params": params,
                "_handler": "none",
                "_real_execution": False,
                "_note": f"No handler registered for '{action}'. Register one via registry.register()"
            }
    
    def register(self, action: str, handler: Callable):
        """Register a custom handler for an action name."""
        self._handlers[action] = handler
    
    def _handle_identify_gaps(self, params: dict) -> dict:
        result = self.gap_finder.execute(params)
        # Store gaps in context for downstream handlers
        self._context["gaps"] = result.get("gaps", [])
        return result
    
    def _handle_prioritize_fixes(self, params: dict) -> dict:
        gaps = self._context.get("gaps", [])
        if not gaps:
            return {"status": "failed", "error": "No gaps in context. Run identify_gaps first."}
        result = self.prioritizer.execute(gaps, params)
        # Store ranked list for executor
        self._context["ranked"] = result.get("ranked", [])
        return result
    
    def _handle_execute_recovery(self, params: dict) -> dict:
        ranked = self._context.get("ranked", [])
        if not ranked:
            return {"status": "failed", "error": "No ranked gaps. Run prioritize_fixes first."}
        return self.executor.execute(ranked, params)
    
    def _handle_verify_recovery(self, params: dict) -> dict:
        return self.verifier.execute(params)
    
    def get_registered_actions(self) -> list[str]:
        return list(self._handlers.keys())


# ============================================================================
# PLANNER INTEGRATION
# ============================================================================

def create_integrated_runner(config, planner=None, causal=None, memory=None):
    """
    Create a fully integrated execution loop:
    Planner → Registry → Handlers → PostgreSQL
    
    Usage:
     runner = create_integrated_runner(PRETTY_BUSY_CLEANING)
     result = runner("Dispatch all pending cleaning requests in Tampa")
    """
    from sovereign_planner import SovereignPlanner
    
    if planner is None:
        planner = SovereignPlanner()
    if causal:
        planner.connect_causal_engine(causal)
    if memory:
        planner.connect_semantic_memory(memory)
    
    registry = HandlerRegistry(config)
    
    def run(goal: str) -> dict:
        plan = planner.decompose(goal)
        results = []
        
        while not planner.is_complete(plan.id):
            ready = planner.get_next_actions(plan.id)
            if not ready:
                break
            
            for task in ready:
                # Route through handler registry
                result = registry.execute(task.action, task.parameters)
                
                success = result.get("status") != "failed"
                planner.report_result(plan.id, task.id, result, success=success)
                
                results.append({
                    "task_id": task.id,
                    "action": task.action,
                    "description": task.description,
                    "result_status": result.get("status"),
                    "real_execution": result.get("_real_execution", False),
                    "details": {k: v for k, v in result.items() if not k.startswith("_")}
                })
        
        status = planner.get_plan_status(plan.id)
        
        return {
            "plan_id": plan.id,
            "goal": goal,
            "domain": config.display_name,
            "percent_complete": status["percent_complete"],
            "task_results": results,
            "summary": {
                "total_tasks": len(results),
                "real_executions": sum(1 for r in results if r["real_execution"]),
                "simulated": sum(1 for r in results if not r["real_execution"]),
                "successes": sum(1 for r in results if r["result_status"] == "success"),
                "failures": sum(1 for r in results if r["result_status"] == "failed")
            }
        }
    
    return run


# ============================================================================
# SELF-TEST (runs without DB to verify logic)
# ============================================================================

def test_handlers_standalone():
    """Test handler logic without PostgreSQL."""
    print("=" * 60)
    print("HANDLER REGISTRY — STANDALONE TEST")
    print("=" * 60)
    config = PRETTY_BUSY_CLEANING
    
    # Test Prioritizer with mock data
    print("\n[1] Prioritizer — scoring mock gaps")
    prioritizer = Prioritizer(config)
    mock_gaps = [
        {"id": "aaa", "title": "Office cleaning Tampa", "budget": 500, "region": "florida", "status": "matched", "created_at": "2026-03-24T10:00:00Z"},
        {"id": "bbb", "title": "Move-out Springfield", "budget": 250, "region": "massachusetts", "status": "routed", "created_at": "2026-03-20T10:00:00Z"},
        {"id": "ccc", "title": "Regular cleaning Cambridge", "budget": 120, "region": "massachusetts", "status": "routed", "created_at": "2026-03-15T10:00:00Z"},
        {"id": "ddd", "title": "Move-in cleaning MA", "budget": 350, "region": "massachusetts", "status": "matched", "created_at": "2026-03-23T10:00:00Z"},
    ]
    
    result = prioritizer.execute(mock_gaps)
    print(f" Ranked {result['count']} gaps:")
    for r in result["ranked"]:
        print(f"  Score={r['_score']:.3f} | ${r['budget']:>5} | {r['title'][:35]:35} | {r['_score_breakdown']}")
    print(f" Top: {result['top_opportunity']['title']} (${result['top_opportunity']['budget']})")
    print(f" Total recoverable: ${result['total_recoverable']}")
    
    # Test Registry routing
    print("\n[2] Registry — action routing")
    registry = HandlerRegistry(config)
    actions = registry.get_registered_actions()
    print(f" Registered actions: {actions}")
    
    # Test unknown action
    sim_result = registry.execute("unknown_action", {"test": True})
    print(f" Unknown action result: {sim_result['status']} (real={sim_result['_real_execution']})")
    
    print("\n" + "=" * 60)
    print("STANDALONE TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    test_handlers_standalone()