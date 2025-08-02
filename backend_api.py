"""
Backend API for EvolDSL Frontend
Provides REST and WebSocket endpoints to interface with MCTS and Evolution systems
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

# Import existing MCTS and Evolution modules
from dsl import DSL, DSLFunction, DSLType
from mcts import MCTSProgramSynthesis, MCTSNode as MCTSNodeOriginal, ProgramState
from evolution import EvolutionEngine, EvolutionCandidate
from mcts_gpt4o import GPT4BootstrapSystem
from llm_integration import LLMConfig
from persistence import SessionManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="EvolDSL Backend API", version="1.0.0")

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

# Simple data models for API (using dicts instead of Pydantic for now)
def validate_gpt4o_config(data: dict):
    required = ['api_key']
    for field in required:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    return data

def validate_mcts_config(data: dict):
    defaults = {
        'iterations': 50,
        'exploration_constant': 1.414,
        'target_task': 'factorial'
    }
    return {**defaults, **data}

def validate_evolution_config(data: dict):
    defaults = {
        'generations': 10,
        'population_size': 20,
        'mutation_rate': 0.3,
        'selection_strategy': 'tournament'
    }
    return {**defaults, **data}

# Data classes for frontend communication
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
    """Manages an evolution session with real-time updates"""
    
    def __init__(self, session_id: str, configs: Dict[str, Any]):
        self.session_id = session_id
        self.configs = configs
        self.is_running = False
        self.current_phase = "idle"
        self.progress = {"current": 0, "total": 0, "phase": "Idle"}
        self.costs = {"total_cost": 0, "mcts_phase": 0, "evolution_phase": 0}
        
        # Initialize DSL and systems
        self.dsl = DSL()
        self.session_manager = SessionManager(session_id)
        self.bootstrap_system = None
        
        # Data storage
        self.mcts_tree: Dict[str, MCTSNodeData] = {}
        self.mcts_root: Optional[str] = None
        self.mcts_iterations: List[Dict[str, Any]] = []
        self.evolution_generations: List[EvolutionGenerationData] = []
        self.current_generation = 0
        
    async def start_evolution(self):
        """Start the evolution process"""
        if self.is_running:
            raise HTTPException(status_code=400, detail="Evolution already running")
        
        self.is_running = True
        self.current_phase = "initializing"
        
        try:
            # Initialize LLM configuration
            llm_config = LLMConfig(
                api_key=self.configs["gpt4o_config"]["api_key"],
                model=self.configs["gpt4o_config"]["model"],
                temperature=self.configs["gpt4o_config"]["temperature"],
                max_tokens=self.configs["gpt4o_config"]["max_tokens"],
            )
            
            # Initialize bootstrap system
            self.bootstrap_system = GPT4BootstrapSystem(
                initial_dsl=self.dsl,
                llm_config=llm_config
            )
            
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
        """Run MCTS search phase"""
        self.current_phase = "mcts"
        mcts_config = self.configs["mcts_config"]
        
        # Initialize MCTS
        mcts = MCTSProgramSynthesis(
            dsl=self.dsl,
            target_function_name="evolved_func"
        )
        
        # Update progress
        self.progress = {
            "current": 0,
            "total": mcts_config["iterations"],
            "phase": "MCTS Search"
        }
        await self._broadcast_status_update()
        
        # Run MCTS iterations with real-time updates
        for i in range(mcts_config["iterations"]):
            # Simulate MCTS iteration (replace with actual MCTS logic)
            await self._simulate_mcts_iteration(mcts, i)
            
            # Update progress
            self.progress["current"] = i + 1
            await self._broadcast_status_update()
            
            # Small delay for visualization
            await asyncio.sleep(0.1)
    
    async def _run_evolution_phase(self):
        """Run evolution phase"""
        self.current_phase = "evolution"
        evolution_config = self.configs["evolution_config"]
        
        # Initialize evolution engine
        evolution = EvolutionEngine(self.dsl)
        
        # Update progress
        self.progress = {
            "current": 0,
            "total": evolution_config["generations"],
            "phase": "Evolution"
        }
        await self._broadcast_status_update()
        
        # Run evolution generations
        for gen in range(evolution_config["generations"]):
            await self._simulate_evolution_generation(evolution, gen)
            
            # Update progress
            self.progress["current"] = gen + 1
            await self._broadcast_status_update()
            
            # Small delay for visualization
            await asyncio.sleep(0.2)
    
    async def _simulate_mcts_iteration(self, mcts: MCTSProgramSynthesis, iteration: int):
        """Simulate an MCTS iteration with realistic data"""
        # Create mock MCTS tree update
        node_id = f"node_{iteration}_{uuid.uuid4().hex[:8]}"
        
        # Create realistic program state
        state = {
            "functionName": "evolved_func",
            "params": ["x", "y"],
            "returnType": "int",
            "bodyTokens": [f"operation_{iteration % 3}("],
            "isComplete": iteration % 5 == 0,
            "depth": iteration % 4,
            "code": f"def evolved_func(x, y):\n    return operation_{iteration % 3}(x, y)" if iteration % 5 == 0 else ""
        }
        
        # Create MCTS node
        node_data = MCTSNodeData(
            id=node_id,
            state=state,
            parent="root" if iteration > 0 else None,
            children=[],
            visits=max(1, 20 - iteration // 5),
            total_reward=min(15, iteration * 0.3 + 2),
            ucb_score=1.5 - (iteration * 0.02),
            is_expanded=True,
            is_selected=False,
            action={
                "actionType": "call_function",
                "value": f"operation_{iteration % 3}",
                "description": f"Call operation {iteration % 3}"
            } if iteration > 0 else None,
            depth=iteration % 4
        )
        
        self.mcts_tree[node_id] = node_data
        
        if iteration == 0:
            self.mcts_root = node_id
        
        # Create iteration data
        iteration_data = {
            "iteration": iteration,
            "selectedPath": [node_id],
            "expandedNode": node_id,
            "reward": min(1.0, iteration * 0.02 + 0.1),
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
        
        self.mcts_iterations.append(iteration_data)
        
        # Broadcast MCTS update
        await self._broadcast_mcts_update(iteration_data)
    
    async def _simulate_evolution_generation(self, evolution: EvolutionEngine, generation: int):
        """Simulate an evolution generation"""
        population_size = self.configs["evolution_config"]["population_size"]
        
        # Create mock population
        population = []
        mutation_strategies = ["generalize_parameters", "combine_functions", "add_recursion", "add_error_handling"]
        
        for i in range(min(population_size, 10)):  # Limit for demo
            candidate_id = f"candidate_{generation}_{i}"
            
            # Create mock DSL function
            function_data = {
                "name": f"evolved_func_{generation}_{i}",
                "params": ["x", "y"] if i % 2 == 0 else ["n"],
                "paramTypes": ["int", "int"] if i % 2 == 0 else ["int"],
                "returnType": "int",
                "body": f"def evolved_func_{generation}_{i}(x, y):\n    return add(x, y)" if i % 2 == 0 else f"def evolved_func_{generation}_{i}(n):\n    return mul(n, n)",
                "implementation": "",
                "fitnessScore": max(0.1, min(0.95, 0.6 + (generation * 0.05) + (i * 0.02))),
                "usageCount": max(1, 10 - i),
                "isEvolved": True
            }
            
            candidate = EvolutionCandidateData(
                id=candidate_id,
                function=function_data,
                generation=generation,
                parent_functions=[f"parent_{generation-1}_{i}"] if generation > 0 else [],
                fitness=function_data["fitnessScore"],
                is_selected=False,
                mutation_strategy=mutation_strategies[i % len(mutation_strategies)]
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
            new_mutations=[f"mutation_{generation}_{i}" for i in range(2)],
            timestamp=int(datetime.now().timestamp() * 1000)
        )
        
        self.evolution_generations.append(generation_data)
        self.current_generation = generation
        
        # Broadcast evolution update
        await self._broadcast_evolution_update(generation_data)
    
    async def _broadcast_status_update(self):
        """Broadcast system status update"""
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
        """Broadcast MCTS iteration update"""
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
        """Broadcast evolution generation update"""
        message = {
            "type": "evolution_generation",
            "data": asdict(generation_data),
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
        await broadcast_message(message)

# WebSocket management
async def broadcast_message(message: Dict[str, Any]):
    """Broadcast message to all connected WebSocket clients"""
    if not websocket_connections:
        return
    
    message_str = json.dumps(message)
    disconnected = []
    
    for websocket in websocket_connections:
        try:
            await websocket.send_text(message_str)
        except Exception as e:
            logger.warning(f"Failed to send message to websocket: {e}")
            disconnected.append(websocket)
    
    # Remove disconnected websockets
    for ws in disconnected:
        websocket_connections.remove(ws)

# REST API Endpoints
@app.post("/api/sessions/{session_id}/start")
async def start_evolution(session_id: str, request_data: dict, background_tasks: BackgroundTasks):
    """Start evolution for a session"""
    
    try:
        # Validate configuration data
        gpt4o_config = validate_gpt4o_config(request_data.get('gpt4o_config', {}))
        mcts_config = validate_mcts_config(request_data.get('mcts_config', {}))
        evolution_config = validate_evolution_config(request_data.get('evolution_config', {}))
        
        # Validate API key
        if not gpt4o_config.get('api_key'):
            raise HTTPException(status_code=400, detail="GPT-4o API key required")
        
        # Create or get session
        if session_id in active_sessions:
            session = active_sessions[session_id]
            if session.is_running:
                raise HTTPException(status_code=400, detail="Evolution already running for this session")
        else:
            configs = {
                "gpt4o_config": gpt4o_config,
                "mcts_config": mcts_config,
                "evolution_config": evolution_config
            }
            session = EvolutionSession(session_id, configs)
            active_sessions[session_id] = session
        
        # Start evolution in background
        background_tasks.add_task(session.start_evolution)
        
        return {"message": "Evolution started", "session_id": session_id}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.post("/api/sessions/{session_id}/stop")
async def stop_evolution(session_id: str):
    """Stop evolution for a session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    session.is_running = False
    session.current_phase = "stopped"
    
    await session._broadcast_status_update()
    
    return {"message": "Evolution stopped", "session_id": session_id}

