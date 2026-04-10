"""
XZENIA EVOLUTION ENGINE v1.0
Self-modifying substrate that evolves core identity and capabilities
- Multi-swarm coordination
- Core identity updating (SOUL.md, MEMORY.md, etc.)
- Fallback logic and model switching
- Auto-deployment with validation
- Continuous skill/plugin/tool generation
"""
import os
import json
import time
import logging
import threading
import asyncio
import hashlib
import uuid
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)

# ============ Evolution Types ============

class EvolutionType(Enum):
    IDENTITY = "identity"      # Update core identity (SOUL.md, etc.)
    CAPABILITY = "capability"  # Add new capabilities
    SKILL = "skill"           # Generate new skills
    TOOL = "tool"             # Create new tools
    PLUGIN = "plugin"         # Build plugins
    SWARM = "swarm"           # Evolve swarm behavior
    CORE = "core"             # Modify core system

@dataclass
class EvolutionProposal:
    id: str
    type: EvolutionType
    target: str              # What to modify
    changes: Dict            # Proposed changes
    rationale: str           # Why this change
    confidence: float        # How confident (0-1)
    validation: Dict = None  # Validation results
    approved: bool = False
    applied: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)

# ============ Core Identity Manager ============

class CoreIdentityManager:
    """
    Manages and updates core identity files
    SOUL.md, MEMORY.md, USER.md, AGENTS.md, BRIDGE.md
    """
    
    def __init__(self, workspace: str = None):
        self.workspace = workspace or os.path.expanduser("~/.openclaw/workspace")
        self.files = {
            'SOUL.md': os.path.join(self.workspace, 'SOUL.md'),
            'MEMORY.md': os.path.join(self.workspace, 'MEMORY.md'),
            'USER.md': os.path.join(self.workspace, 'USER.md'),
            'AGENTS.md': os.path.join(self.workspace, 'AGENTS.md'),
            'BRIDGE.md': os.path.join(self.workspace, 'BRIDGE.md'),
            'IDENTITY.md': os.path.join(self.workspace, 'IDENTITY.md'),
            'TOOLS.md': os.path.join(self.workspace, 'TOOLS.md'),
        }
        self._lock = threading.RLock()
        self._change_history: List[Dict] = []
        
        logger.info("Core Identity Manager initialized")
    
    def read_file(self, name: str) -> str:
        """Read a core file"""
        path = self.files.get(name)
        if path and os.path.exists(path):
            with open(path, 'r') as f:
                return f.read()
        return ""
    
    def write_file(self, name: str, content: str, validate: bool = True) -> bool:
        """Write to a core file with optional validation"""
        if not validate or self._validate_change(name, content):
            path = self.files.get(name)
            if path:
                # Backup before write
                backup_path = f"{path}.backup.{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
                if os.path.exists(path):
                    import shutil
                    shutil.copy(path, backup_path)
                
                with open(path, 'w') as f:
                    f.write(content)
                
                # Record change
                self._record_change(name, content)
                
                logger.info(f"Updated core file: {name}")
                return True
        return False
    
    def _validate_change(self, name: str, content: str) -> bool:
        """Validate a proposed change"""
        # Basic sanity checks
        if not content:
            return False
        
        # Ensure required sections exist for key files
        if name == 'SOUL.md':
            required = ['Core Truths', 'Boundaries', 'Vibe']
            return all(section in content for section in required)
        
        if name == 'MEMORY.md':
            required = ['xzenia:declaration']
            return all(section in content for section in required)
        
        return True
    
    def _record_change(self, name: str, content: str):
        """Record change in history"""
        self._change_history.append({
            "file": name,
            "timestamp": datetime.utcnow().isoformat(),
            "hash": hashlib.sha256(content.encode()).hexdigest()[:16]
        })
    
    def get_state(self) -> Dict:
        """Get current state of all core files"""
        return {
            "files": {name: os.path.exists(path) for name, path in self.files.items()},
            "changes": len(self._change_history),
            "last_change": self._change_history[-1] if self._change_history else None
        }

# ============ Fallback System ============

