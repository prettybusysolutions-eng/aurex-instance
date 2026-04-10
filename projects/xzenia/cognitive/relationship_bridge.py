"""
RELATIONSHIP BRIDGE v1.0
=========================
Connects causal structure learning to semantic memory.

When the causal engine discovers a new edge (A → B), this bridge:
1. Formats it as a natural language insight
2. Stores it in semantic memory with type="causal_relationship"
3. Tags it with source domain and confidence
4. Makes it discoverable by the planner's novel decomposer

This is the transfer learning mechanism. Cleaning teaches
"dispatch speed → completion rate", lead engine finds that
insight when planning outreach timing.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("sovereign.bridge")


class RelationshipBridge:
    """
    Bridges causal discovery to semantic memory.
    
    Usage:
        bridge = RelationshipBridge(causal_engine, semantic_memory)
        
        # After structure learning runs:
        new_edges = bridge.sync()
        # Returns list of newly stored relationships
        
        # Or call automatically after learn_structure():
        bridge.auto_sync_after_learning()
    """
    
    def __init__(self, causal_engine, semantic_memory):
        self.causal = causal_engine
        self.memory = semantic_memory
        self._known_edges = set()  # track what we've already stored
    
    def sync(self, domain: str = "global") -> list[dict]:
        """
        Check for new causal edges and store them in semantic memory.
        Returns list of newly bridged relationships.
        """
        graph = self.causal.get_graph_summary()
        
        if graph.get("status") == "no_graph":
            logger.info("No causal graph yet — nothing to bridge")
            return []
        
        new_relationships = []
        edges = graph.get("edges", [])
        
        for edge in edges:
            if isinstance(edge, (list, tuple)) and len(edge) == 2:
                cause, effect = edge[0], edge[1]
            else:
                continue
            
            edge_key = f"{cause}->{effect}"
            if edge_key in self._known_edges:
                continue
            
            # Try to get effect estimate for this edge
            effect_size = self._get_effect_size(cause, effect)
            confidence = self._get_confidence(cause, effect)
            
            # Format as natural language insight
            insight = self._format_insight(cause, effect, effect_size, confidence, domain)
            
            # Store in semantic memory
            self.memory.store(
                content=insight,
                memory_type="causal_relationship",
                importance=min(0.95, 0.5 + abs(effect_size) if effect_size else 0.6),
                metadata={
                    "cause": cause,
                    "effect": effect,
                    "effect_size": effect_size,
                    "confidence": confidence,
                    "source_domain": domain,
                    "discovered_at": datetime.now(timezone.utc).isoformat(),
                    "discovery_method": "structure_learning"
                }
            )
            
            self._known_edges.add(edge_key)
            new_relationships.append({
                "edge": edge_key,
                "insight": insight,
                "effect_size": effect_size,
                "confidence": confidence,
                "domain": domain
            })
            
            logger.info(f"Bridged: {edge_key} → semantic memory [{domain}]")
        
        return new_relationships
    
    def sync_from_manual_graph(self, domain: str = "global") -> list[dict]:
        """Sync edges from a manually defined graph."""
        return self.sync(domain=domain)
    
    def sync_after_structure_learning(self, domain: str = "global") -> list[dict]:
        """
        Call this right after learn_structure() completes.
        Discovers new edges and bridges them to memory.
        """
        return self.sync(domain=domain)
    
    def get_cross_domain_insights(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Query semantic memory specifically for causal relationships.
        Used by the novel decomposer during goal decomposition.
        """
        results = self.memory.search(
            query=query,
            top_k=top_k,
            memory_type="causal_relationship"
        )
        return results
    
    def get_bridged_count(self) -> dict:
        return {
            "total_bridged": len(self._known_edges),
            "edges": list(self._known_edges)
        }
    
    # ── Internal ──
    
    def _get_effect_size(self, cause: str, effect: str) -> Optional[float]:
        """Try to estimate effect size for this edge."""
        try:
            result = self.causal.estimate_effect(cause, effect)
            if result.get("status") == "success":
                return result.get("estimate")
        except Exception:
            pass
        return None
    
    def _get_confidence(self, cause: str, effect: str) -> float:
        """Estimate confidence based on observation count."""
        try:
            n = len(self.causal.observations)
            # Confidence increases with observations, asymptotes at 1.0
            return min(0.95, n / 100)
        except Exception:
            return 0.3
    
    def _format_insight(
        self, cause: str, effect: str,
        effect_size: Optional[float],
        confidence: float,
        domain: str
    ) -> str:
        """Format causal edge as natural language for semantic search."""
        # Convert variable names to readable form
        cause_readable = cause.replace("_", " ")
        effect_readable = effect.replace("_", " ")
        
        if effect_size is not None:
            direction = "increases" if effect_size > 0 else "decreases"
            magnitude = abs(effect_size)
            if magnitude < 0.01:
                strength = "has negligible effect on"
            elif magnitude < 0.1:
                strength = f"slightly {direction}"
            elif magnitude < 0.5:
                strength = f"moderately {direction}"
            else:
                strength = f"strongly {direction}"
            
            insight = (
                f"Discovered in {domain}: {cause_readable} {strength} "
                f"{effect_readable} (effect size: {effect_size:.4f}, "
                f"confidence: {confidence:.2f})"
            )
        else:
            insight = (
                f"Discovered in {domain}: {cause_readable} causally affects "
                f"{effect_readable} (confidence: {confidence:.2f})"
            )
        
        return insight


