#!/usr/bin/env python3
"""
Simplified Backend API for EvolDSL Frontend Demo
This version provides a working demo without requiring the full MCTS/Evolution dependencies
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import uuid
import random

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="EvolDSL Backend API (Demo)", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
active_sessions: Dict[str, 'EvolutionSession'] = {}
websocket_connections: List[WebSocket] = []

# Data models
@dataclass
class MCTSNodeData:
    id: str
    state: Dict[str, Any]
    parent: Optional[str]
    children: List[str]
    visits: int
    total_reward: float
    ucb_score: float
    is_expanded: bool
    is_selected: bool
    action: Optional[Dict[str, Any]]
    depth: int

@dataclass
class EvolutionCandidateData:
    id: str
    function: Dict[str, Any]
    generation: int
    parent_functions: List[str]
    fitness: float
    is_selected: bool
    mutation_strategy: Optional[str]

@dataclass
class EvolutionGenerationData:
    generation: int
    population: List[EvolutionCandidateData]
    best_fitness: float
    average_fitness: float
    new_mutations: List[str]
    timestamp: int

class EvolutionSession:
    """Demo evolution session with simulated data"""
    
    def __init__(self, session_id: str, configs: Dict[str, Any]):
        self.session_id = session_id
        self.configs = configs
        self.is_running = False
        self.current_phase = "idle"
        self.progress = {"current": 0, "total": 0, "phase": "Idle"}
        self.costs = {"total_cost": 0, "mcts_phase": 0, "evolution_phase": 0}
        
        # Data storage
        self.mcts_tree: Dict[str, MCTSNodeData] = {}
        self.mcts_root: Optional[str] = None
        self.mcts_iterations: List[Dict[str, Any]] = []
        self.evolution_generations: List[EvolutionGenerationData] = []
        self.current_generation = 0
        
    async def start_evolution(self):
        """Start the demo evolution process"""
        if self.is_running:
            raise HTTPException(status_code=400, detail="Evolution already running")
        
        # Check for API key in environment or config
        api_key = os.environ.get('OPENAI_API_KEY') or self.configs.get('gpt4o_config', {}).get('apiKey')
        if not api_key:
            # For demo purposes, we'll continue without API key but log the issue
            logger.warning("No OpenAI API key found in environment or config, running demo mode")
        else:
            logger.info("OpenAI API key found, running with GPT-4o integration")
        
        self.is_running = True
        self.current_phase = "initializing"
        
        try:
            await self._broadcast_status_update()
            
            # Run MCTS phase
            await self._run_mcts_phase()
            
            # Run Evolution phase  
            await self._run_evolution_phase()
            
            self.current_phase = "completed"
            self.is_running = False
            
        except Exception as e:
            logger.error(f"Evolution failed: {str(e)}")
            self.current_phase = "error"
            self.is_running = False
            raise
        
        await self._broadcast_status_update()
    
    async def _run_mcts_phase(self):
        """Run simulated MCTS search phase"""
        self.current_phase = "mcts"
        mcts_config = self.configs["mcts_config"]
        
        self.progress = {
            "current": 0,
            "total": mcts_config["iterations"],
            "phase": "MCTS Search"
        }
        await self._broadcast_status_update()
        
        # Create root node
        root_node = MCTSNodeData(
            id="root",
            state={
                "functionName": "evolved_func",
                "params": ["x", "y"],
                "returnType": "int",
                "bodyTokens": [],
                "isComplete": False,
                "depth": 0,
                "code": ""
            },
            parent=None,
            children=[],
            visits=0,
            total_reward=0.0,
            ucb_score=0.0,
            is_expanded=False,
            is_selected=False,
            action=None,
            depth=0
        )
        
        self.mcts_tree["root"] = root_node
        self.mcts_root = "root"
        
        # Simulate MCTS iterations
        for i in range(mcts_config["iterations"]):
            await self._simulate_mcts_iteration(i)
            
            self.progress["current"] = i + 1
            await self._broadcast_status_update()
            
            # Small delay for visualization
            await asyncio.sleep(0.1)
    
    async def _run_evolution_phase(self):
        """Run simulated evolution phase"""
        self.current_phase = "evolution"
        evolution_config = self.configs["evolution_config"]
        
        self.progress = {
            "current": 0,
            "total": evolution_config["generations"],
            "phase": "Evolution"
        }
        await self._broadcast_status_update()
        
        for gen in range(evolution_config["generations"]):
            await self._simulate_evolution_generation(gen)
            
            self.progress["current"] = gen + 1
            await self._broadcast_status_update()
            
            await asyncio.sleep(0.3)
    
    async def _simulate_mcts_iteration(self, iteration: int):
        """Simulate realistic MCTS iteration building target function"""
        
        # Get target task from config
        target_task = self.configs.get('mcts_config', {}).get('targetTask', 'factorial')
        
        # Define sequences for different functions
        if target_task == 'fibonacci':
            building_sequence = [
                {"action": "define_function", "desc": "Define fibonacci function", "tokens": ["def", "fibonacci(n):"], "depth": 0},
                {"action": "add_base_case", "desc": "Add base case n < 2", "tokens": ["if", "lt(n,", "2):"], "depth": 1},
                {"action": "return_n", "desc": "Return n for base case", "tokens": ["return", "n"], "depth": 2},
                {"action": "add_else_clause", "desc": "Add else clause", "tokens": ["else:"], "depth": 1},
                {"action": "recursive_call", "desc": "Add recursive sum", "tokens": ["return", "add(fibonacci(sub(n,", "1)),"], "depth": 2},
                {"action": "second_call", "desc": "Add second recursive call", "tokens": ["fibonacci(sub(n,", "2)))"], "depth": 3},
            ]
        elif target_task == 'power':
            building_sequence = [
                {"action": "define_function", "desc": "Define power function", "tokens": ["def", "power(base,", "exp):"], "depth": 0},
                {"action": "add_base_case", "desc": "Add base case exp = 0", "tokens": ["if", "eq(exp,", "0):"], "depth": 1},
                {"action": "return_one", "desc": "Return 1 for base case", "tokens": ["return", "1"], "depth": 2},
                {"action": "add_else_clause", "desc": "Add else clause", "tokens": ["else:"], "depth": 1},
                {"action": "recursive_call", "desc": "Add recursive multiplication", "tokens": ["return", "mul(base,", "power(base,"], "depth": 2},
                {"action": "subtract_exp", "desc": "Subtract 1 from exp", "tokens": ["sub(exp,", "1)))"], "depth": 3},
            ]
        elif target_task == 'gcd':
            building_sequence = [
                {"action": "define_function", "desc": "Define GCD function", "tokens": ["def", "gcd(a,", "b):"], "depth": 0},
                {"action": "add_base_case", "desc": "Add base case b = 0", "tokens": ["if", "eq(b,", "0):"], "depth": 1},
                {"action": "return_a", "desc": "Return a for base case", "tokens": ["return", "a"], "depth": 2},
                {"action": "add_else_clause", "desc": "Add else clause", "tokens": ["else:"], "depth": 1},
                {"action": "recursive_call", "desc": "Add recursive GCD call", "tokens": ["return", "gcd(b,", "mod(a,"], "depth": 2},
                {"action": "modulo_op", "desc": "Add modulo operation", "tokens": ["b))"], "depth": 3},
            ]
        else:  # factorial (default)
            building_sequence = [
            # Root level - function signature
            {"action": "define_function", "desc": "Define factorial function", "tokens": ["def", "factorial(n):"], "depth": 0},
            
            # Base case branch
            {"action": "add_base_case", "desc": "Add base case check", "tokens": ["if", "eq(n,", "0):"], "depth": 1},
            {"action": "return_one", "desc": "Return 1 for base case", "tokens": ["return", "1"], "depth": 2},
            
            # Recursive case branch  
            {"action": "add_else_clause", "desc": "Add else clause", "tokens": ["else:"], "depth": 1},
            {"action": "recursive_call", "desc": "Add recursive multiplication", "tokens": ["return", "mul(n,", "factorial("], "depth": 2},
            {"action": "subtract_one", "desc": "Subtract 1 from n", "tokens": ["sub(n,", "1))"], "depth": 3},
            
            # Optimization branches
            {"action": "add_memoization", "desc": "Consider memoization", "tokens": ["memo", "=", "{}"], "depth": 1},
            {"action": "check_memo", "desc": "Check if result cached", "tokens": ["if", "n", "in", "memo:"], "depth": 2},
            {"action": "return_cached", "desc": "Return cached result", "tokens": ["return", "memo[n]"], "depth": 3},
            
            # Error handling
            {"action": "add_validation", "desc": "Add input validation", "tokens": ["if", "lt(n,", "0):"], "depth": 1},
            {"action": "raise_error", "desc": "Raise error for negative", "tokens": ["raise", "ValueError"], "depth": 2},
        ]
        
        # Get current step in sequence (cycling through)
        step_index = iteration % len(building_sequence)
        step = building_sequence[step_index]
        
        # Create meaningful node ID
        node_id = f"{target_task}_{step['action']}_{iteration}"
        
        # Select parent based on tree structure being built
        parent_id = self._select_mcts_parent(iteration, step)
        
        # Calculate realistic fitness/reward based on how "good" this step is
        reward = self._calculate_step_reward(step, iteration)
        
        # Build cumulative code
        current_code = self._build_cumulative_code(iteration, step)
        
        # Set parameters based on function type
        if target_task == 'power':
            params = ["base", "exp"]
        elif target_task == 'gcd':
            params = ["a", "b"]
        else:
            params = ["n"]
            
        state = {
            "functionName": target_task,
            "params": params,
            "returnType": "int", 
            "bodyTokens": step["tokens"],
            "isComplete": step["action"] in ["subtract_one", "return_cached", "raise_error", "second_call", "subtract_exp", "modulo_op"],
            "depth": step["depth"],
            "code": current_code
        }
        
        # Create node with realistic UCB score calculation
        visits = max(1, 20 - step["depth"] * 3 + random.randint(-2, 5))
        total_reward = reward * visits + random.uniform(-0.5, 0.5)
        ucb_score = self._calculate_ucb_score(total_reward, visits, iteration)
        
        node_data = MCTSNodeData(
            id=node_id,
            state=state,
            parent=parent_id,
            children=[],
            visits=visits,
            total_reward=total_reward,
            ucb_score=ucb_score,
            is_expanded=step["depth"] < 3,
            is_selected=False,
            action={
                "actionType": step["action"],
                "value": " ".join(step["tokens"]),
                "description": step["desc"]
            },
            depth=step["depth"]
        )
        
        self.mcts_tree[node_id] = node_data
        
        # Add to parent's children
        if parent_id and parent_id in self.mcts_tree:
            self.mcts_tree[parent_id].children.append(node_id)
        
        # Create iteration data
        iteration_data = {
            "iteration": iteration,
            "selectedPath": self._get_path_to_node(node_id),
            "expandedNode": node_id,
            "reward": reward,
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
        
        self.mcts_iterations.append(iteration_data)
        
        # Broadcast update
        await self._broadcast_mcts_update(iteration_data)
    
    def _select_mcts_parent(self, iteration: int, step: Dict[str, Any]) -> Optional[str]:
        """Select appropriate parent for MCTS node based on tree structure"""
        if iteration == 0 or step["depth"] == 0:
            return self.mcts_root
        
        # Find nodes at the previous depth level
        candidate_parents = [
            node_id for node_id, node in self.mcts_tree.items()
            if node.depth == step["depth"] - 1 and node.visits > 0
        ]
        
        if not candidate_parents:
            return self.mcts_root
            
        # Select parent with highest UCB score
        return max(candidate_parents, key=lambda nid: self.mcts_tree[nid].ucb_score)
    
    def _calculate_step_reward(self, step: Dict[str, Any], iteration: int) -> float:
        """Calculate reward for a particular step in building factorial"""
        base_rewards = {
            "define_function": 0.8,
            "add_base_case": 0.9, 
            "return_one": 0.85,
            "add_else_clause": 0.7,
            "recursive_call": 0.95,
            "subtract_one": 0.9,
            "add_memoization": 0.6,
            "check_memo": 0.65,
            "return_cached": 0.7,
            "add_validation": 0.5,
            "raise_error": 0.55
        }
        
        base_reward = base_rewards.get(step["action"], 0.5)
        
        # Add some randomness and learning progression
        learning_bonus = min(0.2, iteration * 0.01)  # Gets better over iterations
        noise = random.uniform(-0.1, 0.1)
        
        return max(0.1, min(1.0, base_reward + learning_bonus + noise))
    
    def _calculate_ucb_score(self, total_reward: float, visits: int, iteration: int) -> float:
        """Calculate UCB1 score for node selection"""
        import math
        
        if visits == 0:
            return float('inf')
        
        # UCB1 formula: mean_reward + C * sqrt(ln(total_visits) / visits)
        exploration_constant = 1.414  # sqrt(2)
        total_visits = max(iteration + 1, visits)
        
        mean_reward = total_reward / visits
        exploration_bonus = exploration_constant * math.sqrt(math.log(total_visits) / visits)
        
        return mean_reward + exploration_bonus
    
    def _build_cumulative_code(self, iteration: int, current_step: Dict[str, Any]) -> str:
        """Build the cumulative code being constructed"""
        if iteration < 5:
            # Early iterations - just the basic structure
            if iteration == 0:
                return "def factorial(n):"
            elif iteration == 1:
                return "def factorial(n):\n    if eq(n, 0):"
            elif iteration == 2:
                return "def factorial(n):\n    if eq(n, 0):\n        return 1"
            elif iteration == 3:
                return "def factorial(n):\n    if eq(n, 0):\n        return 1\n    else:"
            elif iteration == 4:
                return "def factorial(n):\n    if eq(n, 0):\n        return 1\n    else:\n        return mul(n, factorial(sub(n, 1)))"
        else:
            # Later iterations - adding optimizations
            return """def factorial(n):
    if lt(n, 0):
        raise ValueError("Factorial undefined for negative numbers")
    if eq(n, 0):
        return 1
    else:
        return mul(n, factorial(sub(n, 1)))"""
    
    def _get_path_to_node(self, node_id: str) -> List[str]:
        """Get path from root to given node"""
        path = []
        current = node_id
        
        while current and current in self.mcts_tree:
            path.append(current)
            current = self.mcts_tree[current].parent
        
        return list(reversed(path))
    
    async def _simulate_evolution_generation(self, generation: int):
        """Simulate an evolution generation"""
        population_size = min(self.configs["evolution_config"]["population_size"], 8)
        
        population = []
        mutation_strategies = ["generalize_parameters", "combine_functions", "add_recursion", "add_error_handling"]
        function_names = ["factorial", "power", "fibonacci", "max_two", "min_val", "sum_range", "is_even", "abs_val"]
        
        for i in range(population_size):
            candidate_id = f"candidate_{generation}_{i}"
            func_name = random.choice(function_names)
            
            # Create mock function data
            function_data = {
                "name": f"{func_name}_{generation}_{i}",
                "params": ["n"] if func_name in ["factorial", "fibonacci"] else ["x", "y"],
                "paramTypes": ["int"] if func_name in ["factorial", "fibonacci"] else ["int", "int"],
                "returnType": "int",
                "body": self._generate_function_body(func_name, generation, i),
                "implementation": "",
                "fitnessScore": max(0.1, min(0.98, 0.5 + (generation * 0.08) + random.uniform(-0.1, 0.2))),
                "usageCount": random.randint(1, 20),
                "isEvolved": True
            }
            
            candidate = EvolutionCandidateData(
                id=candidate_id,
                function=function_data,
                generation=generation,
                parent_functions=[f"parent_{generation-1}_{i}"] if generation > 0 else [],
                fitness=function_data["fitnessScore"],
                is_selected=False,
                mutation_strategy=random.choice(mutation_strategies)
            )
            
            population.append(candidate)
        
        # Calculate statistics
        fitnesses = [c.fitness for c in population]
        best_fitness = max(fitnesses)
        average_fitness = sum(fitnesses) / len(fitnesses)
        
        # Create generation data
        generation_data = EvolutionGenerationData(
            generation=generation,
            population=population,
            best_fitness=best_fitness,
            average_fitness=average_fitness,
            new_mutations=[f"mutation_{generation}_{i}" for i in range(random.randint(1, 3))],
            timestamp=int(datetime.now().timestamp() * 1000)
        )
        
        self.evolution_generations.append(generation_data)
        self.current_generation = generation
        
        # Broadcast update
        await self._broadcast_evolution_update(generation_data)
    
    def _generate_function_body(self, func_name: str, generation: int, index: int) -> str:
        """Generate realistic function body code"""
        if func_name == "factorial":
            return f"def factorial_{generation}_{index}(n):\n    if eq(n, 0):\n        return 1\n    else:\n        return mul(n, factorial(sub(n, 1)))"
        elif func_name == "fibonacci":
            return f"def fibonacci_{generation}_{index}(n):\n    if lt(n, 2):\n        return n\n    else:\n        return add(fibonacci(sub(n, 1)), fibonacci(sub(n, 2)))"
        elif func_name == "power":
            return f"def power_{generation}_{index}(x, y):\n    if eq(y, 0):\n        return 1\n    else:\n        return mul(x, power(x, sub(y, 1)))"
        elif func_name == "max_two":
            return f"def max_two_{generation}_{index}(x, y):\n    return if_then_else(gt(x, y), x, y)"
        else:
            return f"def {func_name}_{generation}_{index}(x, y):\n    return add(x, y)"
    
    async def _broadcast_status_update(self):
        """Broadcast system status"""
        message = {
            "type": "system_status",
            "data": {
                "isRunning": self.is_running,
                "currentPhase": self.current_phase,
                "progress": self.progress,
                "costs": self.costs
            },
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
        await broadcast_message(message)
    
    async def _broadcast_mcts_update(self, iteration_data: Dict[str, Any]):
        """Broadcast MCTS update"""
        message = {
            "type": "mcts_iteration",
            "data": {
                "iteration": iteration_data,
                "tree": {k: asdict(v) for k, v in self.mcts_tree.items()},
                "root": self.mcts_root
            },
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
        await broadcast_message(message)
    
    async def _broadcast_evolution_update(self, generation_data: EvolutionGenerationData):
        """Broadcast evolution update"""
        message = {
            "type": "evolution_generation",
            "data": asdict(generation_data),
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
        await broadcast_message(message)

# WebSocket management
async def broadcast_message(message: Dict[str, Any]):
    """Broadcast to all connected clients"""
    if not websocket_connections:
        return
    
    message_str = json.dumps(message)
    disconnected = []
    
    for websocket in websocket_connections:
        try:
            await websocket.send_text(message_str)
        except Exception as e:
            logger.warning(f"Failed to send message: {e}")
            disconnected.append(websocket)
    
    for ws in disconnected:
        websocket_connections.remove(ws)

# API Endpoints
@app.post("/api/sessions/{session_id}/start")
async def start_evolution(session_id: str, request_data: dict, background_tasks: BackgroundTasks):
    """Start evolution demo"""
    
    try:
        # Get configs (API key handled by environment variables)
        gpt4o_config = request_data.get('gpt4o_config', {})
        # Use environment API key if available, otherwise run in demo mode
        api_key = os.environ.get('OPENAI_API_KEY') or gpt4o_config.get('apiKey', '')
        gpt4o_config['apiKey'] = api_key
        
        # Default configs
        mcts_config = {
            'iterations': request_data.get('mcts_config', {}).get('iterations', 20),
            'exploration_constant': 1.414,
            'targetTask': request_data.get('mcts_config', {}).get('targetTask', 'factorial')
        }
        
        evolution_config = {
            'generations': request_data.get('evolution_config', {}).get('generations', 5),
            'population_size': request_data.get('evolution_config', {}).get('population_size', 8),
            'mutation_rate': 0.3,
            'selection_strategy': 'tournament'
        }
        
        configs = {
            "gpt4o_config": gpt4o_config,
            "mcts_config": mcts_config,
            "evolution_config": evolution_config
        }
        
        # Create session
        session = EvolutionSession(session_id, configs)
        active_sessions[session_id] = session
        
        # Start in background
        background_tasks.add_task(session.start_evolution)
        
        return {"message": "Evolution demo started", "session_id": session_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sessions/{session_id}/stop")
async def stop_evolution(session_id: str):
    """Stop evolution"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    session.is_running = False
    session.current_phase = "stopped"
    
    await session._broadcast_status_update()
    return {"message": "Evolution stopped", "session_id": session_id}

