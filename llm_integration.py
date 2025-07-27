"""
GPT-4o integration for policy and value models in MCTS + Evolution system
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import openai
from openai import OpenAI
import time

from dsl import DSL, DSLFunction
from mcts import ProgramState, MCTSAction

@dataclass
class LLMConfig:
    """Configuration for LLM integration"""
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 1000
    timeout: float = 30.0
    max_retries: int = 3
    rate_limit_delay: float = 0.1

class GPT4PolicyModel:
    """GPT-4o based policy model for MCTS action selection"""
    
    def __init__(self, config: LLMConfig = None):
        self.config = config or LLMConfig()
        self.client = OpenAI()
        self.call_count = 0
        self.cache = {}
    
    async def suggest_actions(self, state: ProgramState, available_actions: List[MCTSAction], 
                            dsl: DSL, target_task: str = None, top_k: int = 3) -> List[Tuple[MCTSAction, float]]:
        """Use GPT-4o to suggest best actions for current program state"""
        
        # Create cache key
        cache_key = self._create_cache_key(state, available_actions, target_task)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        prompt = self._create_policy_prompt(state, available_actions, dsl, target_task)
        
        try:
            response = await self._call_gpt4o(prompt)
            scored_actions = self._parse_policy_response(response, available_actions)
            
            # Cache result
            self.cache[cache_key] = scored_actions[:top_k]
            return scored_actions[:top_k]
            
        except Exception as e:
            print(f"GPT-4o policy error: {e}")
            # Fallback to random selection
            return [(action, 0.5) for action in available_actions[:top_k]]
    
    def _create_policy_prompt(self, state: ProgramState, actions: List[MCTSAction], 
                            dsl: DSL, target_task: str = None) -> str:
        """Create prompt for policy evaluation"""
        
        current_code = state.to_code()
        available_functions = ", ".join(dsl.list_functions())
        
        prompt = f"""You are an expert programming assistant helping to build functions using a Domain Specific Language (DSL).

CURRENT PROGRAM STATE:
```python
{current_code}
```

AVAILABLE DSL FUNCTIONS: {available_functions}

TARGET TASK: {target_task or "Create a useful function"}

AVAILABLE ACTIONS:
"""
        
        for i, action in enumerate(actions):
            prompt += f"{i+1}. {action.action_type}: {action.value} - {action.description}\n"
        
        prompt += """
INSTRUCTIONS:
1. Analyze the current program state and target task
2. For each action, provide a score from 0.0 to 1.0 indicating how promising it is
3. Consider: correctness, progress toward target, code elegance, reusability
4. Respond ONLY with a JSON object mapping action numbers to scores

EXAMPLE RESPONSE:
{"1": 0.8, "2": 0.3, "3": 0.9, "4": 0.1}

RESPONSE:"""
        
        return prompt
    
    def _parse_policy_response(self, response: str, actions: List[MCTSAction]) -> List[Tuple[MCTSAction, float]]:
        """Parse GPT-4o response into scored actions"""
        try:
            scores = json.loads(response.strip())
            scored_actions = []
            
            for i, action in enumerate(actions):
                action_key = str(i + 1)
                score = float(scores.get(action_key, 0.5))
                scored_actions.append((action, score))
            
            # Sort by score descending
            scored_actions.sort(key=lambda x: x[1], reverse=True)
            return scored_actions
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing policy response: {e}")
            # Fallback: assign random scores
            return [(action, 0.5) for action in actions]
    
    async def _call_gpt4o(self, prompt: str) -> str:
        """Make API call to GPT-4o with retries"""
        
        for attempt in range(self.config.max_retries):
            try:
                self.call_count += 1
                
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=[
                        {"role": "system", "content": "You are a programming expert. Respond only with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens
                )
                
                await asyncio.sleep(self.config.rate_limit_delay)
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                print(f"GPT-4o API call attempt {attempt + 1} failed: {e}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
    
    def _create_cache_key(self, state: ProgramState, actions: List[MCTSAction], target_task: str) -> str:
        """Create cache key for memoization"""
        action_sig = "_".join(f"{a.action_type}:{a.value}" for a in actions[:5])
        return f"{state.function_name}_{len(state.body_tokens)}_{action_sig}_{target_task or 'default'}"

class GPT4ValueModel:
    """GPT-4o based value model for program evaluation"""
    
    def __init__(self, config: LLMConfig = None):
        self.config = config or LLMConfig()
        self.client = OpenAI()
        self.call_count = 0
        self.cache = {}
    
    async def evaluate_program(self, state: ProgramState, target_task: str = None, 
                             dsl: DSL = None) -> float:
        """Use GPT-4o to evaluate program quality and potential"""
        
        if not state.is_complete:
            return await self._evaluate_partial_program(state, target_task, dsl)
        
        cache_key = f"{state.to_code()}_{target_task or 'default'}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        prompt = self._create_value_prompt(state, target_task, dsl)
        
        try:
            response = await self._call_gpt4o(prompt)
            value = self._parse_value_response(response)
            
            self.cache[cache_key] = value
            return value
            
        except Exception as e:
            print(f"GPT-4o value error: {e}")
            return 0.5  # Neutral fallback
    
    def _create_value_prompt(self, state: ProgramState, target_task: str = None, dsl: DSL = None) -> str:
        """Create prompt for value evaluation"""
        
        current_code = state.to_code()
        available_functions = ", ".join(dsl.list_functions()) if dsl else "standard functions"
        
        prompt = f"""You are an expert code reviewer evaluating the quality and potential of a function.

