#!/usr/bin/env python3
"""
API Composition Backend with MCTS + Evolution
Uses GPT-4o for intelligent API chain construction based on type compatibility
"""

import asyncio
import json
import logging
import os
import random
import math
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
import uuid
import openai
from collections import defaultdict, deque

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="API Composition Backend", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Global state
active_sessions: Dict[str, 'APICompositionSession'] = {}
websocket_connections: List[WebSocket] = []

# --- Comprehensive API Bank ---
@dataclass
class APIDefinition:
    name: str
    inputs: Dict[str, str]  # param_name -> type
    output_type: str
    description: str
    category: str
    cost_estimate: float = 0.1

# Comprehensive API Bank with 25+ APIs across different domains
API_BANK = {
    # Data Sources
    "search_news": APIDefinition("search_news", {"query": "string"}, "article_list", "Search news articles", "data_source"),
    "get_stock_data": APIDefinition("get_stock_data", {"symbol": "string"}, "stock_data", "Get stock price data", "data_source"),
    "fetch_weather": APIDefinition("fetch_weather", {"location": "string"}, "weather_data", "Get weather information", "data_source"),
    "get_company_info": APIDefinition("get_company_info", {"company": "string"}, "company_data", "Get company details", "data_source"),
    "search_patents": APIDefinition("search_patents", {"query": "string"}, "patent_list", "Search patent database", "data_source"),
    "get_social_mentions": APIDefinition("get_social_mentions", {"entity": "string"}, "social_data", "Get social media mentions", "data_source"),
    
    # Analysis APIs
    "analyze_sentiment": APIDefinition("analyze_sentiment", {"text": "article_list"}, "sentiment_score", "Analyze text sentiment", "analysis"),
    "analyze_trend": APIDefinition("analyze_trend", {"data": "stock_data"}, "trend_analysis", "Analyze data trends", "analysis"),
    "extract_entities": APIDefinition("extract_entities", {"text": "article_list"}, "entity_list", "Extract named entities", "analysis"),
    "calculate_risk": APIDefinition("calculate_risk", {"financial_data": "stock_data"}, "risk_score", "Calculate financial risk", "analysis"),
    "predict_price": APIDefinition("predict_price", {"history": "stock_data", "sentiment": "sentiment_score"}, "price_prediction", "Predict future price", "analysis"),
    "analyze_competition": APIDefinition("analyze_competition", {"company": "company_data", "patents": "patent_list"}, "competitive_analysis", "Analyze competitive landscape", "analysis"),
    
    # Processing APIs
    "summarize_text": APIDefinition("summarize_text", {"articles": "article_list"}, "summary", "Summarize text content", "processing"),
    "filter_relevant": APIDefinition("filter_relevant", {"data": "article_list", "criteria": "string"}, "filtered_articles", "Filter relevant content", "processing"),
    "merge_datasets": APIDefinition("merge_datasets", {"data1": "stock_data", "data2": "social_data"}, "merged_data", "Merge multiple datasets", "processing"),
    "normalize_data": APIDefinition("normalize_data", {"raw_data": "stock_data"}, "normalized_data", "Normalize data format", "processing"),
    "aggregate_scores": APIDefinition("aggregate_scores", {"sentiment": "sentiment_score", "risk": "risk_score"}, "composite_score", "Aggregate multiple scores", "processing"),
    
    # Visualization APIs
    "create_chart": APIDefinition("create_chart", {"data": "stock_data"}, "chart_url", "Create data visualization", "visualization"),
    "generate_heatmap": APIDefinition("generate_heatmap", {"scores": "composite_score"}, "heatmap_url", "Generate correlation heatmap", "visualization"),
    "create_timeline": APIDefinition("create_timeline", {"events": "entity_list"}, "timeline_url", "Create event timeline", "visualization"),
    "plot_prediction": APIDefinition("plot_prediction", {"prediction": "price_prediction", "history": "stock_data"}, "prediction_chart", "Plot prediction vs history", "visualization"),
    
    # Output APIs
    "generate_report": APIDefinition("generate_report", {"summary": "summary", "analysis": "trend_analysis"}, "final_report", "Generate comprehensive report", "output"),
    "create_dashboard": APIDefinition("create_dashboard", {"charts": "chart_url", "summary": "summary"}, "dashboard_url", "Create interactive dashboard", "output"),
    "send_alert": APIDefinition("send_alert", {"risk": "risk_score", "threshold": "float"}, "alert_status", "Send risk alert", "output"),
    "export_data": APIDefinition("export_data", {"processed_data": "merged_data"}, "export_url", "Export processed data", "output"),
    "generate_presentation": APIDefinition("generate_presentation", {"report": "final_report", "charts": "prediction_chart"}, "presentation_url", "Generate presentation", "output"),
}