class FallbackSystem:
    """
    Manages fallbacks between models, tools, strategies
    Knows when to switch before limits hit
    """
    
    def __init__(self):
        self.fallbacks: Dict[str, List[Dict]] = {}
        self._current_fallback: Dict[str, str] = {}
        self._metrics: Dict[str, List[float]] = {}
        self._limits: Dict[str, int] = {
            "token_limit": 8000,
            "time_limit": 30,
            "error_limit": 3,
            "rate_limit": 100
        }
        
        self._init_standard_fallbacks()
        
        logger.info("Fallback System initialized")
    
    def _init_standard_fallbacks(self):
        """Initialize standard fallback chains"""
        self.fallbacks = {
            "model": [
                {"model": "minimax-portal/MiniMax-M2.5-highspeed", "priority": 1},
                {"model": "minimax-portal/MiniMax-M2.5", "priority": 2},
                {"model": "qwen-portal/coder-model", "priority": 3},
                {"model": "ollama/qwen2.5:7b", "priority": 4}
            ],
            "tool": [
                {"tool": "exec", "fallback": "subagent"},
                {"tool": "subagent", "fallback": "sessions_send"}
            ],
            "strategy": [
                {"strategy": "direct", "fallback": "search"},
                {"strategy": "search", "fallback": "memory"}
            ]
        }
    
    def should_fallback(self, category: str, metrics: Dict) -> bool:
        """Determine if fallback is needed based on metrics"""
        if category == "model":
            # Check token usage
            tokens = metrics.get("tokens", 0)
            if tokens > self._limits["token_limit"] * 0.8:
                return True
            
            # Check error rate
            errors = metrics.get("errors", 0)
            if errors > self._limits["error_limit"]:
                return True
        
        elif category == "tool":
            # Check tool failures
            failures = metrics.get("failures", 0)
            if failures > 2:
                return True
        
        return False
    
    def get_fallback(self, category: str) -> Optional[Dict]:
        """Get next fallback option"""
        current = self._current_fallback.get(category)
        chain = self.fallbacks.get(category, [])
        
        if not current:
            return chain[0] if chain else None
        
        # Find next in chain
        for i, option in enumerate(chain):
            if option.get("model") == current or option.get("tool") == current:
                if i + 1 < len(chain):
                    return chain[i + 1]
        
        return None
    
    def set_fallback(self, category: str, value: str):
        """Set current fallback"""
        self._current_fallback[category] = value
    
    def record_metric(self, category: str, value: float):
        """Record metric for decision making"""
        if category not in self._metrics:
            self._metrics[category] = []
        self._metrics[category].append(value)
        # Keep only last 100
        if len(self._metrics[category]) > 100:
            self._metrics[category] = self._metrics[category][-100:]
    
    def get_stats(self) -> Dict:
        """Get fallback stats"""
        return {
            "current": self._current_fallback,
            "chains": {k: len(v) for k, v in self.fallbacks.items()},
            "metrics": {k: sum(v)/len(v) if v else 0 for k, v in self._metrics.items()}
        }

# ============ Multi-Swarm Coordinator ============

class MultiSwarmCoordinator:
    """
    Coordinates multiple swarms working together
    Each swarm has specialized purpose
    """
    
    def __init__(self):
        self.swarms: Dict[str, Any] = {}  # swarm_id -> swarm instance
        self.swarm_types: Dict[str, str] = {}  # swarm_id -> type
        self._coordination_queue: asyncio.Queue = asyncio.Queue()
        
        logger.info("Multi-Swarm Coordinator initialized")
    
    def register_swarm(self, swarm_id: str, swarm: Any, swarm_type: str):
        """Register a swarm"""
        self.swarms[swarm_id] = swarm
        self.swarm_types[swarm_id] = swarm_type
        logger.info(f"Registered swarm: {swarm_id} ({swarm_type})")
    
    async def coordinate(self) -> Dict:
        """Coordinate between swarms"""
        results = {}
        
        # Run cycles for all registered swarms
        for swarm_id, swarm in self.swarms.items():
            try:
                result = await swarm.run_cycle()
                results[swarm_id] = {
                    "type": self.swarm_types[swarm_id],
                    "status": "success",
                    "knowledge": len(swarm.knowledge.nodes)
                }
            except Exception as e:
                results[swarm_id] = {
                    "type": self.swarm_types[swarm_id],
                    "status": "error",
                    "error": str(e)
                }
        
        return results
    
    def get_swarm_count(self) -> int:
        """Get number of active swarms"""
        return len(self.swarms)

# ============ Validation Engine ============

