#!/usr/bin/env python3
"""
Comprehensive demonstration of MCTS + Evolution system with persistence
Shows DSL evolution over multiple cycles with GPT-4o integration
"""

import asyncio
import os
import time
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

from dsl import DSL
from mcts_gpt4o import GPT4BootstrapSystem
from llm_integration import LLMConfig
from persistence import SessionManager, DSLPersistence

class EvolutionDemo:
    """Comprehensive demo showing DSL evolution"""
    
    def __init__(self, session_name: str = "evolution_demo"):
        self.session_name = session_name
        self.session = SessionManager(session_name)
        
        # Configure LLM for demo (smaller parameters for cost control)
        self.llm_config = LLMConfig(
            model="gpt-4o-mini",  # Cheaper variant for demo
            temperature=0.7,
            max_tokens=300,
            rate_limit_delay=0.3,
            max_retries=2
        )
        
        print(f"🚀 Starting Evolution Demo: Session '{session_name}'")
        print(f"💰 Using {self.llm_config.model} for cost efficiency")
    
    async def run_complete_demo(self, num_cycles: int = 3, resume: bool = True):
        """Run complete evolution demonstration"""
        
        print("\n" + "="*60)
        print("🧬 MCTS + EVOLUTION DSL DEMONSTRATION")
        print("="*60)
        
        # Initialize or resume session
        dsl = self.session.start_session(resume=resume)
        self._show_dsl_state(dsl, "INITIAL")
        
        # Create bootstrap system
        system = GPT4BootstrapSystem(initial_dsl=dsl, llm_config=self.llm_config)
        
        # Track evolution metrics
        evolution_metrics = []
        
        print(f"\n🔄 Running {num_cycles} evolution cycles...")
        
        for cycle in range(num_cycles):
            print(f"\n{'='*40}")
            print(f"🔬 CYCLE {cycle + 1}/{num_cycles}")
            print(f"{'='*40}")
            
            cycle_start = time.time()
            
            try:
                # Define progressive tasks for each cycle
                target_tasks = self._get_cycle_tasks(cycle)
                
                # Run bootstrap cycle
                summary = await system.run_bootstrap_cycle_async(
                    target_tasks=target_tasks,
                    mcts_iterations=15,  # Small for demo
                    evolution_generations=3,  # Small for demo
                    cycle_id=cycle
                )
                
                cycle_time = time.time() - cycle_start
                summary['cycle_time'] = cycle_time
                
                # Save cycle results
                self.session.save_cycle(dsl, cycle, summary)
                
                # Track metrics
                evolution_metrics.append(summary)
                
                # Show progress
                self._show_cycle_results(cycle, summary, dsl)
                
                # Export current state
                if cycle == num_cycles - 1:  # Last cycle
                    self._export_final_results(dsl)
                
            except Exception as e:
                print(f"❌ Error in cycle {cycle}: {e}")
                print("Continuing with next cycle...")
                continue
        
        # Show final summary
        await self._show_final_summary(evolution_metrics, dsl)
        
        print("\n✅ Evolution demonstration complete!")
        return evolution_metrics
    
    def _get_cycle_tasks(self, cycle: int) -> list:
        """Get progressive tasks for each cycle"""
        task_progression = [
            ["factorial", "power"],           # Cycle 0: Basic math
            ["fibonacci", "sum_range"],       # Cycle 1: Sequences
            ["max_value", "sort_pair"]        # Cycle 2: Comparisons
        ]
        
        if cycle < len(task_progression):
            return task_progression[cycle]
        else:
            return ["advanced_function", "optimization"]
    
    def _show_dsl_state(self, dsl: DSL, stage: str):
        """Display current DSL state"""
        print(f"\n📋 DSL STATE - {stage}")
        print("-" * 30)
        
        primitives = []
        evolved = []
        
        for name, func in dsl.functions.items():
            if func.body is None:  # Primitive function
                primitives.append(name)
            else:  # Evolved function
                evolved.append((name, func.fitness_score))
        
        print(f"🔧 Primitives ({len(primitives)}): {', '.join(primitives)}")
        
        if evolved:
            print(f"🧬 Evolved ({len(evolved)}):")
            for name, fitness in sorted(evolved, key=lambda x: x[1], reverse=True):
                print(f"   • {name} (fitness: {fitness:.3f})")
        else:
            print("🧬 Evolved (0): None yet")
        
        print(f"📊 Total functions: {len(dsl.functions)}")
    
    def _show_cycle_results(self, cycle: int, summary: Dict[str, Any], dsl: DSL):
        """Display results from a cycle"""
        print(f"\n📈 CYCLE {cycle + 1} RESULTS")
        print("-" * 25)
        print(f"⏱️  Time: {summary.get('cycle_time', 0):.1f}s")
        print(f"🔧 Functions added: {summary.get('new_functions', 0)}")
        print(f"📊 DSL size: {summary.get('start_dsl_size', 0)} → {summary.get('end_dsl_size', 0)}")
        print(f"🎯 MCTS programs: {summary.get('mcts_programs', 0)}")
        print(f"🧬 Evolved candidates: {summary.get('evolved_functions', 0)}")
        
        llm_stats = summary.get('llm_stats', {})
        if llm_stats:
            print(f"🤖 LLM calls: {llm_stats.get('total_calls', 0)}")
            print(f"💰 Est. cost: ${llm_stats.get('total_calls', 0) * 0.002:.3f}")
        
        # Show new functions added this cycle
        if summary.get('new_functions', 0) > 0:
            print("\n🆕 New functions discovered:")
            current_evolved = [(name, func.fitness_score) for name, func in dsl.functions.items() 
                             if func.body is not None]
            recent_functions = sorted(current_evolved, key=lambda x: x[1], reverse=True)[:summary.get('new_functions', 0)]
            
            for name, fitness in recent_functions:
                print(f"   ✨ {name} (fitness: {fitness:.3f})")
                if name in dsl.functions and dsl.functions[name].body:
                    # Show a snippet of the code
                    code_lines = dsl.functions[name].body.split('\n')
                    if len(code_lines) > 1:
                        print(f"      {code_lines[1].strip()}")  # Show function signature line
    
    def _export_final_results(self, dsl: DSL):
        """Export final results for inspection"""
        print(f"\n💾 EXPORTING FINAL RESULTS")
        print("-" * 30)
        
        persistence = DSLPersistence(f"sessions/{self.session_name}")
        
        # Export as Python code
        python_file = persistence.export_to_python(dsl)
        print(f"🐍 Python code: {python_file}")
        
        # Show file contents preview
        try:
            with open(python_file, 'r') as f:
                lines = f.readlines()
                if len(lines) > 20:
                    print("📄 Preview (first 20 lines):")
                    for i, line in enumerate(lines[:20]):
                        print(f"   {i+1:2d}: {line.rstrip()}")
                    print(f"   ... ({len(lines)-20} more lines)")
        except Exception as e:
            print(f"❌ Could not preview file: {e}")
    
    async def _show_final_summary(self, metrics: list, dsl: DSL):
        """Show final evolution summary"""
        print(f"\n🎉 EVOLUTION SUMMARY")
        print("=" * 40)
        
        if not metrics:
            print("❌ No successful cycles completed")
            return
        
        # Overall statistics
        total_functions_added = sum(m.get('new_functions', 0) for m in metrics)
        total_time = sum(m.get('cycle_time', 0) for m in metrics)
        total_llm_calls = sum(m.get('llm_stats', {}).get('total_calls', 0) for m in metrics)
        estimated_cost = total_llm_calls * 0.002  # Rough estimate
        
        print(f"🔄 Cycles completed: {len(metrics)}")
        print(f"⏱️  Total time: {total_time:.1f}s")
        print(f"🧬 Functions discovered: {total_functions_added}")
        print(f"📊 Final DSL size: {len(dsl.functions)}")
        print(f"🤖 Total LLM calls: {total_llm_calls}")
        print(f"💰 Estimated cost: ${estimated_cost:.3f}")
        
        # Evolution trajectory
        print(f"\n📈 EVOLUTION TRAJECTORY")
        print("-" * 25)
        for i, metric in enumerate(metrics):
            functions_added = metric.get('new_functions', 0)
            dsl_size = metric.get('end_dsl_size', 0)
            cycle_time = metric.get('cycle_time', 0)
            print(f"Cycle {i+1}: +{functions_added} functions → {dsl_size} total ({cycle_time:.1f}s)")
        
        # Show session summary
        session_summary = self.session.get_session_summary()
        print(f"\n📋 SESSION SUMMARY")
        print("-" * 20)
        for key, value in session_summary.items():
            print(f"{key}: {value}")
        
        # Final DSL state
        self._show_dsl_state(dsl, "FINAL")

async def main():
    """Main demonstration entry point"""
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment")
        print("Please set your OpenAI API key and try again")
        return
    
    print("🔑 OpenAI API key found")
    
    # Create and run demo
    demo = EvolutionDemo("comprehensive_demo")
    
    try:
        # Run the evolution demo
        await demo.run_complete_demo(
            num_cycles=3,  # Start with 3 cycles
            resume=False   # Start fresh for demo
        )
        
        print("\n🎯 Demo completed successfully!")
        print(f"📁 Results saved in sessions/{demo.session_name}/")
        print("🔍 Check the generated files to see your evolved DSL!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("This might be due to API limits, network issues, or other factors")

if __name__ == "__main__":
    print("🚀 MCTS + Evolution DSL Demo Starting...")
    asyncio.run(main())