# Type compatibility graph
TYPE_COMPATIBILITY = {
    "string": ["string"],
    "article_list": ["article_list", "text"],
    "stock_data": ["stock_data", "data", "financial_data", "history"],
    "weather_data": ["weather_data", "data"],
    "company_data": ["company_data", "data"],
    "patent_list": ["patent_list", "data"],
    "social_data": ["social_data", "data"],
    "sentiment_score": ["sentiment_score", "score"],
    "trend_analysis": ["trend_analysis", "analysis"],
    "entity_list": ["entity_list", "events"],
    "risk_score": ["risk_score", "score"],
    "price_prediction": ["price_prediction", "prediction"],
    "competitive_analysis": ["competitive_analysis", "analysis"],
    "summary": ["summary", "text"],
    "filtered_articles": ["filtered_articles", "article_list", "text"],
    "merged_data": ["merged_data", "processed_data", "data"],
    "normalized_data": ["normalized_data", "data"],
    "composite_score": ["composite_score", "scores", "score"],
    "chart_url": ["chart_url", "charts"],
    "heatmap_url": ["heatmap_url", "chart_url"],
    "timeline_url": ["timeline_url", "chart_url"],
    "prediction_chart": ["prediction_chart", "charts", "chart_url"],
    "final_report": ["final_report", "report"],
    "dashboard_url": ["dashboard_url"],
    "alert_status": ["alert_status"],
    "export_url": ["export_url"],
    "presentation_url": ["presentation_url"],
    "float": ["float", "threshold"]
}

def is_type_compatible(output_type: str, required_type: str) -> bool:
    """Check if output_type can be used as required_type"""
    return required_type in TYPE_COMPATIBILITY.get(output_type, [])

# --- MCTS Node for API Composition ---
@dataclass
class APINode:
    id: str
    api_name: str
    inputs: Dict[str, str]  # param -> source_node_id
    output_type: str
    depth: int
    visits: int = 0
    total_reward: float = 0.0
    children: List[str] = None
    parent: Optional[str] = None
    is_terminal: bool = False
    
    def __post_init__(self):
        if self.children is None:
            self.children = []

@dataclass
class MCTSState:
    nodes: Dict[str, APINode]
    root_id: str
    available_types: Dict[str, str]  # type -> node_id that produces it
    goal: str
    current_depth: int = 0
    
    def get_ucb_score(self, node_id: str, exploration_constant: float = 1.414) -> float:
        """Calculate UCB1 score for node selection"""
        node = self.nodes[node_id]
        if node.visits == 0:
            return float('inf')
        
        parent = self.nodes.get(node.parent)
        if not parent or parent.visits == 0:
            return node.total_reward / node.visits
            
        exploitation = node.total_reward / node.visits
        exploration = exploration_constant * math.sqrt(math.log(parent.visits) / node.visits)
        return exploitation + exploration