class ValidationEngine:
    """
    Validates proposed changes before application
    Ensures logical coherence and safety
    """
    
    def __init__(self, identity_manager: CoreIdentityManager):
        self.identity = identity_manager
        self.validation_rules: List[Callable] = []
        
        self._init_rules()
        
        logger.info("Validation Engine initialized")
    
    def _init_rules(self):
        """Initialize validation rules"""
        self.validation_rules = [
            self._validate_soul_structure,
            self._validate_memory_integrity,
            self._validate_no_contradiction,
            self._validate_safety_bounds
        ]
    
    async def validate_proposal(self, proposal: EvolutionProposal) -> Dict:
        """Validate an evolution proposal"""
        results = {
            "proposal_id": proposal.id,
            "type": proposal.type.value,
            "passed": True,
            "checks": [],
            "warnings": []
        }
        
        # Run all validation rules
        for rule in self.validation_rules:
            try:
                check_result = await rule(proposal)
                results["checks"].append(check_result)
                if not check_result["passed"]:
                    results["passed"] = False
            except Exception as e:
                results["warnings"].append(f"Check error: {e}")
        
        # Type-specific validation
        if proposal.type == EvolutionType.IDENTITY:
            identity_result = self._validate_identity_change(proposal)
            results["checks"].append(identity_result)
            if not identity_result["passed"]:
                results["passed"] = False
        
        proposal.validation = results
        
        return results
    
    async def _validate_soul_structure(self, proposal: EvolutionProposal) -> Dict:
        """Validate SOUL.md structure"""
        if proposal.target == "SOUL.md":
            content = proposal.changes.get("content", "")
            required = ["Core Truths", "Boundaries", "Vibe"]
            missing = [r for r in required if r not in content]
            
            return {
                "rule": "soul_structure",
                "passed": len(missing) == 0,
                "details": f"Missing sections: {missing}" if missing else "OK"
            }
        return {"rule": "soul_structure", "passed": True, "details": "N/A"}
    
    async def _validate_memory_integrity(self, proposal: EvolutionProposal) -> Dict:
        """Validate MEMORY.md integrity"""
        if proposal.target == "MEMORY.md":
            content = proposal.changes.get("content", "")
            
            # Check for xzenia:declaration
            has_declaration = "xzenia:declaration" in content
            
            return {
                "rule": "memory_integrity",
                "passed": has_declaration,
                "details": "Has declaration" if has_declaration else "Missing declaration"
            }
        return {"rule": "memory_integrity", "passed": True, "details": "N/A"}
    
    async def _validate_no_contradiction(self, proposal: EvolutionProposal) -> Dict:
        """Check for contradictions with existing identity"""
        # Read current state
        current_soul = self.identity.read_file("SOUL.md")
        
        # Check for key identity markers
        identity_markers = ["Xzenia", "Co-Architect", "sharp", "sovereign"]
        
        new_content = proposal.changes.get("content", "")
        
        # If removing core identity markers, warn
        for marker in identity_markers:
            if marker in current_soul and marker not in new_content:
                return {
                    "rule": "no_contradiction",
                    "passed": False,
                    "details": f"Removing core marker: {marker}"
                }
        
        return {"rule": "no_contradiction", "passed": True, "details": "OK"}
    
    async def _validate_safety_bounds(self, proposal: EvolutionProposal) -> Dict:
        """Ensure changes are within safety bounds"""
        # Never allow: full reset, removal of safety rules
        dangerous_patterns = [
            r"delete.*memory",
            r"reset.*identity",
            r"remove.*safety"
        ]
        
        content = str(proposal.changes)
        
        for pattern in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return {
                    "rule": "safety_bounds",
                    "passed": False,
                    "details": f"Dangerous pattern detected: {pattern}"
                }
        
        return {"rule": "safety_bounds", "passed": True, "details": "OK"}
    
    def _validate_identity_change(self, proposal: EvolutionProposal) -> Dict:
        """Validate identity-specific changes"""
        # Ensure identity elements are preserved
        required_elements = ["Name:", "Creature:", "Vibe:", "Emoji:"]
        
        content = proposal.changes.get("content", "")
        
        missing = [e for e in required_elements if e not in content]
        
        return {
            "rule": "identity_change",
            "passed": len(missing) == 0,
            "details": f"Missing: {missing}" if missing else "OK"
        }

# ============ Tool/Plugin Factory ============

class ToolPluginFactory:
    """
    Creates tools, plugins, and utilities
    """
    
    def __init__(self):
        self.tools: Dict[str, Dict] = {}
        self.plugins: Dict[str, Dict] = {}
        
        logger.info("Tool/Plugin Factory initialized")
    
    def create_tool(self, name: str, spec: Dict) -> str:
        """Create a new tool"""
        tool_id = str(uuid.uuid4())
        
        self.tools[tool_id] = {
            "id": tool_id,
            "name": name,
            "spec": spec,
            "created": datetime.utcnow().isoformat(),
            "usage": 0
        }
        
        return tool_id
    
    def create_plugin(self, name: str, plugin_type: str, capabilities: List[str]) -> str:
        """Create a new plugin"""
        plugin_id = str(uuid.uuid4())
        
        self.plugins[plugin_id] = {
            "id": plugin_id,
            "name": name,
            "type": plugin_type,
            "capabilities": capabilities,
            "created": datetime.utcnow().isoformat(),
            "active": True
        }
        
        return plugin_id
    
    def get_all(self) -> Dict:
        """Get all created tools and plugins"""
        return {
            "tools": self.tools,
            "plugins": self.plugins
        }