@app.get("/api/sessions/{session_id}/status")
async def get_session_status(session_id: str):
    """Get current status of a session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    
    return {
        "session_id": session_id,
        "is_running": session.is_running,
        "current_phase": session.current_phase,
        "progress": session.progress,
        "costs": session.costs,
        "mcts_iterations": len(session.mcts_iterations),
        "evolution_generations": len(session.evolution_generations)
    }

@app.get("/api/sessions/{session_id}/mcts")
async def get_mcts_data(session_id: str):
    """Get MCTS tree data for a session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    
    return {
        "tree": {k: asdict(v) for k, v in session.mcts_tree.items()},
        "root": session.mcts_root,
        "iterations": session.mcts_iterations
    }

@app.get("/api/sessions/{session_id}/evolution")
async def get_evolution_data(session_id: str):
    """Get evolution data for a session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    
    return {
        "generations": [asdict(gen) for gen in session.evolution_generations],
        "current_generation": session.current_generation
    }

@app.get("/api/sessions")
async def list_sessions():
    """List all active sessions"""
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

# WebSocket endpoint
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    logger.info(f"WebSocket connected for session {session_id}")
    
    try:
        # Send initial status if session exists
        if session_id in active_sessions:
            session = active_sessions[session_id]
            await session._broadcast_status_update()
        
        # Keep connection alive
        while True:
            try:
                # Wait for messages from client (ping/pong, etc.)
                data = await websocket.receive_text()
                # Echo back for now
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

# Serve static files (built frontend)
@app.get("/")
async def read_root():
    """Health check endpoint"""
    return {"message": "EvolDSL Backend API", "status": "running"}

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "backend_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )