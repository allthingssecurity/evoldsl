import random
import copy
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from dsl import DSL, DSLFunction, DSLType
from mcts import ProgramState, MCTSProgramSynthesis, LLMRewardModel
import ast
import inspect

@dataclass
class EvolutionCandidate:
    """Represents a function candidate for evolution"""
    function: DSLFunction
    source_programs: List[ProgramState]  # Programs that led to this function
    generation: int = 0
    parent_functions: List[str] = None
    
    def __post_init__(self):
        if self.parent_functions is None:
            self.parent_functions = []

class LLMEvolutionGuide:
    """Simulates LLM guidance for evolutionary mutations"""
    
    def __init__(self):
        self.mutation_strategies = [
            "generalize_parameters",
            "add_error_handling", 
            "combine_functions",
            "add_recursion",
            "optimize_performance",
            "add_edge_cases"
        ]
    
    def suggest_mutations(self, function: DSLFunction, dsl: DSL, top_k: int = 3) -> List[Tuple[str, Dict[str, Any]]]:
        """Suggest mutations for a function"""
        suggestions = []
        
        # Analyze function to determine best mutations
        for strategy in self.mutation_strategies:
            score = self._score_mutation_strategy(function, strategy, dsl)
            mutation_params = self._generate_mutation_params(function, strategy, dsl)
            suggestions.append((strategy, score, mutation_params))
        
        # Sort by score and return top-k
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [(strategy, params) for strategy, score, params in suggestions[:top_k]]
    
    def _score_mutation_strategy(self, function: DSLFunction, strategy: str, dsl: DSL) -> float:
        """Score how good a mutation strategy is for this function"""
        base_score = 0.5
        
        if strategy == "generalize_parameters":
            # Good for simple functions with hardcoded values
            if function.body and any(char.isdigit() for char in function.body):
                base_score += 0.3
        
        elif strategy == "combine_functions":
            # Good if there are compatible functions in DSL
            compatible_funcs = [f for f in dsl.functions.values() 
                             if f != function and len(f.params) <= 2]
            if len(compatible_funcs) >= 2:
                base_score += 0.4
        
        elif strategy == "add_recursion":
            # Good for functions that could benefit from recursion
            if function.name in ["factorial", "fibonacci", "sum", "count"]:
                base_score += 0.5
            elif "n" in function.params:
                base_score += 0.2
        
        elif strategy == "add_error_handling":
            # Good for functions with potential failure points
            if function.body and ("div" in function.body or "/" in function.body):
                base_score += 0.3
        
        # Add randomness to simulate LLM uncertainty
        base_score += random.random() * 0.1
        return min(base_score, 1.0)
    
    def _generate_mutation_params(self, function: DSLFunction, strategy: str, dsl: DSL) -> Dict[str, Any]:
        """Generate parameters for a specific mutation strategy"""
        if strategy == "generalize_parameters":
            return {
                "new_param_name": f"param_{len(function.params)}",
                "target_value": "1" if "1" in str(function.body) else "0"
            }
        
        elif strategy == "combine_functions":
            compatible_funcs = [f.name for f in dsl.functions.values() 
                             if f != function and len(f.params) <= 2]
            if compatible_funcs:
                return {
                    "combine_with": random.choice(compatible_funcs),
                    "combination_type": random.choice(["compose", "parallel", "conditional"])
                }
        
        elif strategy == "add_recursion":
            return {
                "base_case": "n <= 1",
                "recursive_call": f"{function.name}(n-1)"
            }
        
        elif strategy == "add_error_handling":
            return {
                "error_condition": "y == 0" if "y" in function.params else "x == 0",
                "fallback_value": "0"
            }
        
        return {}