FUNCTION TO EVALUATE:
```python
{current_code}
```

TARGET TASK: {target_task or "General purpose function"}
AVAILABLE DSL FUNCTIONS: {available_functions}

EVALUATION CRITERIA:
1. Correctness: Does the function work without errors?
2. Relevance: How well does it address the target task?
3. Elegance: Is the code clean, readable, and well-structured?
4. Reusability: Could this function be useful in other contexts?
5. Novelty: Does this represent a meaningful new capability?

INSTRUCTIONS:
- Analyze the function against each criterion
- Provide a single score from 0.0 to 1.0 (0.0 = terrible, 1.0 = excellent)
- Consider both current quality and future potential
- Respond ONLY with a single number

RESPONSE:"""
        
        return prompt
    
    async def _evaluate_partial_program(self, state: ProgramState, target_task: str = None, 
                                      dsl: DSL = None) -> float:
        """Evaluate incomplete programs based on potential"""
        
        current_code = state.to_code()
        progress = len(state.body_tokens) / 10.0  # Assume 10 tokens is reasonable length
        
        prompt = f"""You are evaluating a partially complete function for its potential.

PARTIAL FUNCTION:
```python
{current_code}
```

CURRENT PROGRESS: {len(state.body_tokens)} tokens written
TARGET TASK: {target_task or "General purpose function"}

INSTRUCTIONS:
- Assess how promising this partial function looks
- Consider: logical structure, meaningful variable usage, appropriate complexity
- Score from 0.0 (poor potential) to 1.0 (excellent potential)
- Factor in that this is incomplete - judge the trajectory, not final result
- Respond ONLY with a single number between 0.0 and 1.0

RESPONSE:"""
        
        try:
            response = await self._call_gpt4o(prompt)
            base_value = self._parse_value_response(response)
            
            # Discount for incompleteness
            return base_value * min(progress, 0.8)  # Max 80% value for incomplete programs
            
        except Exception as e:
            print(f"Error evaluating partial program: {e}")
            return 0.3  # Conservative fallback for partial programs
    
    def _parse_value_response(self, response: str) -> float:
        """Parse GPT-4o value response"""
        try:
            # Extract number from response
            cleaned = response.strip()
            
            # Try to parse as direct float
            try:
                value = float(cleaned)
                return max(0.0, min(1.0, value))  # Clamp to [0, 1]
            except ValueError:
                # Try to extract first number found
                import re
                numbers = re.findall(r'0\.\d+|\d+\.\d+', cleaned)
                if numbers:
                    value = float(numbers[0])
                    return max(0.0, min(1.0, value))
                else:
                    return 0.5  # Fallback
                    
        except Exception as e:
            print(f"Error parsing value response: {e}")
            return 0.5
    
    async def _call_gpt4o(self, prompt: str) -> str:
        """Make API call to GPT-4o with retries"""
        
        for attempt in range(self.config.max_retries):
            try:
                self.call_count += 1
                
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=[
                        {"role": "system", "content": "You are a code evaluation expert. Respond only with a number between 0.0 and 1.0."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,  # Lower temperature for value evaluation
                    max_tokens=50  # Short response expected
                )
                
                await asyncio.sleep(self.config.rate_limit_delay)
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                print(f"GPT-4o API call attempt {attempt + 1} failed: {e}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise

class GPT4EvolutionGuide:
    """GPT-4o based guide for evolution mutations"""
    
    def __init__(self, config: LLMConfig = None):
        self.config = config or LLMConfig()
        self.client = OpenAI()
        self.call_count = 0
    
    async def suggest_mutations(self, function: DSLFunction, dsl: DSL, 
                              top_k: int = 3) -> List[Tuple[str, Dict[str, Any]]]:
        """Use GPT-4o to suggest evolutionary mutations"""
        
        prompt = self._create_mutation_prompt(function, dsl)
        
        try:
            response = await self._call_gpt4o(prompt)
            mutations = self._parse_mutation_response(response)
            return mutations[:top_k]
            
        except Exception as e:
            print(f"GPT-4o mutation error: {e}")
            # Fallback to simple mutations
            return [
                ("generalize_parameters", {"new_param": "param_new"}),
                ("add_error_handling", {"condition": "input validation"}),
                ("optimize_performance", {"strategy": "memoization"})
            ][:top_k]
    
    def _create_mutation_prompt(self, function: DSLFunction, dsl: DSL) -> str:
        """Create prompt for mutation suggestions"""
        
        available_functions = ", ".join(dsl.list_functions())
        
        prompt = f"""You are an expert in evolutionary programming, suggesting mutations for function improvement.

