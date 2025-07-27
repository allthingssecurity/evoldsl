import math
import random
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import copy
import json

@dataclass
class ProgramState:
    """Represents a partial program being constructed"""
    function_name: str
    params: List[str]
    return_type: str
    body_tokens: List[str] = field(default_factory=list)
    is_complete: bool = False
    depth: int = 0
    
    def clone(self):
        return copy.deepcopy(self)
    
    def to_code(self) -> str:
        """Convert current state to readable code"""
        if not self.body_tokens:
            return f"def {self.function_name}({', '.join(self.params)}):\n    pass"
        
        body = ' '.join(self.body_tokens)
        return f"def {self.function_name}({', '.join(self.params)}):\n    return {body}"

@dataclass  
class MCTSAction:
    """Represents an action that can be taken to extend a program"""
    action_type: str  # "call_function", "add_literal", "add_condition", "return"
    value: str
    description: str

class MCTSNode:
    def __init__(self, state: ProgramState, parent: Optional['MCTSNode'] = None, action: Optional[MCTSAction] = None):
        self.state = state
        self.parent = parent
        self.action = action
        self.children: List['MCTSNode'] = []
        self.visits = 0
        self.total_reward = 0.0
        self.untried_actions: List[MCTSAction] = []
        self.is_expanded = False
        
    def is_leaf(self) -> bool:
        return len(self.children) == 0
    
    def is_fully_expanded(self) -> bool:
        return len(self.untried_actions) == 0
    
    def ucb_score(self, exploration_constant: float = 1.414) -> float:
        if self.visits == 0:
            return float('inf')
        
        exploitation = self.total_reward / self.visits
        exploration = exploration_constant * math.sqrt(math.log(self.parent.visits) / self.visits)
        return exploitation + exploration
    
    def add_child(self, action: MCTSAction, new_state: ProgramState) -> 'MCTSNode':
        child = MCTSNode(new_state, parent=self, action=action)
        self.children.append(child)
        return child
    
    def backpropagate(self, reward: float):
        """Backpropagate reward up the tree"""
        self.visits += 1
        self.total_reward += reward
        if self.parent:
            self.parent.backpropagate(reward)

class ActionGenerator:
    """Generates possible actions for MCTS expansion"""
    
    def __init__(self, dsl):
        self.dsl = dsl
    
    def get_possible_actions(self, state: ProgramState) -> List[MCTSAction]:
        """Generate possible next actions for a given program state"""
        actions = []
        
        # If program is complete, no more actions
        if state.is_complete:
            return actions
        
        # If we haven't started the body, we can:
        if not state.body_tokens:
            # Start with a literal value
            actions.extend([
                MCTSAction("add_literal", "0", "Return literal 0"),
                MCTSAction("add_literal", "1", "Return literal 1"),
                MCTSAction("add_literal", "True", "Return literal True"),
                MCTSAction("add_literal", "False", "Return literal False"),
            ])
            
            # Start with a parameter
            for param in state.params:
                actions.append(MCTSAction("use_param", param, f"Use parameter {param}"))
            
            # Start with a function call
            for func_name in self.dsl.list_functions():
                if func_name != state.function_name:  # Don't call self directly
                    actions.append(MCTSAction("call_function", func_name, f"Call function {func_name}"))
            
            # Start with a conditional
            actions.append(MCTSAction("add_condition", "if", "Add conditional logic"))
        
        else:
            # We have some tokens, we can:
            # Complete the current expression
            actions.append(MCTSAction("complete", "complete", "Mark function as complete"))
            
            # Add more operations if we're building an expression
            last_token = state.body_tokens[-1] if state.body_tokens else ""
            
            # If last token was a function name, we need arguments
            if last_token in self.dsl.list_functions():
                for param in state.params:
                    actions.append(MCTSAction("add_arg", param, f"Add argument {param}"))
                for literal in ["0", "1", "True", "False"]:
                    actions.append(MCTSAction("add_arg", literal, f"Add literal {literal}"))
        
        return actions

class LLMPolicyModel:
    """Simulates an LLM-based policy for action selection"""
    
    def __init__(self, dsl):
        self.dsl = dsl
    
    def suggest_actions(self, state: ProgramState, available_actions: List[MCTSAction], top_k: int = 3) -> List[Tuple[MCTSAction, float]]:
        """Suggest top-k actions with probabilities"""
        # For now, simulate LLM policy with heuristics
        scored_actions = []
        
        for action in available_actions:
            score = self._score_action(state, action)
            scored_actions.append((action, score))
        
        # Sort by score and return top-k
        scored_actions.sort(key=lambda x: x[1], reverse=True)
        return scored_actions[:top_k]
    
    def _score_action(self, state: ProgramState, action: MCTSAction) -> float:
        """Score an action based on heuristics (simulating LLM policy)"""
        score = 0.5  # base score
        
        # Prefer completing programs that are getting long
        if action.action_type == "complete" and len(state.body_tokens) > 2:
            score += 0.3
        
        # Prefer using parameters over literals
        if action.action_type == "use_param":
            score += 0.2
        
        # Prefer calling useful functions
        if action.action_type == "call_function":
            func = self.dsl.get_function(action.value)
            if func and func.usage_count > 0:
                score += 0.1 * min(func.fitness_score, 1.0)
        
        # Add some randomness to simulate LLM uncertainty
        score += random.random() * 0.1
        
        return score