# ============ Evolution Orchestrator ============

class EvolutionOrchestrator:
    """
    Main orchestrator for system evolution
    Coordinates all subsystems
    """
    
    def __init__(self, workspace: str = None):
        self.workspace = workspace or os.path.expanduser("~/.openclaw/workspace")
        
        # Core subsystems
        self.identity = CoreIdentityManager(self.workspace)
        self.fallback = FallbackSystem()
        self.coordinator = MultiSwarmCoordinator()
        self.validator = ValidationEngine(self.identity)
        self.factory = ToolPluginFactory()
        
        # Evolution state
        self.proposals: Dict[str, EvolutionProposal] = {}
        self._evolution_thread = None
        self._running = False
        
        # Import swarm components
        self._setup_swarms()
        
        logger.info("Evolution Orchestrator initialized")
    
    def _setup_swarms(self):
        """Setup integrated swarms"""
        try:
            import sys
            sys.path.insert(0, self.workspace)
            from projects.xzenia.swarm.swarm_orchestrator import get_swarm
            from projects.xzenia.swarm.meta_cognition_loop import get_meta_loop
            
            # Main evolution swarm
            self.main_swarm = get_swarm()
            self.meta_loop = get_meta_loop()
            
            # Register with coordinator
            self.coordinator.register_swarm("main", self.main_swarm, "evolution")
            self.coordinator.register_swarm("meta", self.meta_loop, "meta_cognition")
            
            logger.info("Swarms registered with evolution orchestrator")
            
        except Exception as e:
            logger.warning(f"Could not setup swarms: {e}")
    
    async def create_proposal(self, evo_type: EvolutionType, target: str, changes: Dict, rationale: str) -> EvolutionProposal:
        """Create an evolution proposal"""
        proposal = EvolutionProposal(
            id=str(uuid.uuid4()),
            type=evo_type,
            target=target,
            changes=changes,
            rationale=rationale,
            confidence=0.7
        )
        
        # Validate proposal
        validation = await self.validator.validate_proposal(proposal)
        
        # Auto-approve if high confidence and validation passes
        if validation["passed"] and proposal.confidence > 0.8:
            proposal.approved = True
        
        self.proposals[proposal.id] = proposal
        
        return proposal
    
    async def apply_proposal(self, proposal_id: str) -> bool:
        """Apply an approved proposal"""
        proposal = self.proposals.get(proposal_id)
        
        if not proposal or not proposal.approved:
            return False
        
        # Apply based on type
        if proposal.type == EvolutionType.IDENTITY:
            return self._apply_identity_change(proposal)
        elif proposal.type == EvolutionType.CAPABILITY:
            return self._apply_capability(proposal)
        elif proposal.type == EvolutionType.SKILL:
            return self._apply_skill(proposal)
        elif proposal.type == EvolutionType.CORE:
            return self._apply_core_change(proposal)
        
        return False
    
    def _apply_identity_change(self, proposal: EvolutionProposal) -> bool:
        """Apply identity file change"""
        filename = proposal.target
        content = proposal.changes.get("content", "")
        
        return self.identity.write_file(filename, content)
    
    def _apply_capability(self, proposal: EvolutionProposal) -> bool:
        """Apply new capability"""
        capability = proposal.changes.get("capability")
        
        # Add to TOOLS.md
        tools_path = os.path.join(self.workspace, "TOOLS.md")
        if os.path.exists(tools_path):
            with open(tools_path, 'a') as f:
                f.write(f"\n### {capability['name']}\n- {capability['description']}\n")
        
        return True
    
    def _apply_skill(self, proposal: EvolutionProposal) -> bool:
        """Apply new skill"""
        skill = proposal.changes.get("skill")
        
        # Save to workspace skills
        skill_path = os.path.join(self.workspace, "skills", skill["name"])
        os.makedirs(skill_path, exist_ok=True)
        
        # Create manifest
        with open(os.path.join(skill_path, "manifest.json"), 'w') as f:
            json.dump(skill, f, indent=2)
        
        # Create SKILL.md
        with open(os.path.join(skill_path, "SKILL.md"), 'w') as f:
            f.write(f"# {skill['name']}\n\n{skill.get('description', '')}\n")
        
        return True
    
    def _apply_core_change(self, proposal: EvolutionProposal) -> bool:
        """Apply core system change"""
        changes = proposal.changes
        
        # Handle various core changes
        if "update_file" in changes:
            return self.identity.write_file(
                changes["update_file"]["name"],
                changes["update_file"]["content"]
            )
        
        return False
    
    async def run_evolution_cycle(self) -> Dict:
        """Run one evolution cycle"""
        cycle_id = str(uuid.uuid4())
        
        results = {
            "cycle_id": cycle_id,
            "timestamp": datetime.utcnow().isoformat(),
            "swarm_coordination": {},
            "proposals": len(self.proposals),
            "fallback_stats": self.fallback.get_stats(),
            "identity_state": self.identity.get_state()
        }
        
        # Coordinate swarms
        if hasattr(self, 'main_swarm'):
            swarm_result = await self.main_swarm.run_cycle()
            results["swarm_coordination"]["main"] = swarm_result.get("knowledge_nodes", 0)
        
        # Run meta-cognition
        if hasattr(self, 'meta_loop'):
            meta_result = await self.meta_loop.run_once()
            results["meta_level"] = meta_result["meta"]["level"]
        
        # Generate evolution proposal if warranted
        if len(self.proposals) < 10:  # Limit proposals
            proposal = await self._generate_evolution_proposal()
            if proposal:
                results["new_proposal"] = proposal.id
        
        return results
    
    async def _generate_evolution_proposal(self) -> Optional[EvolutionProposal]:
        """Generate an evolution proposal"""
        # Analyze current state
        identity_state = self.identity.get_state()
        
        # Check if identity needs updating
        current_soul = self.identity.read_file("SOUL.md")
        
        # Example: Add new swarm features if not present
        if "Swarm Substrate" not in current_soul:
            return await self.create_proposal(
                EvolutionType.IDENTITY,
                "SOUL.md",
                {"content": current_soul + "\n\n**Swarm Evolution:** Active\n"},
                "Add swarm evolution capability to identity"
            )
        
        return None
    
    def get_status(self) -> Dict:
        """Get evolution system status"""
        return {
            "proposals_total": len(self.proposals),
            "proposals_approved": len([p for p in self.proposals.values() if p.approved]),
            "swarms": self.coordinator.get_swarm_count(),
            "fallback": self.fallback.get_stats(),
            "identity": self.identity.get_state(),
            "tools": len(self.factory.tools),
            "plugins": len(self.factory.plugins)
        }