CURRENT FUNCTION:
Name: {function.name}
Parameters: {function.params}
Body: {function.body or "No implementation"}
Fitness Score: {function.fitness_score}

AVAILABLE DSL FUNCTIONS: {available_functions}

MUTATION STRATEGIES:
1. generalize_parameters - Replace hardcoded values with parameters
2. combine_functions - Combine with other DSL functions
3. add_recursion - Add recursive structure
4. add_error_handling - Add safety checks
5. optimize_performance - Improve efficiency
6. add_edge_cases - Handle special cases

INSTRUCTIONS:
- Suggest 3-5 promising mutations for this function
- For each mutation, specify the strategy and key parameters
- Focus on improvements that would increase fitness/utility
- Respond with JSON format

EXAMPLE RESPONSE:
[
  {"strategy": "generalize_parameters", "params": {"target_value": "1", "new_param": "threshold"}},
  {"strategy": "combine_functions", "params": {"combine_with": "add", "type": "compose"}},
  {"strategy": "add_error_handling", "params": {"condition": "x < 0", "fallback": "0"}}
]

RESPONSE:"""
        
        return prompt
    
    def _parse_mutation_response(self, response: str) -> List[Tuple[str, Dict[str, Any]]]:
        """Parse GPT-4o mutation response"""
        try:
            mutations_data = json.loads(response.strip())
            mutations = []
            
            for mutation in mutations_data:
                strategy = mutation.get("strategy", "generalize_parameters")
                params = mutation.get("params", {})
                mutations.append((strategy, params))
            
            return mutations
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing mutation response: {e}")
            # Fallback mutations
            return [
                ("generalize_parameters", {}),
                ("add_error_handling", {}),
                ("combine_functions", {})
            ]
    
    async def _call_gpt4o(self, prompt: str) -> str:
        """Make API call to GPT-4o"""
        
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": "You are an evolutionary programming expert. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        
        await asyncio.sleep(self.config.rate_limit_delay)
        return response.choices[0].message.content.strip()

class LLMStats:
    """Track LLM usage statistics"""
    
    def __init__(self):
        self.policy_calls = 0
        self.value_calls = 0
        self.mutation_calls = 0
        self.total_tokens = 0
        self.start_time = time.time()
    
    def update_stats(self, model_type: str, tokens_used: int = 0):
        """Update usage statistics"""
        if model_type == "policy":
            self.policy_calls += 1
        elif model_type == "value":
            self.value_calls += 1
        elif model_type == "mutation":
            self.mutation_calls += 1
        
        self.total_tokens += tokens_used
    
    def get_summary(self) -> Dict[str, Any]:
        """Get usage summary"""
        elapsed_time = time.time() - self.start_time
        return {
            "policy_calls": self.policy_calls,
            "value_calls": self.value_calls,
            "mutation_calls": self.mutation_calls,
            "total_calls": self.policy_calls + self.value_calls + self.mutation_calls,
            "estimated_tokens": self.total_tokens,
            "elapsed_time": elapsed_time,
            "calls_per_minute": (self.policy_calls + self.value_calls + self.mutation_calls) / (elapsed_time / 60) if elapsed_time > 0 else 0
        }