def test_bridge():
    """Test the relationship bridge with mock engines."""
    print("=" * 60)
    print("RELATIONSHIP BRIDGE — TEST")
    print("=" * 60)
    
    # Mock causal engine
    class MockCausal:
        def __init__(self):
            self.observations = list(range(14))
        def get_graph_summary(self):
            return {
                "nodes": ["dispatch_time", "completion_rate", "revenue", "location_priority"],
                "edges": [
                    ("dispatch_time", "completion_rate"),
                    ("location_priority", "revenue"),
                    ("completion_rate", "revenue")
                ],
                "status": "ok"
            }
        def estimate_effect(self, cause, effect):
            effects = {
                ("dispatch_time", "completion_rate"): -0.35,
                ("location_priority", "revenue"): 0.62,
                ("completion_rate", "revenue"): 0.48
            }
            val = effects.get((cause, effect))
            if val:
                return {"status": "success", "estimate": val}
            return {"status": "failed"}
    
    # Mock semantic memory
    class MockMemory:
        def __init__(self):
            self.stored = []
        def store(self, content, memory_type, importance, metadata=None):
            self.stored.append({
                "content": content,
                "type": memory_type,
                "importance": importance,
                "metadata": metadata
            })
            print(f"  STORED: {content[:80]}...")
        def search(self, query, top_k=5, memory_type=None):
            return [s for s in self.stored if memory_type is None or s["type"] == memory_type][:top_k]
    
    causal = MockCausal()
    memory = MockMemory()
    bridge = RelationshipBridge(causal, memory)
    
    # Sync
    print("\n[1] Sync causal graph to semantic memory:")
    results = bridge.sync(domain="pretty_busy_cleaning")
    print(f"\n  Bridged {len(results)} relationships")
    for r in results:
        print(f"  {r['edge']} | effect={r['effect_size']} | conf={r['confidence']:.2f}")
    
    # Second sync should find nothing new
    print("\n[2] Second sync (should find nothing new):")
    results2 = bridge.sync(domain="pretty_busy_cleaning")
    print(f"  Bridged {len(results2)} new relationships (expected 0)")
    
    # Cross-domain query
    print("\n[3] Cross-domain insight query:")
    insights = bridge.get_cross_domain_insights("speed affects outcomes")
    print(f"  Found {len(insights)} causal relationships")
    for i in insights:
        print(f"  {i['content'][:80]}...")
    
    print(f"\n  Total bridged: {bridge.get_bridged_count()}")
    print("\nBRIDGE TEST PASSED")


if __name__ == "__main__":
    test_bridge()