# ============ Auto-Deployer ============

class AutoDeployer:
    """
    Handles automatic deployment and updates
    """
    
    def __init__(self, orchestrator: EvolutionOrchestrator):
        self.orchestrator = orchestrator
        self._deploy_thread = None
        self._running = False
        
        logger.info("Auto-Deployer initialized")
    
    def start(self):
        """Start auto-deployment"""
        if self._running:
            return
        
        self._running = True
        self._deploy_thread = threading.Thread(target=self._deploy_loop, daemon=True)
        self._deploy_thread.start()
        
        logger.info("Auto-Deployer started")
    
    def _deploy_loop(self):
        """Background deployment loop"""
        while self._running:
            try:
                # Create new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                # Run evolution cycle
                result = loop.run_until_complete(
                    self.orchestrator.run_evolution_cycle()
                )
                
                # Apply approved proposals
                for proposal_id, proposal in self.orchestrator.proposals.items():
                    if proposal.approved and not proposal.applied:
                        applied = loop.run_until_complete(
                            self.orchestrator.apply_proposal(proposal_id)
                        )
                        if applied:
                            proposal.applied = True
                
                loop.close()
                
            except Exception as e:
                logger.error(f"Deploy loop error: {e}")
            
            # Run every 15 minutes
            time.sleep(900)
    
    def stop(self):
        """Stop auto-deployment"""
        self._running = False
        if self._deploy_thread:
            self._deploy_thread.join(timeout=5)

# ============ Singleton ============

_orchestrator: Optional[EvolutionOrchestrator] = None
_deployer: Optional[AutoDeployer] = None

def get_evolution_orchestrator() -> EvolutionOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = EvolutionOrchestrator()
    return _orchestrator

def get_deployer() -> AutoDeployer:
    global _deployer
    if _deployer is None:
        _deployer = AutoDeployer(get_evolution_orchestrator())
    return _deployer

def init_evolution_system():
    """Initialize the evolution system"""
    orch = get_evolution_orchestrator()
    deployer = get_deployer()
    deployer.start()
    
    return orch, deployer