@app.get("/api/sessions/{session_id}/status")
async def get_session_status(session_id: str):
    """Get session status"""
    if session_id not in active_sessions:
        return {
            "session_id": session_id,
            "is_running": False,
            "current_phase": "idle",
            "progress": {"current": 0, "total": 0, "phase": "Idle"},
            "costs": {"total_cost": 0, "mcts_phase": 0, "evolution_phase": 0}
        }
    
    session = active_sessions[session_id]
    return {
        "session_id": session_id,
        "is_running": session.is_running,
        "current_phase": session.current_phase,
        "progress": session.progress,
        "costs": session.costs
    }

@app.get("/api/sessions/{session_id}/mcts")
async def get_mcts_data(session_id: str):
    """Get MCTS data"""
    if session_id not in active_sessions:
        return {"tree": {}, "root": None, "iterations": []}
    
    session = active_sessions[session_id]
    return {
        "tree": {k: asdict(v) for k, v in session.mcts_tree.items()},
        "root": session.mcts_root,
        "iterations": session.mcts_iterations
    }

@app.get("/api/sessions/{session_id}/evolution")
async def get_evolution_data(session_id: str):
    """Get evolution data"""
    if session_id not in active_sessions:
        return {"generations": [], "current_generation": 0}
    
    session = active_sessions[session_id]
    return {
        "generations": [asdict(gen) for gen in session.evolution_generations],
        "current_generation": session.current_generation
    }

@app.get("/api/sessions")
async def list_sessions():
    """List sessions"""
    return {
        "sessions": [
            {
                "session_id": sid,
                "is_running": session.is_running,
                "current_phase": session.current_phase
            }
            for sid, session in active_sessions.items()
        ]
    }

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket for real-time updates"""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    logger.info(f"WebSocket connected for session {session_id}")
    
    try:
        # Send initial status
        if session_id in active_sessions:
            session = active_sessions[session_id]
            await session._broadcast_status_update()
        
        # Keep alive
        while True:
            try:
                data = await websocket.receive_text()
                # Echo back
                await websocket.send_text(f"Echo: {data}")
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
                
    except WebSocketDisconnect:
        pass
    finally:
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)
        logger.info(f"WebSocket disconnected for session {session_id}")

@app.get("/")
async def read_root():
    """Health check"""
    return {"message": "EvolDSL Backend API Demo", "status": "running"}

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(
        "backend_simple:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )