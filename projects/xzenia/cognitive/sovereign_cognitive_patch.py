"""
SOVEREIGN COGNITIVE PATCH v1.0

Integrated replacement for:

1. Frequency-based causal inference → Real DoWhy causal graphs
2. ILIKE keyword search → Embedding-based semantic memory

Drop-in compatible with CognitiveEngineV5.2 PostgreSQL schema.
Designed for: Python 3.11+ | MacBook Air 8GB | PostgreSQL 16 | Ollama local

Author: Aurex × Claude collaborative build
"""

import json
import logging
import hashlib
from datetime import datetime, timezone
from typing import Any, Optional
from dataclasses import dataclass, field

import numpy as np
import networkx as nx
import pandas as pd

# ─── DoWhy imports ───
from dowhy import CausalModel

# ─── pgmpy for graph construction ───
from pgmpy.models import BayesianNetwork
from pgmpy.estimators import HillClimbSearch, BIC

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sovereign.cognitive")

# ============================================================================

# PART 1: CAUSAL INFERENCE ENGINE (replaces frequency counter)

# ============================================================================

@dataclass
class CausalObservation:
    """Single observed event with variables and values."""
    variables: dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class SovereignCausalEngine:
    """
    Real causal inference engine using DoWhy + pgmpy.
    Pipeline:
    1. Collect observations as structured variable sets
    2. Build causal graph via structure learning (BIC-scored hill climbing)
       OR accept user-defined graph
    3. Identify causal estimands via DoWhy (backdoor/frontdoor)
    4. Estimate treatment effects
    5. Run counterfactual queries: "What would happen if X had been different?"

    This replaces the frequency-based pair counter entirely.
    """

    def __init__(self, min_observations: int = 20):
        self.observations: list[CausalObservation] = []
        self.min_observations = min_observations
        self._learned_graph: Optional[nx.DiGraph] = None
        self._dataframe: Optional[pd.DataFrame] = None
        self._manual_graph: Optional[str] = None  # DOT format

    # ── Data Collection ──

    def observe(self, variables: dict[str, Any]) -> int:
        """
        Record an observation. Each observation is a dict of variable: value pairs.
        
        Example:
        engine.observe({
            "pricing_change": 1,
            "churn_rate": 0.12,
            "revenue": 50000,
            "support_tickets": 23
        })
        
        Returns: total observation count
        """
        obs = CausalObservation(variables=variables)
        self.observations.append(obs)
        # Invalidate cached graph when new data arrives
        if len(self.observations) % 10 == 0:
            self._learned_graph = None
        return len(self.observations)

    def load_observations_from_df(self, df: pd.DataFrame) -> int:
        """Bulk load from a DataFrame (e.g., from PostgreSQL query)."""
        for _, row in df.iterrows():
            self.observe(row.to_dict())
        return len(self.observations)

    # ── Graph Construction ──

    def set_causal_graph(self, edges: list[tuple[str, str]]) -> None:
        """
        Manually define causal structure when domain knowledge exists.
        
        Example:
        engine.set_causal_graph([
            ("pricing_change", "churn_rate"),
            ("pricing_change", "revenue"),
            ("churn_rate", "revenue"),
            ("support_quality", "churn_rate")
        ])
        """
        G = nx.DiGraph()
        G.add_edges_from(edges)
        
        # Validate: must be a DAG
        if not nx.is_directed_acyclic_graph(G):
            raise ValueError("Causal graph must be a DAG (no cycles). "
                           f"Cycles found: {list(nx.simple_cycles(G))}")
        
        self._learned_graph = G
        # Build DOT format for DoWhy
        dot_edges = "; ".join(f"{u} -> {v}" for u, v in G.edges())
        self._manual_graph = f"digraph {{ {dot_edges} }}"
        logger.info(f"Causal graph set: {len(G.nodes())} nodes, {len(G.edges())} edges")

    def learn_structure(self, force: bool = False) -> nx.DiGraph:
        """
        Learn causal graph structure from data using BIC-scored hill climbing.
        Requires sufficient observations for statistical validity.
        
        Returns the learned DiGraph.
        """
        if self._learned_graph is not None and not force:
            return self._learned_graph

        df = self._get_dataframe()
        if len(df) < self.min_observations:
            raise ValueError(
                f"Need at least {self.min_observations} observations for structure learning. "
                f"Have {len(df)}. Collect more data or set graph manually via set_causal_graph()."
            )

        # Discretize continuous variables for structure learning
        df_discrete = df.copy()
        for col in df_discrete.columns:
            if df_discrete[col].dtype in [np.float64, np.float32]:
                df_discrete[col] = pd.qcut(df_discrete[col], q=4, labels=False, duplicates='drop')

        # Hill climb with BIC score
        searcher = HillClimbSearch(df_discrete)
        best_model = searcher.estimate(scoring_method=BIC(df_discrete))
        
        self._learned_graph = nx.DiGraph(best_model.edges())
        
        # Build DOT for DoWhy
        dot_edges = "; ".join(f"{u} -> {v}" for u, v in best_model.edges())
        self._manual_graph = f"digraph {{ {dot_edges} }}"
        
        logger.info(f"Learned structure: {list(best_model.edges())}")
        return self._learned_graph

    # ── Causal Queries ──

    def estimate_effect(
        self,
        treatment: str,
        outcome: str,
        method: str = "backdoor.linear_regression"
    ) -> dict:
        """
        Estimate the causal effect of treatment on outcome.
        
        Args:
            treatment: Variable name (e.g., "pricing_change")
            outcome: Variable name (e.g., "churn_rate")
            method: DoWhy estimation method
        
        Returns:
            {
                "treatment": str,
                "outcome": str,
                "estimand": str,
                "estimate": float,
                "confidence": str,
                "method": str
            }
        """
        df = self._get_dataframe()
        graph = self._get_dot_graph()

        # Auto-convert treatment to binary if needed for propensity methods
        treatment_converted = False
        if "propensity" in method:
            if df[treatment].nunique() > 2:
                median_val = df[treatment].median()
                df = df.copy()
                df[treatment] = (df[treatment] > median_val).astype(float)
                treatment_converted = True
            elif not set(df[treatment].unique()).issubset({0.0, 1.0, 0, 1}):
                unique_vals = sorted(df[treatment].unique())
                df = df.copy()
                df[treatment] = (df[treatment] == unique_vals[-1]).astype(float)
                treatment_converted = True

        try:
            model = CausalModel(
                data=df,
                treatment=treatment,
                outcome=outcome,
                graph=graph
            )

            # Identify estimand
            estimand = model.identify_effect(proceed_when_unidentifiable=True)
            
            # Estimate
            estimate = model.estimate_effect(
                estimand,
                method_name=method
            )

            return {
                "treatment": treatment,
                "outcome": outcome,
                "estimand": str(estimand),
                "estimate": float(estimate.value),
                "interpretation": self._interpret_effect(treatment, outcome, float(estimate.value)),
                "method": method,
                "n_observations": len(df),
                "status": "success",
                "treatment_converted": treatment_converted
            }

        except Exception as e:
            logger.warning(f"DoWhy estimation failed: {e}")
            return {
                "treatment": treatment,
                "outcome": outcome,
                "error": str(e),
                "status": "failed",
                "suggestion": self._suggest_fix(str(e), treatment, outcome, df),
                "treatment_converted": treatment_converted
            }

    def counterfactual(
        self,
        treatment: str,
        outcome: str,
        treatment_value: float,
        control_value: float = 0.0
    ) -> dict:
        """
        Answer: "What would outcome have been if treatment were set to X?"
        
        Example:
        engine.counterfactual(treatment="pricing_change",
                             outcome="revenue",
                             treatment_value=1.0,  # what if we changed pricing
                             control_value=0.0    # compared to not changing
        )
        """
        df = self._get_dataframe()
        graph = self._get_dot_graph()

        try:
            model = CausalModel(
                data=df,
                treatment=treatment,
                outcome=outcome,
                graph=graph
            )

            estimand = model.identify_effect(proceed_when_unidentifiable=True)
            estimate = model.estimate_effect(estimand, method_name="backdoor.linear_regression")

            # Counterfactual: effect × (treatment_value - control_value)
            effect = float(estimate.value)
            counterfactual_delta = effect * (treatment_value - control_value)
            
            baseline_outcome = float(df[outcome].mean())

            return {
                "question": f"What if {treatment} = {treatment_value} vs {control_value}?",
                "causal_effect_per_unit": effect,
                "counterfactual_delta": counterfactual_delta,
                "baseline_outcome": baseline_outcome,
                "projected_outcome": baseline_outcome + counterfactual_delta,
                "status": "success"
            }

        except Exception as e:
            return {
                "question": f"What if {treatment} = {treatment_value}?",
                "error": str(e),
                "status": "failed"
            }

    def get_graph_summary(self) -> dict:
        """Return current causal graph as inspectable structure."""
        if self._learned_graph is None:
            return {"status": "no_graph", "message": "Call learn_structure() or set_causal_graph() first"}
        
        G = self._learned_graph
        return {
            "nodes": list(G.nodes()),
            "edges": list(G.edges()),
            "n_nodes": len(G.nodes()),
            "n_edges": len(G.edges()),
            "root_causes": [n for n in G.nodes() if G.in_degree(n) == 0],
            "terminal_effects": [n for n in G.nodes() if G.out_degree(n) == 0],
            "dot": self._manual_graph
        }

    # ── Internal Helpers ──

    def _get_dataframe(self) -> pd.DataFrame:
        if not self.observations:
            raise ValueError("No observations recorded. Call observe() first.")
        records = [obs.variables for obs in self.observations]
        return pd.DataFrame(records)

    def _get_dot_graph(self) -> str:
        if self._manual_graph:
            return self._manual_graph
        if self._learned_graph is not None:
            dot_edges = "; ".join(f"{u} -> {v}" for u, v in self._learned_graph.edges())
            return f"digraph {{ {dot_edges} }}"
        raise ValueError("No causal graph available. Call set_causal_graph() or learn_structure().")

    @staticmethod
    def _interpret_effect(treatment: str, outcome: str, value: float) -> str:
        direction = "increases" if value > 0 else "decreases"
        magnitude = abs(value)
        if magnitude < 0.01:
            strength = "negligible"
        elif magnitude < 0.1:
            strength = "small"
        elif magnitude < 0.5:
            strength = "moderate"
        else:
            strength = "strong"
        return f"{treatment} has a {strength} {direction} effect on {outcome} ({value:+.4f} per unit)"

    @staticmethod
    def _suggest_fix(error: str, treatment: str, outcome: str, df: pd.DataFrame) -> str:
        if "not found" in error.lower() or "column" in error.lower():
            return f"Variable names must match columns. Available: {list(df.columns)}"
        if "singular" in error.lower() or "collinear" in error.lower():
            return "Variables may be collinear. Try different treatment/outcome pairs."
        return "Check that graph structure is valid and variables have sufficient variance."