class LLMRewardModel:
    """Simulates an LLM-based reward model for evaluating programs"""
    
    def __init__(self):
        self.evaluation_cache = {}
    
    def evaluate_program(self, state: ProgramState, target_task: str = None) -> float:
        """Evaluate a program and return a reward score [0, 1]"""
        if not state.is_complete:
            return 0.0  # Incomplete programs get no reward
        
        code = state.to_code()
        cache_key = (code, target_task)
        
        if cache_key in self.evaluation_cache:
            return self.evaluation_cache[cache_key]
        
        reward = self._evaluate_code_quality(code, target_task)
        self.evaluation_cache[cache_key] = reward
        return reward
    
    def _evaluate_code_quality(self, code: str, target_task: str = None) -> float:
        """Evaluate code quality using multiple criteria"""
        score = 0.0
        
        # Syntactic correctness (basic check)
        try:
            compile(code, '<string>', 'exec')
            score += 0.3
        except:
            return 0.0  # Invalid syntax gets 0
        
        # Complexity/elegance heuristics
        lines = code.strip().split('\n')
        body_lines = [l for l in lines if l.strip() and not l.strip().startswith('def')]
        
        if len(body_lines) == 1:  # Simple one-liner
            score += 0.2
        elif len(body_lines) <= 3:  # Reasonably simple
            score += 0.1
        
        # Check for meaningful computation
        if any(op in code for op in ['add', 'mul', 'sub', 'div']):
            score += 0.2
        
        # Check for control flow
        if 'if' in code or 'for' in code or 'while' in code:
            score += 0.1
        
        # Novelty bonus (different from common patterns)
        if self._is_novel_pattern(code):
            score += 0.2
        
        return min(score, 1.0)
    
    def _is_novel_pattern(self, code: str) -> bool:
        """Check if code represents a novel pattern"""
        # Simple heuristic: novel if it's not just returning a parameter or literal
        return not (code.count('return') == 1 and len(code.split()) < 10)

class MCTSProgramSynthesis:
    """Main MCTS engine for program synthesis"""
    
    def __init__(self, dsl, target_function_name: str = "synthesized_func"):
        self.dsl = dsl
        self.target_function_name = target_function_name
        self.action_generator = ActionGenerator(dsl)
        self.policy_model = LLMPolicyModel(dsl)
        self.reward_model = LLMRewardModel()
        self.root = None
        self.best_programs = []
    
    def search(self, iterations: int = 100, target_task: str = None) -> List[ProgramState]:
        """Run MCTS search to find good programs"""
        # Initialize root with empty program state
        initial_state = ProgramState(
            function_name=self.target_function_name,
            params=["x", "y"],  # Default parameters
            return_type="int"
        )
        
        self.root = MCTSNode(initial_state)
        
        for i in range(iterations):
            # Selection
            node = self._select(self.root)
            
            # Expansion
            if not node.state.is_complete and not node.is_fully_expanded():
                node = self._expand(node)
            
            # Simulation
            reward = self._simulate(node, target_task)
            
            # Backpropagation
            node.backpropagate(reward)
            
            # Track best programs
            if node.state.is_complete and reward > 0.5:
                self.best_programs.append((node.state.clone(), reward))
        
        # Return best programs found
        self.best_programs.sort(key=lambda x: x[1], reverse=True)
        return [prog for prog, score in self.best_programs[:10]]
    
    def _select(self, node: MCTSNode) -> MCTSNode:
        """Select a node using UCB"""
        while not node.is_leaf() and node.is_fully_expanded():
            node = max(node.children, key=lambda c: c.ucb_score())
        return node
    
    def _expand(self, node: MCTSNode) -> MCTSNode:
        """Expand a node by adding a new child"""
        if not node.is_expanded:
            # Get possible actions for this state
            actions = self.action_generator.get_possible_actions(node.state)
            
            # Use LLM policy to get top actions
            suggested_actions = self.policy_model.suggest_actions(node.state, actions)
            node.untried_actions = [action for action, score in suggested_actions]
            node.is_expanded = True
        
        if node.untried_actions:
            # Pick the next untried action
            action = node.untried_actions.pop(0)
            
            # Apply action to create new state
            new_state = self._apply_action(node.state, action)
            
            # Create and return new child
            return node.add_child(action, new_state)
        
        return node
    
    def _apply_action(self, state: ProgramState, action: MCTSAction) -> ProgramState:
        """Apply an action to a state to create a new state"""
        new_state = state.clone()
        
        if action.action_type == "add_literal":
            new_state.body_tokens.append(action.value)
        elif action.action_type == "use_param":
            new_state.body_tokens.append(action.value)
        elif action.action_type == "call_function":
            new_state.body_tokens.append(f"{action.value}(")
        elif action.action_type == "add_arg":
            if new_state.body_tokens and new_state.body_tokens[-1].endswith("("):
                new_state.body_tokens.append(f"{action.value})")
            else:
                new_state.body_tokens.append(f", {action.value}")
        elif action.action_type == "complete":
            new_state.is_complete = True
        
        new_state.depth += 1
        return new_state
    
    def _simulate(self, node: MCTSNode, target_task: str = None) -> float:
        """Simulate from a node to get a reward"""
        if node.state.is_complete:
            return self.reward_model.evaluate_program(node.state, target_task)
        
        # For incomplete nodes, do a quick rollout
        current_state = node.state.clone()
        max_depth = 5
        
        for _ in range(max_depth):
            if current_state.is_complete:
                break
                
            actions = self.action_generator.get_possible_actions(current_state)
            if not actions:
                break
                
            # Pick a random action for simulation
            action = random.choice(actions)
            if action.action_type == "complete" or random.random() < 0.3:
                current_state.is_complete = True
                break
            else:
                current_state = self._apply_action(current_state, action)
        
        if not current_state.is_complete:
            current_state.is_complete = True
        
        return self.reward_model.evaluate_program(current_state, target_task)