class EvolutionEngine:
    """Main evolution engine for discovering new DSL functions"""
    
    def __init__(self, dsl: DSL):
        self.dsl = dsl
        self.evolution_guide = LLMEvolutionGuide()
        self.reward_model = LLMRewardModel()
        self.population: List[EvolutionCandidate] = []
        self.generation = 0
        self.mutation_cache = {}
    
    def seed_population(self, mcts_results: List[ProgramState]):
        """Seed evolution population with MCTS results"""
        for i, program in enumerate(mcts_results):
            if program.is_complete:
                # Convert program to DSL function
                function = self._program_to_function(program, f"evolved_func_{i}")
                if function:
                    candidate = EvolutionCandidate(
                        function=function,
                        source_programs=[program],
                        generation=0
                    )
                    self.population.append(candidate)
    
    def evolve(self, generations: int = 10, population_size: int = 20) -> List[DSLFunction]:
        """Run evolution to discover new functions"""
        best_functions = []
        
        for gen in range(generations):
            self.generation = gen
            
            # Generate new candidates through mutation
            new_candidates = self._generate_mutations()
            
            # Evaluate all candidates
            all_candidates = self.population + new_candidates
            evaluated_candidates = self._evaluate_candidates(all_candidates)
            
            # Select best candidates for next generation
            self.population = self._select_survivors(evaluated_candidates, population_size)
            
            # Track best functions from this generation
            gen_best = sorted(self.population, key=lambda c: c.function.fitness_score, reverse=True)[:3]
            best_functions.extend([c.function for c in gen_best])
            
            print(f"Generation {gen}: Best fitness = {gen_best[0].function.fitness_score:.3f}")
        
        # Return top functions across all generations
        all_functions = [c.function for c in self.population]
        all_functions.sort(key=lambda f: f.fitness_score, reverse=True)
        return all_functions[:10]
    
    def _program_to_function(self, program: ProgramState, name: str) -> Optional[DSLFunction]:
        """Convert a program state to a DSL function"""
        try:
            code = program.to_code()
            
            # Parse the function to extract implementation
            tree = ast.parse(code)
            func_def = tree.body[0]
            
            if not isinstance(func_def, ast.FunctionDef):
                return None
            
            # Extract parameter information
            params = [arg.arg for arg in func_def.args.args]
            
            # Create executable implementation
            namespace = {}
            namespace.update({name: func for name, func in self.dsl.functions.items()})
            
            exec(code, namespace)
            implementation = namespace[program.function_name]
            
            # Create DSL function
            dsl_func = DSLFunction(
                name=name,
                params=params,
                param_types=[DSLType.ANY] * len(params),  # Default to ANY for now
                return_type=DSLType.ANY,
                body=code,
                implementation=implementation
            )
            
            return dsl_func
            
        except Exception as e:
            print(f"Error converting program to function: {e}")
            return None
    
    def _generate_mutations(self) -> List[EvolutionCandidate]:
        """Generate mutations of current population"""
        new_candidates = []
        
        for candidate in self.population:
            # Get mutation suggestions from LLM
            mutations = self.evolution_guide.suggest_mutations(candidate.function, self.dsl)
            
            for strategy, params in mutations:
                mutated_func = self._apply_mutation(candidate.function, strategy, params)
                if mutated_func:
                    new_candidate = EvolutionCandidate(
                        function=mutated_func,
                        source_programs=candidate.source_programs,
                        generation=self.generation + 1,
                        parent_functions=[candidate.function.name]
                    )
                    new_candidates.append(new_candidate)
        
        return new_candidates
    
    def _apply_mutation(self, function: DSLFunction, strategy: str, params: Dict[str, Any]) -> Optional[DSLFunction]:
        """Apply a specific mutation strategy"""
        try:
            if strategy == "generalize_parameters":
                return self._mutate_generalize_parameters(function, params)
            elif strategy == "combine_functions":
                return self._mutate_combine_functions(function, params)
            elif strategy == "add_recursion":
                return self._mutate_add_recursion(function, params)
            elif strategy == "add_error_handling":
                return self._mutate_add_error_handling(function, params)
            else:
                return None
        except Exception as e:
            print(f"Mutation error ({strategy}): {e}")
            return None
    
    def _mutate_generalize_parameters(self, function: DSLFunction, params: Dict[str, Any]) -> Optional[DSLFunction]:
        """Generalize hardcoded values to parameters"""
        if not function.body:
            return None
        
        new_name = f"{function.name}_generalized"
        new_params = function.params + [params["new_param_name"]]
        new_body = function.body.replace(params["target_value"], params["new_param_name"])
        
        # Try to create new implementation
        try:
            namespace = {}
            namespace.update({name: func for name, func in self.dsl.functions.items()})
            exec(new_body, namespace)
            new_impl = namespace[function.name]
            
            return DSLFunction(
                name=new_name,
                params=new_params,
                param_types=[DSLType.ANY] * len(new_params),
                return_type=function.return_type,
                body=new_body,
                implementation=new_impl
            )
        except:
            return None
    
    def _mutate_combine_functions(self, function: DSLFunction, params: Dict[str, Any]) -> Optional[DSLFunction]:
        """Combine this function with another"""
        combine_with = params.get("combine_with")
        if not combine_with or combine_with not in self.dsl.functions:
            return None
        
        other_func = self.dsl.functions[combine_with]
        combination_type = params.get("combination_type", "compose")
        
        new_name = f"{function.name}_{combination_type}_{combine_with}"
        
        if combination_type == "compose":
            # f(g(x))
            new_body = f"def {new_name}({', '.join(function.params)}):\n"
            new_body += f"    temp = {combine_with}({', '.join(function.params[:len(other_func.params)])})\n"
            new_body += f"    return {function.name}(temp)"
        
        elif combination_type == "parallel":
            # f(x) + g(x)
            new_body = f"def {new_name}({', '.join(function.params)}):\n"
            new_body += f"    result1 = {function.name}({', '.join(function.params)})\n"
            new_body += f"    result2 = {combine_with}({', '.join(function.params[:len(other_func.params)])})\n"
            new_body += f"    return add(result1, result2)"
        
        else:  # conditional
            new_body = f"def {new_name}({', '.join(function.params)}):\n"
            new_body += f"    if {function.params[0] if function.params else 'True'}:\n"
            new_body += f"        return {function.name}({', '.join(function.params)})\n"
            new_body += f"    else:\n"
            new_body += f"        return {combine_with}({', '.join(function.params[:len(other_func.params)])})"
        
        try:
            namespace = {}
            namespace.update({name: func for name, func in self.dsl.functions.items()})
            exec(new_body, namespace)
            new_impl = namespace[new_name]
            
            return DSLFunction(
                name=new_name,
                params=function.params,
                param_types=function.param_types,
                return_type=function.return_type,
                body=new_body,
                implementation=new_impl
            )
        except:
            return None
    
    def _mutate_add_recursion(self, function: DSLFunction, params: Dict[str, Any]) -> Optional[DSLFunction]:
        """Add recursive structure to function"""
        if "n" not in function.params:
            return None
        
        new_name = f"{function.name}_recursive"
        base_case = params.get("base_case", "n <= 1")
        recursive_call = params.get("recursive_call", f"{function.name}(n-1)")
        
        new_body = f"def {new_name}({', '.join(function.params)}):\n"
        new_body += f"    if {base_case}:\n"
        new_body += f"        return 1\n"
        new_body += f"    else:\n"
        new_body += f"        return mul({function.params[0]}, {recursive_call})"
        
        try:
            namespace = {}
            namespace.update({name: func for name, func in self.dsl.functions.items()})
            exec(new_body, namespace)
            new_impl = namespace[new_name]
            
            return DSLFunction(
                name=new_name,
                params=function.params,
                param_types=function.param_types,
                return_type=function.return_type,
                body=new_body,
                implementation=new_impl
            )
        except:
            return None
    
    def _mutate_add_error_handling(self, function: DSLFunction, params: Dict[str, Any]) -> Optional[DSLFunction]:
        """Add error handling to function"""
        error_condition = params.get("error_condition", "False")
        fallback_value = params.get("fallback_value", "0")
        
        new_name = f"{function.name}_safe"
        new_body = f"def {new_name}({', '.join(function.params)}):\n"
        new_body += f"    if {error_condition}:\n"
        new_body += f"        return {fallback_value}\n"
        new_body += f"    else:\n"
        new_body += f"        return {function.name}({', '.join(function.params)})"
        
        try:
            namespace = {}
            namespace.update({name: func for name, func in self.dsl.functions.items()})
            exec(new_body, namespace)
            new_impl = namespace[new_name]
            
            return DSLFunction(
                name=new_name,
                params=function.params,
                param_types=function.param_types,
                return_type=function.return_type,
                body=new_body,
                implementation=new_impl
            )
        except:
            return None
    
    def _evaluate_candidates(self, candidates: List[EvolutionCandidate]) -> List[EvolutionCandidate]:
        """Evaluate fitness of all candidates"""
        for candidate in candidates:
            if candidate.function.fitness_score == 0.0:  # Not evaluated yet
                # Create a dummy program state for evaluation
                dummy_state = ProgramState(
                    function_name=candidate.function.name,
                    params=candidate.function.params,
                    return_type=str(candidate.function.return_type.value),
                    body_tokens=[],
                    is_complete=True
                )
                dummy_state.body_tokens = [candidate.function.body] if candidate.function.body else []
                
                # Evaluate using reward model
                fitness = self._evaluate_function_fitness(candidate.function)
                candidate.function.fitness_score = fitness
        
        return candidates
    
    def _evaluate_function_fitness(self, function: DSLFunction) -> float:
        """Evaluate fitness of a function"""
        score = 0.0
        
        # Correctness: Can the function execute without errors?
        try:
            if hasattr(function, 'implementation') and function.implementation:
                # Test with some sample inputs
                test_inputs = [(1, 2), (0, 1), (5, 3)]
                for inputs in test_inputs:
                    try:
                        result = function.implementation(*inputs[:len(function.params)])
                        score += 0.1  # Successful execution
                    except:
                        pass
        except:
            pass
        
        # Novelty: Is this function different from existing ones?
        existing_names = [f.name for f in self.dsl.functions.values()]
        if function.name not in existing_names:
            score += 0.2
        
        # Complexity: Prefer functions that do meaningful computation
        if function.body:
            if len(function.body.split()) > 5:  # Non-trivial
                score += 0.1
            if any(op in function.body for op in ['if', 'for', 'while']):
                score += 0.2
        
        # Utility: Functions that could be useful building blocks
        if function.name.endswith('_safe'):  # Error handling
            score += 0.15
        if function.name.endswith('_recursive'):  # Recursion
            score += 0.15
        if 'generalized' in function.name:  # Generalization
            score += 0.1
        
        return min(score, 1.0)
    
    def _select_survivors(self, candidates: List[EvolutionCandidate], population_size: int) -> List[EvolutionCandidate]:
        """Select survivors for next generation"""
        # Sort by fitness
        candidates.sort(key=lambda c: c.function.fitness_score, reverse=True)
        
        # Keep top performers
        survivors = candidates[:population_size // 2]
        
        # Add some diversity by including random selection from rest
        remaining = candidates[population_size // 2:]
        if remaining:
            random_survivors = random.sample(remaining, min(len(remaining), population_size // 2))
            survivors.extend(random_survivors)
        
        return survivors[:population_size]