# --- GPT-4o Integration ---
class GPT4OPolicy:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key) if api_key else None
        
    async def get_next_api_suggestion(self, current_state: MCTSState, goal: str) -> Dict[str, Any]:
        """Use GPT-4o to suggest the next best API to add"""
        if not self.client:
            return self._fallback_policy(current_state, goal)
            
        try:
            # Build context for GPT-4o
            current_apis = [node.api_name for node in current_state.nodes.values() if node.api_name != "START"]
            available_types = list(current_state.available_types.keys())
            
            prompt = f"""
            Goal: {goal}
            
            Current API chain: {' -> '.join(current_apis)}
            Available data types: {', '.join(available_types)}
            
            From these APIs, which should be added next to progress toward the goal?
            Available APIs: {', '.join(API_BANK.keys())}
            
            Consider:
            1. Type compatibility (inputs must match available outputs)
            2. Logical flow toward the goal
            3. Value of information gain
            
            Respond with JSON: {{"api_name": "suggested_api", "reasoning": "explanation", "confidence": 0.8}}
            """
            
            response = await self.client.chat.completions.acreate(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.warning(f"GPT-4o call failed: {e}, using fallback")
            return self._fallback_policy(current_state, goal)
    
    def _fallback_policy(self, current_state: MCTSState, goal: str) -> Dict[str, Any]:
        """Fallback policy when GPT-4o is not available"""
        # Simple heuristic: prefer APIs that can use available types
        possible_apis = []
        for api_name, api_def in API_BANK.items():
            if api_name in [node.api_name for node in current_state.nodes.values()]:
                continue
                
            can_satisfy = True
            for param, required_type in api_def.inputs.items():
                found_compatible = False
                for available_type in current_state.available_types.keys():
                    if is_type_compatible(available_type, required_type):
                        found_compatible = True
                        break
                if not found_compatible:
                    can_satisfy = False
                    break
                    
            if can_satisfy:
                possible_apis.append(api_name)
        
        if possible_apis:
            suggested = random.choice(possible_apis)
            return {"api_name": suggested, "reasoning": "Heuristic selection", "confidence": 0.6}
        
        return {"api_name": None, "reasoning": "No compatible APIs found", "confidence": 0.1}

    async def evaluate_state(self, state: MCTSState, goal: str) -> float:
        """Use GPT-4o to evaluate how close the current state is to the goal"""
        if not self.client:
            return self._fallback_evaluation(state, goal)
            
        try:
            current_apis = [node.api_name for node in state.nodes.values() if node.api_name != "START"]
            
            prompt = f"""
            Goal: {goal}
            Current API chain: {' -> '.join(current_apis)}
            
            Rate how close this API chain is to achieving the goal on a scale of 0.0 to 1.0.
            Consider:
            1. Completeness of the data pipeline
            2. Logical flow from input to desired output
            3. Missing critical steps
            
            Respond with just a number between 0.0 and 1.0.
            """
            
            response = await self.client.chat.completions.acreate(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=10
            )
            
            score = float(response.choices[0].message.content.strip())
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.warning(f"GPT-4o evaluation failed: {e}, using fallback")
            return self._fallback_evaluation(state, goal)
    
    def _fallback_evaluation(self, state: MCTSState, goal: str) -> float:
        """Fallback evaluation when GPT-4o is not available"""
        nodes = [n for n in state.nodes.values() if n.api_name != "START"]
        if not nodes:
            return 0.0
            
        # Simple heuristic based on API categories and chain length
        categories = set()
        for node in nodes:
            if node.api_name in API_BANK:
                categories.add(API_BANK[node.api_name].category)
        
        score = 0.0
        score += len(categories) * 0.15  # Reward diversity
        score += len(nodes) * 0.05  # Reward chain length
        
        # Bonus for having output APIs
        output_apis = [n for n in nodes if API_BANK.get(n.api_name, APIDefinition("", {}, "", "", "")).category == "output"]
        if output_apis:
            score += 0.4
            
        return min(1.0, score)

# --- API Composition Session ---
class APICompositionSession:
    def __init__(self, session_id: str, configs: Dict[str, Any]):
        self.session_id = session_id
        self.configs = configs
        self.is_running = False
        self.current_phase = "idle"
        self.progress = {"current": 0, "total": 0, "phase": "Idle"}
        
        # Initialize GPT-4o policy
        api_key = configs.get('gpt4o_config', {}).get('apiKey') or os.environ.get('OPENAI_API_KEY')
        self.gpt4o_policy = GPT4OPolicy(api_key)
        
        # MCTS state
        self.mcts_states: List[MCTSState] = []
        self.current_iteration = 0
        self.best_chains: List[Dict[str, Any]] = []
        
    async def start_composition(self):
        """Start the API composition process"""
        if self.is_running:
            raise HTTPException(status_code=400, detail="Session already running")
        
        self.is_running = True
        self.current_phase = "initializing"
        
        try:
            await self._broadcast_status_update()
            
            # Initialize with START node
            start_node = APINode(
                id="START",
                api_name="START", 
                inputs={}, 
                output_type="string", 
                depth=0,
                visits=1,
                total_reward=0.0,
                children=[],
                parent=None,
                is_terminal=False
            )
            
            initial_state = MCTSState(
                nodes={"START": start_node},
                root_id="START",
                available_types={"string": "START"},
                goal=self.configs.get('goal', 'Create a comprehensive analysis dashboard'),
                current_depth=0
            )
            
            self.mcts_states = [initial_state]
            
            # Send initial tree state
            await self._broadcast_mcts_update(0, initial_state, 0.0)
            
            # Run MCTS iterations
            await self._run_mcts_iterations()
            
            # Start Evolution phase
            self.current_phase = "evolution"
            await self._run_evolution_phase()
            
            self.current_phase = "completed"
            self.is_running = False
            
        except Exception as e:
            logger.error(f"Composition failed: {str(e)}")
            self.current_phase = "error"
            self.is_running = False
            raise
        
        await self._broadcast_status_update()
    
    async def _run_mcts_iterations(self):
        """Run MCTS iterations to build API chains"""
        self.current_phase = "mcts_composition"
        max_iterations = self.configs.get('mcts_config', {}).get('iterations', 20)
        
        self.progress = {
            "current": 0,
            "total": max_iterations,
            "phase": "Building API Chains with MCTS"
        }
        
        for iteration in range(max_iterations):
            await self._mcts_iteration(iteration)
            
            self.progress["current"] = iteration + 1
            await self._broadcast_status_update()
            await asyncio.sleep(0.5)  # Visualization delay
    
    async def _mcts_iteration(self, iteration: int):
        """Single MCTS iteration"""
        current_state = self.mcts_states[-1] if self.mcts_states else None
        if not current_state:
            return
        
        # Selection - choose node to expand using UCB
        selected_node_id = await self._select_node(current_state)
        
        # Expansion - add new API node
        new_state = await self._expand_node(current_state, selected_node_id, iteration)
        
        if new_state:
            # Evaluation - get reward from GPT-4o
            reward = await self.gpt4o_policy.evaluate_state(new_state, new_state.goal)
            
            # Backpropagation - update node statistics
            await self._backpropagate(new_state, reward)
            
            self.mcts_states.append(new_state)
            
            # Broadcast update immediately after each iteration
            await self._broadcast_mcts_update(iteration, new_state, reward)
            
            # Small delay for visualization
            await asyncio.sleep(0.5)
    
    async def _select_node(self, state: MCTSState) -> str:
        """Select best node to expand using UCB1"""
        best_node_id = None
        best_ucb = -float('inf')
        
        for node_id, node in state.nodes.items():
            if node.api_name == "START" or len(node.children) < 3:  # Can still expand
                ucb = state.get_ucb_score(node_id)
                if ucb > best_ucb:
                    best_ucb = ucb
                    best_node_id = node_id
        
        return best_node_id or "START"
    
    async def _expand_node(self, state: MCTSState, parent_id: str, iteration: int) -> Optional[MCTSState]:
        """Expand node by adding new API"""
        # Get GPT-4o suggestion
        suggestion = await self.gpt4o_policy.get_next_api_suggestion(state, state.goal)
        
        if not suggestion.get('api_name') or suggestion['api_name'] not in API_BANK:
            return None
        
        # Create new state
        new_state = MCTSState(
            nodes=state.nodes.copy(),
            root_id=state.root_id,
            available_types=state.available_types.copy(),
            goal=state.goal,
            current_depth=state.current_depth + 1
        )
        
        # Add new API node
        api_name = suggestion['api_name']
        api_def = API_BANK[api_name]
        
        # Find input sources
        input_sources = {}
        for param, required_type in api_def.inputs.items():
            for available_type, source_node_id in new_state.available_types.items():
                if is_type_compatible(available_type, required_type):
                    input_sources[param] = source_node_id
                    break
        
        # Create new node
        new_node_id = f"{api_name}_{iteration}"
        new_node = APINode(
            id=new_node_id,
            api_name=api_name,
            inputs=input_sources,
            output_type=api_def.output_type,
            depth=state.current_depth + 1,
            parent=parent_id
        )
        
        new_state.nodes[new_node_id] = new_node
        new_state.nodes[parent_id].children.append(new_node_id)
        new_state.available_types[api_def.output_type] = new_node_id
        
        return new_state
    
    async def _backpropagate(self, state: MCTSState, reward: float):
        """Update node statistics"""
        for node in state.nodes.values():
            if node.api_name != "START":
                node.visits += 1
                node.total_reward += reward
    
    async def _run_evolution_phase(self):
        """Run evolution phase to optimize API chains"""
        self.current_phase = "evolution"
        max_generations = self.configs.get('evolution_config', {}).get('generations', 10)
        
        self.progress = {
            "current": 0,
            "total": max_generations,
            "phase": "Evolving API Chains"
        }
        
        # Get the best MCTS state as starting point
        best_state = self.mcts_states[-1] if self.mcts_states else None
        if not best_state:
            return
        
        # Initialize evolution population with variations of the best MCTS chain
        population = []
        for i in range(5):  # Create 5 variations
            # Create mutations of the best chain
            mutated_state = await self._mutate_chain(best_state, i)
            if mutated_state:
                population.append(mutated_state)
        
        # Run evolution generations
        for generation in range(max_generations):
            await self._evolution_generation(generation, population)
            
            self.progress["current"] = generation + 1
            await self._broadcast_status_update()
            await asyncio.sleep(0.3)  # Faster than MCTS
    
    async def _evolution_generation(self, generation: int, population: List[MCTSState]):
        """Single evolution generation"""
        # Evaluate all candidates
        evaluated_population = []
        for candidate in population:
            fitness = await self.gpt4o_policy.evaluate_state(candidate, candidate.goal)
            evaluated_population.append((candidate, fitness))
        
        # Sort by fitness
        evaluated_population.sort(key=lambda x: x[1], reverse=True)
        
        # Broadcast evolution update
        await self._broadcast_evolution_update(generation, evaluated_population)
        
        # Select top candidates for next generation
        top_candidates = [candidate for candidate, fitness in evaluated_population[:3]]
        
        # Create new generation through mutation
        new_population = top_candidates.copy()  # Keep best
        
        # Add mutations
        for i in range(2):  # Add 2 mutations
            parent = random.choice(top_candidates)
            mutated = await self._mutate_chain(parent, generation * 10 + i)
            if mutated:
                new_population.append(mutated)
        
        population[:] = new_population
    
    async def _mutate_chain(self, state: MCTSState, mutation_id: int) -> Optional[MCTSState]:
        """Create a mutation of an API chain"""
        try:
            # Simple mutation: try to add one more API to the chain
            suggestion = await self.gpt4o_policy.get_next_api_suggestion(state, state.goal)
            
            if not suggestion.get('api_name') or suggestion['api_name'] not in API_BANK:
                return state  # Return original if no good mutation
            
            # Create mutated state
            mutated_state = MCTSState(
                nodes=state.nodes.copy(),
                root_id=state.root_id,
                available_types=state.available_types.copy(),
                goal=state.goal,
                current_depth=state.current_depth + 1
            )
            
            # Add the mutation
            api_name = suggestion['api_name']
            api_def = API_BANK[api_name]
            
            # Find input sources
            input_sources = {}
            for param, required_type in api_def.inputs.items():
                for available_type, source_node_id in mutated_state.available_types.items():
                    if is_type_compatible(available_type, required_type):
                        input_sources[param] = source_node_id
                        break
            
            if not input_sources:  # Can't connect
                return state
            
            # Create new node
            new_node_id = f"{api_name}_evo_{mutation_id}"
            new_node = APINode(
                id=new_node_id,
                api_name=api_name,
                inputs=input_sources,
                output_type=api_def.output_type,
                depth=mutated_state.current_depth + 1,
                visits=1,
                total_reward=0.0
            )
            
            mutated_state.nodes[new_node_id] = new_node
            mutated_state.available_types[api_def.output_type] = new_node_id
            
            return mutated_state
            
        except Exception as e:
            logger.warning(f"Mutation failed: {e}")
            return state
    
    async def _broadcast_evolution_update(self, generation: int, evaluated_population: List[tuple]):
        """Broadcast evolution generation update"""
        # Convert to serializable format
        population_data = []
        for i, (candidate, fitness) in enumerate(evaluated_population):
            population_data.append({
                "id": f"candidate_{generation}_{i}",
                "fitness": fitness,
                "api_count": len([n for n in candidate.nodes.values() if n.api_name != "START"]),
                "chain_apis": [n.api_name for n in candidate.nodes.values() if n.api_name != "START"]
            })
        
        best_fitness = evaluated_population[0][1] if evaluated_population else 0.0
        avg_fitness = sum(fitness for _, fitness in evaluated_population) / len(evaluated_population) if evaluated_population else 0.0
        
        generation_data = {
            "generation": generation,
            "population": population_data,
            "bestFitness": best_fitness,
            "averageFitness": avg_fitness,
            "newMutations": [f"mutation_{generation}_{i}" for i in range(2)],
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
        
        message = {
            "type": "evolution_generation",
            "data": generation_data,
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
        await broadcast_message(message)
    
    async def _broadcast_status_update(self):
        """Broadcast system status"""
        message = {
            "type": "system_status",
            "data": {
                "isRunning": self.is_running,
                "currentPhase": self.current_phase,
                "progress": self.progress
            },
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
        await broadcast_message(message)
    
    async def _broadcast_mcts_update(self, iteration: int, state: MCTSState, reward: float):
        """Broadcast MCTS tree update"""
        # Convert nodes to serializable format
        nodes_data = {}
        for node_id, node in state.nodes.items():
            nodes_data[node_id] = {
                "id": node.id,
                "api_name": node.api_name,
                "inputs": node.inputs,
                "output_type": node.output_type,
                "depth": node.depth,
                "visits": node.visits,
                "total_reward": node.total_reward,
                "ucb_score": state.get_ucb_score(node_id),
                "children": node.children,
                "parent": node.parent,
                "description": API_BANK.get(node.api_name, APIDefinition("", {}, "", "", "")).description,
                "category": API_BANK.get(node.api_name, APIDefinition("", {}, "", "", "")).category
            }
        
        message = {
            "type": "mcts_update",
            "data": {
                "iteration": iteration,
                "nodes": nodes_data,
                "root_id": state.root_id,
                "reward": reward,
                "goal": state.goal
            },
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
        await broadcast_message(message)

# --- WebSocket Management ---
async def broadcast_message(message: Dict[str, Any]):
    """Broadcast message to all connected WebSocket clients"""
    if not websocket_connections:
        return
    
    disconnected = []
    for ws in websocket_connections:
        try:
            await ws.send_text(json.dumps(message))
        except Exception:
            disconnected.append(ws)
    
    # Remove disconnected clients
    for ws in disconnected:
        websocket_connections.remove(ws)

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    websocket_connections.append(websocket)
    logger.info(f"WebSocket connected for session {session_id}")
    
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming WebSocket messages if needed
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    finally:
        if websocket in websocket_connections:
            websocket_connections.remove(websocket)

# --- API Endpoints ---
@app.post("/api/sessions/{session_id}/start")
async def start_composition(session_id: str, request_data: dict, background_tasks: BackgroundTasks):
    """Start API composition process"""
    
    try:
        # Get configs (API key handled by environment variables)
        gpt4o_config = request_data.get('gpt4o_config', {})
        api_key = os.environ.get('OPENAI_API_KEY') or gpt4o_config.get('apiKey', '')
        gpt4o_config['apiKey'] = api_key
        
        # Default configs
        mcts_config = {
            'iterations': request_data.get('mcts_config', {}).get('iterations', 15),
            'exploration_constant': 1.414,
        }
        
        configs = {
            'gpt4o_config': gpt4o_config,
            'mcts_config': mcts_config,
            'goal': request_data.get('goal', 'Create comprehensive business intelligence dashboard with news analysis, stock predictions, and risk assessment')
        }
        
        # Create session
        session = APICompositionSession(session_id, configs)
        active_sessions[session_id] = session
        
        # Start composition in background
        background_tasks.add_task(session.start_composition)
        
        return {"status": "success", "message": "API composition started"}
        
    except Exception as e:
        logger.error(f"Failed to start composition: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sessions/{session_id}/stop")
async def stop_composition(session_id: str):
    """Stop API composition process"""
    if session_id in active_sessions:
        session = active_sessions[session_id]
        session.is_running = False
        session.current_phase = "stopped"
        await session._broadcast_status_update()
        return {"status": "success", "message": "Composition stopped"}
    
    raise HTTPException(status_code=404, detail="Session not found")

@app.get("/api/sessions/{session_id}/status")
async def get_session_status(session_id: str):
    """Get session status"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    return {
        "is_running": session.is_running,
        "current_phase": session.current_phase,
        "progress": session.progress,
        "iteration": session.current_iteration
    }

@app.get("/api/sessions")
async def list_sessions():
    """List all sessions"""
    return {"sessions": list(active_sessions.keys())}

@app.get("/api/bank")
async def get_api_bank():
    """Get the complete API bank"""
    return {
        "apis": {name: asdict(api_def) for name, api_def in API_BANK.items()},
        "type_compatibility": TYPE_COMPATIBILITY
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)