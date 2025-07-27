"""
Main integration system that combines MCTS and Evolution for self-bootstrapping DSL development
"""

from typing import List, Dict, Any, Optional
import json
import time
from dataclasses import dataclass

from dsl import DSL, DSLFunction, DSLType
from mcts import MCTSProgramSynthesis, ProgramState
from evolution import EvolutionEngine, EvolutionCandidate

@dataclass
class BootstrapCycle:
    """Represents one cycle of MCTS + Evolution"""
    cycle_id: int
    mcts_iterations: int
    evolution_generations: int
    starting_dsl_size: int
    ending_dsl_size: int
    best_programs: List[ProgramState]
    new_functions: List[DSLFunction]
    performance_metrics: Dict[str, float]
    timestamp: float

class BootstrapSystem:
    """Main system that orchestrates MCTS + Evolution cycles"""
    
    def __init__(self, initial_dsl: Optional[DSL] = None):
        self.dsl = initial_dsl if initial_dsl else DSL()
        self.cycles: List[BootstrapCycle] = []
        self.function_lineage: Dict[str, Dict[str, Any]] = {}
        self.performance_history: List[Dict[str, float]] = []
        
    def run_bootstrap_cycle(self, 
                          target_tasks: List[str] = None,
                          mcts_iterations: int = 100,
                          evolution_generations: int = 10,
                          cycle_id: int = None) -> BootstrapCycle:
        """Run one complete MCTS + Evolution cycle"""
        
        if cycle_id is None:
            cycle_id = len(self.cycles)
        
        print(f"\n=== Bootstrap Cycle {cycle_id} ===")
        print(f"Starting DSL size: {len(self.dsl.functions)} functions")
        
        starting_dsl_size = len(self.dsl.functions)
        start_time = time.time()
        
        # Phase 1: MCTS Program Synthesis
        print(f"Phase 1: Running MCTS for {mcts_iterations} iterations...")
        mcts_results = []
        
        if target_tasks is None:
            target_tasks = ["factorial", "fibonacci", "sum_list", "max_value"]
        
        for task in target_tasks:
            mcts = MCTSProgramSynthesis(self.dsl, target_function_name=f"synthesized_{task}")
            task_results = mcts.search(iterations=mcts_iterations, target_task=task)
            mcts_results.extend(task_results)
            print(f"  Task '{task}': Found {len(task_results)} candidate programs")
        
        # Phase 2: Evolution
        print(f"Phase 2: Running Evolution for {evolution_generations} generations...")
        evolution_engine = EvolutionEngine(self.dsl)
        evolution_engine.seed_population(mcts_results)
        evolved_functions = evolution_engine.evolve(generations=evolution_generations)
        
        # Phase 3: Select and integrate best functions
        print("Phase 3: Integrating new functions into DSL...")
        new_functions = self._select_functions_for_integration(evolved_functions)
        
        for func in new_functions:
            self.dsl.add_function(func)
            self._track_function_lineage(func, cycle_id)
        
        ending_dsl_size = len(self.dsl.functions)
        end_time = time.time()
        
        # Compute performance metrics
        metrics = self._compute_cycle_metrics(mcts_results, evolved_functions, end_time - start_time)
        
        # Create cycle record
        cycle = BootstrapCycle(
            cycle_id=cycle_id,
            mcts_iterations=mcts_iterations,
            evolution_generations=evolution_generations,
            starting_dsl_size=starting_dsl_size,
            ending_dsl_size=ending_dsl_size,
            best_programs=mcts_results[:10],  # Keep top 10
            new_functions=new_functions,
            performance_metrics=metrics,
            timestamp=start_time
        )
        
        self.cycles.append(cycle)
        self.performance_history.append(metrics)
        
        print(f"Cycle {cycle_id} complete:")
        print(f"  Added {len(new_functions)} new functions")
        print(f"  DSL grew from {starting_dsl_size} to {ending_dsl_size} functions")
        print(f"  Best fitness achieved: {metrics.get('best_fitness', 0):.3f}")
        print(f"  Time taken: {metrics.get('cycle_time', 0):.1f}s")
        
        return cycle
    
    def run_multiple_cycles(self, 
                          num_cycles: int = 5,
                          mcts_iterations: int = 100,
                          evolution_generations: int = 10) -> List[BootstrapCycle]:
        """Run multiple bootstrap cycles"""
        
        print(f"Starting {num_cycles} bootstrap cycles...")
        
        results = []
        for i in range(num_cycles):
            cycle = self.run_bootstrap_cycle(
                mcts_iterations=mcts_iterations,
                evolution_generations=evolution_generations,
                cycle_id=i
            )
            results.append(cycle)
            
            # Adaptive parameters based on performance
            if len(self.performance_history) >= 2:
                recent_improvement = (self.performance_history[-1]['best_fitness'] - 
                                    self.performance_history[-2]['best_fitness'])
                if recent_improvement < 0.05:  # Diminishing returns
                    mcts_iterations = min(mcts_iterations + 20, 200)
                    print(f"  Increasing MCTS iterations to {mcts_iterations}")
        
        return results
    
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
                        
                        # Limit growth per cycle
                        if len(selected) >= 3:
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
                if len(candidate_tokens & existing_tokens) / len(candidate_tokens | existing_tokens) > 0.8:
                    return True
        
        return False
    
    def _track_function_lineage(self, function: DSLFunction, cycle_id: int):
        """Track the lineage of evolved functions"""
        self.function_lineage[function.name] = {
            "cycle_created": cycle_id,
            "fitness_score": function.fitness_score,
            "parent_functions": getattr(function, 'parent_functions', []),
            "usage_count": 0,
            "success_rate": 0.0
        }
    
    def _compute_cycle_metrics(self, mcts_results: List[ProgramState], 
                             evolved_functions: List[DSLFunction], 
                             cycle_time: float) -> Dict[str, float]:
        """Compute performance metrics for a cycle"""
        metrics = {}
        
        # MCTS metrics
        if mcts_results:
            # This would need actual fitness evaluation, simulating for now
            mcts_fitnesses = [0.5 + (i * 0.1) for i in range(len(mcts_results))]
            metrics['mcts_best_fitness'] = max(mcts_fitnesses) if mcts_fitnesses else 0.0
            metrics['mcts_avg_fitness'] = sum(mcts_fitnesses) / len(mcts_fitnesses) if mcts_fitnesses else 0.0
            metrics['mcts_program_count'] = len(mcts_results)
        
        # Evolution metrics
        if evolved_functions:
            evolution_fitnesses = [f.fitness_score for f in evolved_functions]
            metrics['evolution_best_fitness'] = max(evolution_fitnesses)
            metrics['evolution_avg_fitness'] = sum(evolution_fitnesses) / len(evolution_fitnesses)
            metrics['evolution_function_count'] = len(evolved_functions)
        
        # Overall metrics
        all_fitnesses = []
        if mcts_results:
            all_fitnesses.extend([0.5] * len(mcts_results))  # Placeholder
        if evolved_functions:
            all_fitnesses.extend([f.fitness_score for f in evolved_functions])
        
        metrics['best_fitness'] = max(all_fitnesses) if all_fitnesses else 0.0
        metrics['avg_fitness'] = sum(all_fitnesses) / len(all_fitnesses) if all_fitnesses else 0.0
        metrics['cycle_time'] = cycle_time
        metrics['dsl_growth_rate'] = len(evolved_functions)
        
        return metrics
    
    def get_dsl_summary(self) -> Dict[str, Any]:
        """Get a summary of the current DSL state"""
        summary = {
            "total_functions": len(self.dsl.functions),
            "primitive_functions": 0,
            "evolved_functions": 0,
            "function_categories": {},
            "top_functions_by_fitness": [],
            "cycles_completed": len(self.cycles)
        }
        
        for func_name, func in self.dsl.functions.items():
            if func_name in self.function_lineage:
                summary["evolved_functions"] += 1
                cycle = self.function_lineage[func_name]["cycle_created"]
                summary["function_categories"][f"cycle_{cycle}"] = summary["function_categories"].get(f"cycle_{cycle}", 0) + 1
            else:
                summary["primitive_functions"] += 1
        
        # Sort functions by fitness
        func_fitness_pairs = [(name, func.fitness_score) for name, func in self.dsl.functions.items()]
        func_fitness_pairs.sort(key=lambda x: x[1], reverse=True)
        summary["top_functions_by_fitness"] = func_fitness_pairs[:10]
        
        return summary
    
    def save_state(self, filename: str):
        """Save the current system state"""
        state = {
            "dsl_functions": {},
            "cycles": [],
            "function_lineage": self.function_lineage,
            "performance_history": self.performance_history
        }
        
        # Serialize DSL functions (without implementations)
        for name, func in self.dsl.functions.items():
            state["dsl_functions"][name] = {
                "name": func.name,
                "params": func.params,
                "param_types": [t.value for t in func.param_types],
                "return_type": func.return_type.value,
                "body": func.body,
                "fitness_score": func.fitness_score,
                "usage_count": func.usage_count
            }
        
        # Serialize cycles
        for cycle in self.cycles:
            cycle_data = {
                "cycle_id": cycle.cycle_id,
                "mcts_iterations": cycle.mcts_iterations,
                "evolution_generations": cycle.evolution_generations,
                "starting_dsl_size": cycle.starting_dsl_size,
                "ending_dsl_size": cycle.ending_dsl_size,
                "performance_metrics": cycle.performance_metrics,
                "timestamp": cycle.timestamp,
                "new_function_names": [f.name for f in cycle.new_functions]
            }
            state["cycles"].append(cycle_data)
        
        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)
        
        print(f"System state saved to {filename}")
    
    def demonstrate_evolution(self):
        """Demonstrate the evolution process with a simple example"""
        print("=== Evolution Demonstration ===")
        
        print("Initial DSL functions:")
        for name in self.dsl.list_functions():
            print(f"  - {name}")
        
        # Run a few cycles
        cycles = self.run_multiple_cycles(num_cycles=3, mcts_iterations=50, evolution_generations=5)
        
        print("\n=== Final Results ===")
        summary = self.get_dsl_summary()
        print(f"Total functions: {summary['total_functions']}")
        print(f"Primitive functions: {summary['primitive_functions']}")
        print(f"Evolved functions: {summary['evolved_functions']}")
        
        print("\nTop functions by fitness:")
        for name, fitness in summary['top_functions_by_fitness'][:5]:
            print(f"  {name}: {fitness:.3f}")
        
        print("\nEvolution trajectory:")
        for i, metrics in enumerate(self.performance_history):
            print(f"  Cycle {i}: best_fitness={metrics['best_fitness']:.3f}, "
                  f"new_functions={metrics.get('dsl_growth_rate', 0)}")
        
        return summary


def main():
    """Main demonstration of the MCTS + Evolution system"""
    
    print("🚀 MCTS + Evolution Coding Agent System")
    print("=====================================")
    
    # Create the bootstrap system
    system = BootstrapSystem()
    
    # Run demonstration
    summary = system.demonstrate_evolution()
    
    # Save results
    system.save_state("bootstrap_results.json")
    
    print("\n✅ Demonstration complete!")
    print("Check 'bootstrap_results.json' for detailed results.")


if __name__ == "__main__":
    main()