#!/usr/bin/env python3
"""
Test resuming from saved DSL state to show persistent evolution
"""

from persistence import SessionManager, DSLPersistence
from dsl import DSLFunction, DSLType

def test_resume_functionality():
    """Test that we can resume evolution from saved state"""
    
    print("🔄 Testing DSL Resume Functionality")
    print("=" * 40)
    
    # Try to resume from the previous session
    print("📂 Loading previous session 'persistence_demo'...")
    session = SessionManager("persistence_demo")
    dsl = session.start_session(resume=True)
    
    print(f"✅ Successfully loaded DSL with {len(dsl.functions)} functions")
    
    # Show loaded state
    print(f"\n📋 LOADED DSL STATE")
    print("-" * 20)
    
    primitives = []
    evolved = []
    
    for name, func in dsl.functions.items():
        if hasattr(func, 'implementation') and func.implementation and not func.body:
            primitives.append(name)
        else:
            evolved.append((name, func.fitness_score))
    
    print(f"🔧 Primitives ({len(primitives)}): {', '.join(primitives)}")
    print(f"🧬 Evolved functions ({len(evolved)}):")
    for name, fitness in sorted(evolved, key=lambda x: x[1], reverse=True):
        print(f"   • {name} (fitness: {fitness:.3f})")
    
    # Test that we can add a new function
    print(f"\n🆕 ADDING NEW FUNCTION")
    print("-" * 25)
    
    # Create a new evolved function that uses existing ones
    advanced_func = DSLFunction(
        name="advanced_combo",
        params=["n"],
        param_types=[DSLType.INT],
        return_type=DSLType.INT,
        body="""def advanced_combo(n):
    fact_n = factorial(n)
    power_n = power(n, 2)
    return max_two(fact_n, power_n)""",
        fitness_score=0.92
    )
    
    # Add to DSL
    dsl.add_function(advanced_func)
    print(f"✅ Added '{advanced_func.name}' (fitness: {advanced_func.fitness_score:.3f})")
    
    # Save the updated state
    cycle_summary = {
        "cycle_id": 4,
        "new_functions": 1,
        "timestamp": 1753613800.0,
        "best_fitness": advanced_func.fitness_score
    }
    session.save_cycle(dsl, 4, cycle_summary)
    print(f"💾 Saved updated DSL state")
    
    # Show final state
    print(f"\n📊 FINAL STATE")
    print("-" * 15)
    print(f"Total functions: {len(dsl.functions)}")
    print(f"Best fitness: {max(func.fitness_score for func in dsl.functions.values()):.3f}")
    
    # Export the enhanced DSL
    persistence = DSLPersistence(f"sessions/{session.session_name}")
    python_file = persistence.export_to_python(dsl, "enhanced_evolved_functions.py")
    print(f"🐍 Enhanced DSL exported to: {python_file}")
    
    return dsl

def show_evolution_timeline():
    """Show the complete evolution timeline from session logs"""
    
    print(f"\n📈 EVOLUTION TIMELINE")
    print("=" * 30)
    
    session = SessionManager("persistence_demo")
    summary = session.get_session_summary()
    
    print(f"Session: {summary['session_name']}")
    print(f"Cycles completed: {summary['cycles_completed']}")
    print(f"Functions discovered: {summary['functions_discovered']}")
    print(f"Best fitness achieved: {summary['best_fitness_achieved']:.3f}")
    
    # Show cycle-by-cycle progress
    if hasattr(session, 'session_log') and session.session_log:
        print(f"\n📊 Cycle-by-cycle progress:")
        for log_entry in session.session_log:
            cycle_id = log_entry['cycle_id']
            functions_added = log_entry['functions_added']
            total_functions = log_entry['total_functions']
            best_fitness = log_entry['best_fitness']
            print(f"   Cycle {cycle_id + 1}: +{functions_added} functions → {total_functions} total (best: {best_fitness:.3f})")

if __name__ == "__main__":
    try:
        # Test resume functionality
        dsl = test_resume_functionality()
        
        # Show evolution timeline
        show_evolution_timeline()
        
        print(f"\n✅ Resume test completed successfully!")
        print(f"🎯 The DSL now persists across sessions and can continue evolving!")
        
    except Exception as e:
        print(f"\n❌ Resume test failed: {e}")
        import traceback
        traceback.print_exc()