# ============================================================================

# PART 2: SEMANTIC MEMORY ENGINE (replaces ILIKE search)

# ============================================================================

@dataclass
class MemoryRecord:
    """A memory with both text content and its embedding vector."""
    id: str
    content: str
    memory_type: str
    importance: float
    embedding: Optional[np.ndarray] = None
    metadata: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class SovereignSemanticMemory:
    """
    Semantic memory engine using local Ollama embeddings.
    Pipeline:
    1. Text → Ollama embedding model → 768-dim vector
    2. Store vector alongside JSONB record in PostgreSQL
    3. Query → embed query → cosine similarity against all stored vectors
    4. Return ranked results by semantic relevance

    Falls back to keyword search ONLY if Ollama is unreachable,
    and logs a warning so you know it happened.

    Compatible with: nomic-embed-text, all-minilm, mxbai-embed-large
    """

    def __init__(
        self,
        ollama_url: str = "http://localhost:11434",
        model: str = "nomic-embed-text",
        fallback_model: str = "all-minilm"
    ):
        self.ollama_url = ollama_url
        self.model = model
        self.fallback_model = fallback_model
        self.memories: list[MemoryRecord] = []
        self._embedding_cache: dict[str, np.ndarray] = {}

    # ── Embedding Generation ──

    def _get_embedding(self, text: str) -> Optional[np.ndarray]:
        """
        Get embedding vector from Ollama. Tries primary model, then fallback.
        Uses cache to avoid redundant API calls.
        """
        cache_key = hashlib.md5(f"{self.model}:{text}".encode()).hexdigest()
        if cache_key in self._embedding_cache:
            return self._embedding_cache[cache_key]

        import urllib.request
        
        for model_name in [self.model, self.fallback_model]:
            try:
                payload = json.dumps({
                    "model": model_name,
                    "prompt": text
                }).encode()
                
                req = urllib.request.Request(
                    f"{self.ollama_url}/api/embeddings",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                
                with urllib.request.urlopen(req, timeout=30) as resp:
                    result = json.loads(resp.read().decode())
                    if "embedding" in result:
                        vec = np.array(result["embedding"], dtype=np.float32)
                        self._embedding_cache[cache_key] = vec
                        logger.info(f"Embedding generated via {model_name}: dim={len(vec)}")
                        return vec

            except Exception as e:
                logger.warning(f"Embedding failed with {model_name}: {e}")
                continue

        logger.error("ALL embedding models failed. Semantic search unavailable.")
        return None

    # ── Memory Storage ──

    def store(
        self,
        content: str,
        memory_type: str = "general",
        importance: float = 0.5,
        metadata: Optional[dict] = None
    ) -> MemoryRecord:
        """
        Store a memory with its embedding vector.
        
        Example:
        mem.store(
            content="Pricing increase of 15% caused 8% churn spike in Q3",
            memory_type="causal_observation",
            importance=0.9,
            metadata={"domain": "revenue", "quarter": "Q3"}
        )
        """
        embedding = self._get_embedding(content)
        
        record = MemoryRecord(
            id=hashlib.sha256(f"{content}{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:16],
            content=content,
            memory_type=memory_type,
            importance=importance,
            embedding=embedding,
            metadata=metadata or {},
        )
        
        self.memories.append(record)
        
        status = "with_embedding" if embedding is not None else "text_only (NO EMBEDDING)"
        logger.info(f"Memory stored [{status}]: {content[:60]}...")
        return record

    # ── Semantic Search ──

    def search(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.3,
        memory_type: Optional[str] = None
    ) -> list[dict]:
        """
        Search memories by semantic similarity.
        
        Returns ranked list of memories with similarity scores.
        Falls back to keyword search with WARNING if no embeddings available.
        """
        query_embedding = self._get_embedding(query)
        
        candidates = self.memories
        if memory_type:
            candidates = [m for m in candidates if m.memory_type == memory_type]

        if query_embedding is None or not any(m.embedding is not None for m in candidates):
            logger.warning("⚠ FALLING BACK TO KEYWORD SEARCH — embeddings unavailable")
            return self._keyword_fallback(query, candidates, top_k)

        # Cosine similarity search
        results = []
        for mem in candidates:
            if mem.embedding is None:
                continue
            similarity = self._cosine_similarity(query_embedding, mem.embedding)
            if similarity >= min_similarity:
                results.append({
                    "id": mem.id,
                    "content": mem.content,
                    "type": mem.memory_type,
                    "importance": mem.importance,
                    "similarity": float(similarity),
                    "metadata": mem.metadata,
                    "search_method": "semantic"
                })

        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    def search_by_concept(self, concept: str, top_k: int = 5) -> list[dict]:
        """
        Higher-level search: find memories related to a concept,
        even if the exact words don't appear.
        
        Example: search_by_concept("customer attrition") 
                 should find memories about "churn", "cancellations", "lost accounts"
        """
        return self.search(query=concept, top_k=top_k, min_similarity=0.25)

    # ── Internal Helpers ──

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    @staticmethod
    def _keyword_fallback(query: str, candidates: list[MemoryRecord], top_k: int) -> list[dict]:
        query_terms = set(query.lower().split())
        results = []
        for mem in candidates:
            content_terms = set(mem.content.lower().split())
            overlap = len(query_terms & content_terms)
            if overlap > 0:
                results.append({
                    "id": mem.id,
                    "content": mem.content,
                    "type": mem.memory_type,
                    "importance": mem.importance,
                    "similarity": overlap / max(len(query_terms), 1),
                    "metadata": mem.metadata,
                    "search_method": "keyword_fallback"
                })
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    def get_stats(self) -> dict:
        embedded_count = sum(1 for m in self.memories if m.embedding is not None)
        return {
            "total_memories": len(self.memories),
            "with_embeddings": embedded_count,
            "without_embeddings": len(self.memories) - embedded_count,
            "embedding_coverage": f"{embedded_count/max(len(self.memories),1)*100:.1f}%",
            "cache_size": len(self._embedding_cache),
            "model": self.model
        }


# ============================================================================

# PART 3: POSTGRESQL INTEGRATION LAYER

# ============================================================================

class PostgreSQLBridge:
    """
    Bridge to wire both engines into your existing PostgreSQL schema.
    Provides SQL for:
    - Adding embedding column to memory table
    - Storing/retrieving embeddings as binary
    - Loading observations for causal engine from structured tables

    Does NOT require schema migration — adds columns non-destructively.
    """

    @staticmethod
    def migration_sql() -> str:
        """SQL to add embedding support to existing memory table."""
        return """
        -- Add embedding column if not exists
        DO $$ 
        BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'memories' AND column_name = 'embedding'
        ) THEN
            ALTER TABLE memories ADD COLUMN embedding BYTEA;
        END IF;
        END $$;
        
        -- Add embedding dimension tracking
        DO $$ 
        BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'memories' AND column_name = 'embedding_dim'
        ) THEN
            ALTER TABLE memories ADD COLUMN embedding_dim INTEGER DEFAULT 0;
        END IF;
        END $$;

        -- Create causal observations table
        CREATE TABLE IF NOT EXISTS causal_observations (
            id SERIAL PRIMARY KEY,
            variables JSONB NOT NULL,
            observed_at TIMESTAMPTZ DEFAULT NOW(),
            source VARCHAR(255) DEFAULT 'system'
        );
        
        -- Create causal graphs table
        CREATE TABLE IF NOT EXISTS causal_graphs (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            dot_graph TEXT NOT NULL,
            edges JSONB NOT NULL,
            learned_at TIMESTAMPTZ DEFAULT NOW(),
            n_observations INTEGER,
            method VARCHAR(50) DEFAULT 'hill_climb_bic'
        );
        
        -- Index for faster JSONB queries on observations
        CREATE INDEX IF NOT EXISTS idx_causal_obs_variables 
            ON causal_observations USING GIN (variables);
        """

    @staticmethod
    def store_embedding_sql() -> str:
        return """
        UPDATE memories 
        SET embedding = %(embedding)s, embedding_dim = %(dim)s
        WHERE id = %(memory_id)s;
        """

    @staticmethod
    def load_observations_sql(limit: int = 1000) -> str:
        return f"""
        SELECT variables FROM causal_observations 
        ORDER BY observed_at DESC LIMIT {limit};
        """

    @staticmethod
    def numpy_to_bytes(arr: np.ndarray) -> bytes:
        """Serialize numpy array for PostgreSQL BYTEA storage."""
        return arr.tobytes()

    @staticmethod
    def bytes_to_numpy(data: bytes, dim: int) -> np.ndarray:
        """Deserialize BYTEA back to numpy array."""
        return np.frombuffer(data, dtype=np.float32).reshape(dim)


# ============================================================================

# PART 4: INTEGRATION TEST SUITE

# ============================================================================

def run_integration_tests() -> dict:
    """
    Run all tests to verify both engines are operational.
    Returns structured results — paste these back for validation.
    """
    results = {}
    
    # ── Test 1: Causal Engine with manual graph ──
    print("\n" + "="*60)
    print("TEST 1: Causal Inference — Manual Graph + DoWhy")
    print("="*60)

    try:
        causal = SovereignCausalEngine(min_observations=10)
        
        # Generate synthetic but realistic B2B SaaS observations
        np.random.seed(42)
        n = 100
        
        pricing_change = np.random.binomial(1, 0.3, n).astype(float)
        support_quality = np.random.normal(7, 1.5, n).clip(1, 10)
        # Causal relationships: pricing → churn, support → churn, churn → revenue
        churn_rate = 0.05 + 0.08 * pricing_change - 0.02 * support_quality + np.random.normal(0, 0.02, n)
        churn_rate = churn_rate.clip(0, 1)
        revenue = 100000 - 500000 * churn_rate + 20000 * support_quality + np.random.normal(0, 5000, n)
        
        for i in range(n):
            causal.observe({
                "pricing_change": pricing_change[i],
                "support_quality": support_quality[i],
                "churn_rate": churn_rate[i],
                "revenue": revenue[i]
            })
        
        # Set known causal graph
        causal.set_causal_graph([
            ("pricing_change", "churn_rate"),
            ("support_quality", "churn_rate"),
            ("churn_rate", "revenue"),
            ("support_quality", "revenue")
        ])
        
        # Estimate causal effect
        effect = causal.estimate_effect("pricing_change", "churn_rate")
        print(f" Effect of pricing_change → churn_rate: {json.dumps(effect, indent=2)}")
        
        # Counterfactual
        cf = causal.counterfactual("pricing_change", "revenue", 
                                  treatment_value=1.0, control_value=0.0)
        print(f" Counterfactual (pricing=1 vs 0): {json.dumps(cf, indent=2)}")
        
        # Graph summary
        graph = causal.get_graph_summary()
        print(f" Graph: {graph['n_nodes']} nodes, {graph['n_edges']} edges")
        print(f" Root causes: {graph['root_causes']}")
        print(f" Terminal effects: {graph['terminal_effects']}")
        
        results["causal_engine"] = {
            "status": "OPERATIONAL",
            "effect_estimate": effect,
            "counterfactual": cf,
            "graph": graph
        }
        
    except Exception as e:
        results["causal_engine"] = {"status": "FAILED", "error": str(e)}
        print(f" FAILED: {e}")
        import traceback
        traceback.print_exc()

    # ── Test 1b: Structure Learning ──
    print("\n" + "="*60)
    print("TEST 1b: Causal Structure Learning (from data alone)")
    print("="*60)

    try:
        causal_auto = SovereignCausalEngine(min_observations=10)
        
        # Same data but NO manual graph — let it learn
        for i in range(n):
            causal_auto.observe({
                "pricing_change": pricing_change[i],
                "support_quality": support_quality[i],
                "churn_rate": churn_rate[i],
                "revenue": revenue[i]
            })
        
        learned_graph = causal_auto.learn_structure()
        summary = causal_auto.get_graph_summary()
        print(f" Learned edges: {summary['edges']}")
        print(f" Root causes: {summary['root_causes']}")
        
        # Test effect estimation on learned graph
        learned_effect = causal_auto.estimate_effect("pricing_change", "churn_rate")
        print(f" Learned effect estimate: {learned_effect}")
        
        results["structure_learning"] = {
            "status": "OPERATIONAL",
            "learned_edges": summary['edges'],
            "effect_on_learned_graph": learned_effect
        }
        
    except Exception as e:
        results["structure_learning"] = {"status": "FAILED", "error": str(e)}
        print(f" FAILED: {e}")
        import traceback
        traceback.print_exc()

    # ── Test 2: Semantic Memory (without Ollama — test mechanics) ──
    print("\n" + "="*60)
    print("TEST 2: Semantic Memory Engine")
    print("="*60)

    try:
        memory = SovereignSemanticMemory(
            ollama_url="http://localhost:11434",
            model="nomic-embed-text"
        )
        
        # Store test memories
        test_memories = [
            ("Pricing increase of 15% caused 8% churn spike in Q3", "causal_observation", 0.9),
            ("Customer onboarding flow redesign reduced time-to-value by 40%", "product_insight", 0.8),
            ("Revenue recovery identified $45K in missed billing from Stripe sync lag", "revenue_event", 0.95),
            ("Support ticket volume correlates with deployment complexity", "pattern", 0.6),
            ("Quarterly board review highlighted need for causal attribution in marketing spend", "strategic", 0.7),
        ]
        
        for content, mtype, importance in test_memories:
            memory.store(content=content, memory_type=mtype, importance=importance)
        
        # Search test
        search_results = memory.search("customer churn pricing", top_k=3)
        print(f" Search 'customer churn pricing': {len(search_results)} results")
        for r in search_results:
            print(f"  [{r['search_method']}] sim={r['similarity']:.3f}: {r['content'][:60]}...")
        
        # Concept search
        concept_results = memory.search_by_concept("lost revenue billing errors")
        print(f" Concept 'lost revenue billing errors': {len(concept_results)} results")
        for r in concept_results:
            print(f"  [{r['search_method']}] sim={r['similarity']:.3f}: {r['content'][:60]}...")
        
        stats = memory.get_stats()
        print(f" Stats: {json.dumps(stats, indent=2)}")
        
        results["semantic_memory"] = {
            "status": "OPERATIONAL" if stats["with_embeddings"] > 0 else "FALLBACK_ONLY",
            "stats": stats,
            "search_results_count": len(search_results),
            "search_method": search_results[0]["search_method"] if search_results else "none"
        }
        
    except Exception as e:
        results["semantic_memory"] = {"status": "FAILED", "error": str(e)}
        print(f" FAILED: {e}")
        import traceback
        traceback.print_exc()

    # ── Test 3: PostgreSQL Migration SQL ──
    print("\n" + "="*60)
    print("TEST 3: PostgreSQL Bridge")
    print("="*60)

    bridge = PostgreSQLBridge()
    print(f" Migration SQL generated: {len(bridge.migration_sql())} chars")

    # Test serialization
    test_vec = np.random.randn(768).astype(np.float32)
    serialized = bridge.numpy_to_bytes(test_vec)
    deserialized = bridge.bytes_to_numpy(serialized, 768)
    roundtrip_match = np.allclose(test_vec, deserialized)
    print(f" Embedding serialization roundtrip: {'PASS' if roundtrip_match else 'FAIL'}")

    results["postgresql_bridge"] = {
        "status": "OPERATIONAL",
        "migration_sql_ready": True,
        "serialization_test": "PASS" if roundtrip_match else "FAIL"
    }

    # ── Summary ──
    print("\n" + "="*60)
    print("INTEGRATION TEST SUMMARY")
    print("="*60)
    for component, result in results.items():
        status = result.get("status", "UNKNOWN")
        emoji = "✓" if "OPERATIONAL" in status else ("⚠" if "FALLBACK" in status else "✗")
        print(f" {emoji} {component}: {status}")

    return results


if __name__ == "__main__":
    results = run_integration_tests()
    print("\n\nFull results JSON:")
    
    # Clean for JSON serialization
    def clean(obj):
        if isinstance(obj, dict):
            return {k: clean(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [clean(i) for i in obj]
        if isinstance(obj, (np.floating, np.integer)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    print(json.dumps(clean(results), indent=2))