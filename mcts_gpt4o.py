"""
GPT-4o integrated MCTS and Evolution system
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from dsl import DSL, DSLFunction
from mcts import MCTSProgramSynthesis, ProgramState, MCTSAction, MCTSNode, ActionGenerator
from evolution import EvolutionEngine, EvolutionCandidate
from llm_integration import GPT4PolicyModel, GPT4ValueModel, GPT4EvolutionGuide, LLMConfig, LLMStats

class GPT4MCTSProgramSynthesis(MCTSProgramSynthesis):
    """MCTS Program Synthesis with GPT-4o integration"""
    
    def __init__(self, dsl: DSL, target_function_name: str = "synthesized_func", llm_config: LLMConfig = None):
        super().__init__(dsl, target_function_name)
        
        # Replace mock models with GPT-4o models
        self.policy_model = GPT4PolicyModel(llm_config)
        self.value_model = GPT4ValueModel(llm_config)
        self.stats = LLMStats()
    
    async def search_async(self, iterations: int = 100, target_task: str = None) -> List[ProgramState]:
        """Async version of MCTS search with GPT-4o"""
        
        print(f"Starting GPT-4o MCTS search: {iterations} iterations for task '{target_task}'")
        
        # Initialize root
        initial_state = ProgramState(
            function_name=self.target_function_name,
            params=["x", "y"],
            return_type="int"
        )
        self.root = MCTSNode(initial_state)
        
        for i in range(iterations):
            if i % 10 == 0:
                print(f"  MCTS iteration {i}/{iterations}")
            
            # Selection
            node = self._select(self.root)
            
            # Expansion (with GPT-4o policy)
            if not node.state.is_complete and not node.is_fully_expanded():
                node = await self._expand_async(node, target_task)
            
            # Simulation (with GPT-4o value)
            reward = await self._simulate_async(node, target_task)
            
            # Backpropagation
            node.backpropagate(reward)
            
            # Track best programs
            if node.state.is_complete and reward > 0.5:
                self.best_programs.append((node.state.clone(), reward))
        
        # Return best programs found
        self.best_programs.sort(key=lambda x: x[1], reverse=True)
        
        print(f"MCTS search complete. Found {len(self.best_programs)} high-quality programs")
        print(f"LLM calls - Policy: {self.policy_model.call_count}, Value: {self.value_model.call_count}")
        
        return [prog for prog, score in self.best_programs[:10]]
    
    async def _expand_async(self, node: MCTSNode, target_task: str = None) -> MCTSNode:
        """Async expansion with GPT-4o policy guidance"""
        
        if not node.is_expanded:
            # Get possible actions
            actions = self.action_generator.get_possible_actions(node.state)
            
            if actions:
                # Use GPT-4o to get top actions
                suggested_actions = await self.policy_model.suggest_actions(
                    node.state, actions, self.dsl, target_task
                )
                node.untried_actions = [action for action, score in suggested_actions]
                self.stats.update_stats("policy")
            
            node.is_expanded = True
        
        if node.untried_actions:
            # Pick the next untried action
            action = node.untried_actions.pop(0)
            
            # Apply action to create new state
            new_state = self._apply_action(node.state, action)
            
            # Create and return new child
            return node.add_child(action, new_state)
        
        return node
    
    async def _simulate_async(self, node: MCTSNode, target_task: str = None) -> float:
        """Async simulation with GPT-4o value evaluation"""
        
        if node.state.is_complete:
            reward = await self.value_model.evaluate_program(node.state, target_task, self.dsl)
            self.stats.update_stats("value")
            return reward
        
        # For incomplete nodes, do a quick rollout then evaluate
        current_state = node.state.clone()
        max_depth = 5
        
        for _ in range(max_depth):
            if current_state.is_complete:
                break
                
            actions = self.action_generator.get_possible_actions(current_state)
            if not actions:
                break
            
            # Use GPT-4o for some rollout decisions
            if len(actions) > 1 and len(current_state.body_tokens) < 3:
                try:
                    suggested_actions = await self.policy_model.suggest_actions(
                        current_state, actions[:3], self.dsl, target_task, top_k=1
                    )
                    if suggested_actions:
                        action = suggested_actions[0][0]
                    else:
                        action = actions[0]
                    self.stats.update_stats("policy")
                except:
                    action = actions[0]  # Fallback
            else:
                action = actions[0]  # Quick rollout
            
            if action.action_type == "complete" or len(current_state.body_tokens) >= 4:
                current_state.is_complete = True
                break
            else:
                current_state = self._apply_action(current_state, action)
        
        if not current_state.is_complete:
            current_state.is_complete = True
        
        reward = await self.value_model.evaluate_program(current_state, target_task, self.dsl)
        self.stats.update_stats("value")
        return reward * 0.8  # Discount for rollout uncertainty

class GPT4EvolutionEngine(EvolutionEngine):
    """Evolution Engine with GPT-4o integration"""
    
    def __init__(self, dsl: DSL, llm_config: LLMConfig = None):
        super().__init__(dsl)
        
        # Replace mock evolution guide with GPT-4o
        self.evolution_guide = GPT4EvolutionGuide(llm_config)
        self.value_model = GPT4ValueModel(llm_config)
        self.stats = LLMStats()
    
    async def evolve_async(self, generations: int = 10, population_size: int = 20) -> List[DSLFunction]:
        """Async evolution with GPT-4o guidance"""
        
        print(f"Starting GPT-4o Evolution: {generations} generations, population size {population_size}")
        best_functions = []
        
        for gen in range(generations):
            print(f"  Evolution generation {gen}/{generations}")
            
            # Generate new candidates through mutation (with GPT-4o)
            new_candidates = await self._generate_mutations_async()
            
            # Evaluate all candidates (with GPT-4o)
            all_candidates = self.population + new_candidates
            evaluated_candidates = await self._evaluate_candidates_async(all_candidates)
            
            # Select best candidates for next generation
            self.population = self._select_survivors(evaluated_candidates, population_size)
            
            # Track best functions from this generation
            gen_best = sorted(self.population, key=lambda c: c.function.fitness_score, reverse=True)[:3]
            best_functions.extend([c.function for c in gen_best])
            
            best_fitness = gen_best[0].function.fitness_score if gen_best else 0.0
            print(f"    Generation {gen}: Best fitness = {best_fitness:.3f}")
        
        # Return top functions across all generations
        all_functions = [c.function for c in self.population]
        all_functions.sort(key=lambda f: f.fitness_score, reverse=True)
        
        print(f"Evolution complete. LLM calls - Mutations: {self.evolution_guide.call_count}, Evaluations: {self.value_model.call_count}")
        
        return all_functions[:10]
    
    async def _generate_mutations_async(self) -> List[EvolutionCandidate]:
        """Generate mutations using GPT-4o guidance"""
        
        new_candidates = []
        
        for candidate in self.population:
            try:
                # Get mutation suggestions from GPT-4o
                mutations = await self.evolution_guide.suggest_mutations(candidate.function, self.dsl)
                self.stats.update_stats("mutation")
                
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
            
            except Exception as e:
                print(f"Error generating mutations for {candidate.function.name}: {e}")
                continue
        
        return new_candidates
    
    async def _evaluate_candidates_async(self, candidates: List[EvolutionCandidate]) -> List[EvolutionCandidate]:
        """Evaluate candidates using GPT-4o value model"""
        
        for candidate in candidates:
            if candidate.function.fitness_score == 0.0:  # Not evaluated yet
                try:
                    # Create a dummy program state for evaluation
                    dummy_state = ProgramState(
                        function_name=candidate.function.name,
                        params=candidate.function.params,
                        return_type=str(candidate.function.return_type.value),
                        body_tokens=[candidate.function.body] if candidate.function.body else [],
                        is_complete=True
                    )
                    
                    # Evaluate using GPT-4o value model
                    fitness = await self.value_model.evaluate_program(dummy_state, dsl=self.dsl)
                    candidate.function.fitness_score = fitness
                    self.stats.update_stats("value")
                    
                except Exception as e:
                    print(f"Error evaluating {candidate.function.name}: {e}")
                    candidate.function.fitness_score = 0.1  # Low fallback score
        
        return candidates

class GPT4BootstrapSystem:
    """Main bootstrap system with GPT-4o integration"""
    
    def __init__(self, initial_dsl: Optional[DSL] = None, llm_config: LLMConfig = None):
        self.dsl = initial_dsl if initial_dsl else DSL()
        self.llm_config = llm_config or LLMConfig()
        self.cycles = []
        self.stats = LLMStats()
    
    async def run_bootstrap_cycle_async(self, 
                                      target_tasks: List[str] = None,
                                      mcts_iterations: int = 50,  # Reduced for LLM efficiency
                                      evolution_generations: int = 5,
                                      cycle_id: int = None) -> Dict[str, Any]:
        """Run one complete MCTS + Evolution cycle with GPT-4o"""
        
        if cycle_id is None:
            cycle_id = len(self.cycles)
        
        print(f"\n🚀 GPT-4o Bootstrap Cycle {cycle_id}")
        print(f"Starting DSL size: {len(self.dsl.functions)} functions")
        
        start_time = time.time()
        
        # Phase 1: MCTS Program Synthesis with GPT-4o
        print(f"📊 Phase 1: MCTS with GPT-4o ({mcts_iterations} iterations)")
        mcts_results = []
        
        if target_tasks is None:
            target_tasks = ["factorial", "fibonacci", "power"]
        
        for task in target_tasks:
            print(f"  🎯 Task: {task}")
            mcts = GPT4MCTSProgramSynthesis(self.dsl, f"synthesized_{task}", self.llm_config)
            task_results = await mcts.search_async(iterations=mcts_iterations, target_task=task)
            mcts_results.extend(task_results)
            
            # Update stats
            self.stats.policy_calls += mcts.stats.policy_calls
            self.stats.value_calls += mcts.stats.value_calls
        
        # Phase 2: Evolution with GPT-4o
        print(f"🧬 Phase 2: Evolution with GPT-4o ({evolution_generations} generations)")
        evolution_engine = GPT4EvolutionEngine(self.dsl, self.llm_config)
        evolution_engine.seed_population(mcts_results)
        evolved_functions = await evolution_engine.evolve_async(generations=evolution_generations)
        
        # Update stats
        self.stats.mutation_calls += evolution_engine.stats.mutation_calls
        self.stats.value_calls += evolution_engine.stats.value_calls
        
        # Phase 3: Integration
        print("🔗 Phase 3: Integrating new functions")
        new_functions = self._select_functions_for_integration(evolved_functions)
        
        for func in new_functions:
            self.dsl.add_function(func)
            print(f"  ✅ Added: {func.name} (fitness: {func.fitness_score:.3f})")
        
        end_time = time.time()
        cycle_time = end_time - start_time
        
        # Create cycle summary
        cycle_summary = {
            "cycle_id": cycle_id,
            "start_dsl_size": len(self.dsl.functions) - len(new_functions),
            "end_dsl_size": len(self.dsl.functions),
            "new_functions": len(new_functions),
            "mcts_programs": len(mcts_results),
            "evolved_functions": len(evolved_functions),
            "cycle_time": cycle_time,
            "llm_stats": self.stats.get_summary()
        }
        
        self.cycles.append(cycle_summary)
        
        print(f"✅ Cycle {cycle_id} complete:")
        print(f"  📈 Added {len(new_functions)} new functions")
        print(f"  🔢 DSL size: {cycle_summary['start_dsl_size']} → {cycle_summary['end_dsl_size']}")
        print(f"  ⏱️  Time: {cycle_time:.1f}s")
        print(f"  🤖 LLM calls: {self.stats.get_summary()['total_calls']}")
        
        return cycle_summary
    
    def _select_functions_for_integration(self, candidates: List[DSLFunction]) -> List[DSLFunction]:
        """Select which evolved functions to integrate into DSL"""
        selected = []
        
        # Sort by fitness
        candidates.sort(key=lambda f: f.fitness_score, reverse=True)
        
        for func in candidates:
            # Only integrate high-quality functions
            if func.fitness_score > 0.6:
                # Avoid duplicates
                if func.name not in self.dsl.functions:
                    # Avoid overly similar functions
                    if not self._is_too_similar_to_existing(func):
                        selected.append(func)
                        
                        # Limit growth per cycle for cost control
                        if len(selected) >= 2:
                            break
        
        return selected
    
    def _is_too_similar_to_existing(self, candidate: DSLFunction) -> bool:
        """Check if candidate is too similar to existing functions"""
        if not candidate.body:
            return False
        
        candidate_tokens = set(candidate.body.split())
        
        for existing_func in self.dsl.functions.values():
            if existing_func.body:
                existing_tokens = set(existing_func.body.split())
                # Simple similarity check based on token overlap
                overlap = len(candidate_tokens & existing_tokens) / len(candidate_tokens | existing_tokens)
                if overlap > 0.8:
                    return True
        
        return False

async def demo_gpt4o_system():
    """Demonstrate the GPT-4o integrated system"""
    
    print("🚀 GPT-4o MCTS + Evolution Coding Agent Demo")
    print("=" * 50)
    
    # Configure LLM
    config = LLMConfig(
        model="gpt-4o",
        temperature=0.7,
        max_tokens=500,
        rate_limit_delay=0.2  # Be nice to the API
    )
    
    # Create system
    system = GPT4BootstrapSystem(llm_config=config)
    
    print(f"📋 Initial DSL functions: {system.dsl.list_functions()}")
    
    try:
        # Run a few cycles
        for cycle in range(2):  # Limited cycles for demo
            summary = await system.run_bootstrap_cycle_async(
                target_tasks=["factorial", "fibonacci"],
                mcts_iterations=20,  # Smaller for demo
                evolution_generations=3,
                cycle_id=cycle
            )
        
        print("\n📊 Final Summary:")
        print(f"Total DSL functions: {len(system.dsl.functions)}")
        print(f"Total LLM calls: {system.stats.get_summary()['total_calls']}")
        print(f"Estimated cost: ~${system.stats.get_summary()['total_calls'] * 0.01:.2f}")
        
        print("\n📋 All DSL functions:")
        for name, func in system.dsl.functions.items():
            print(f"  {name}: fitness={func.fitness_score:.3f}")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        print("Make sure you have OPENAI_API_KEY set in your environment")

if __name__ == "__main__":
    asyncio.run(demo_gpt4o_system())