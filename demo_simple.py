#!/usr/bin/env python3
"""
Simplified demonstration showing DSL evolution and persistence
Manually creates some evolved functions to show the persistence system working
"""

import os
import time
from dotenv import load_dotenv

load_dotenv()

from dsl import DSL, DSLFunction, DSLType
from persistence import SessionManager, DSLPersistence

def create_sample_evolved_functions():
    """Create some sample evolved functions to demonstrate persistence"""
    
    # Factorial function
    factorial = DSLFunction(
        name="factorial",
        params=["n"],
        param_types=[DSLType.INT],
        return_type=DSLType.INT,
        body="""def factorial(n):
    if eq(n, 0):
        return 1
    else:
        return mul(n, factorial(sub(n, 1)))""",
        fitness_score=0.85
    )
    
    # Power function
    power = DSLFunction(
        name="power",
        params=["base", "exp"],
        param_types=[DSLType.INT, DSLType.INT], 
        return_type=DSLType.INT,
        body="""def power(base, exp):
    if eq(exp, 0):
        return 1
    else:
        return mul(base, power(base, sub(exp, 1)))""",
        fitness_score=0.78
    )
    
    # Max function
    max_func = DSLFunction(
        name="max_two",
        params=["a", "b"],
        param_types=[DSLType.INT, DSLType.INT],
        return_type=DSLType.INT,
        body="""def max_two(a, b):
    return if_then_else(gt(a, b), a, b)""",
        fitness_score=0.72
    )
    
    # Fibonacci helper
    fib_helper = DSLFunction(
        name="fib_helper",
        params=["n"],
        param_types=[DSLType.INT],
        return_type=DSLType.INT,
        body="""def fib_helper(n):
    if lt(n, 2):
        return n
    else:
        return add(fib_helper(sub(n, 1)), fib_helper(sub(n, 2)))""",
        fitness_score=0.69
    )
    
    return [factorial, power, max_func, fib_helper]

def demonstrate_persistence():
    """Demonstrate the persistence system with manual evolution simulation"""
    
    print("🚀 DSL Evolution & Persistence Demonstration")
    print("=" * 50)
    
    # Create session manager
    session = SessionManager("persistence_demo")
    
    print("\n📋 CYCLE 0: Starting with basic DSL")
    print("-" * 30)
    
    # Start fresh
    dsl = DSL()
    show_dsl_state(dsl, "Initial")
    
    # Simulate adding evolved functions over cycles
    evolved_functions = create_sample_evolved_functions()
    
    for cycle, func in enumerate(evolved_functions):
        print(f"\n📋 CYCLE {cycle + 1}: Adding '{func.name}'")
        print("-" * 40)
        
        # Add function to DSL
        dsl.add_function(func)
        
        # Create implementation for demo
        try:
            func.implementation = create_function_implementation(func, dsl)
            print(f"✅ Successfully added {func.name} (fitness: {func.fitness_score:.3f})")
        except Exception as e:
            print(f"⚠️  Added {func.name} but couldn't create implementation: {e}")
        
        # Show current state
        show_dsl_state(dsl, f"After adding {func.name}")
        
        # Save cycle
        cycle_summary = {
            "cycle_id": cycle,
            "new_functions": 1,
            "timestamp": time.time(),
            "best_fitness": func.fitness_score
        }
        session.save_cycle(dsl, cycle, cycle_summary)
        
        print(f"💾 Cycle {cycle + 1} saved to session")
        
        # Test the function if possible
        test_function(func, dsl)
    
    print(f"\n🎉 FINAL RESULTS")
    print("=" * 25)
    
    # Export results
    persistence = DSLPersistence(f"sessions/{session.session_name}")
    python_file = persistence.export_to_python(dsl)
    
    print(f"🐍 Python code exported to: {python_file}")
    print(f"📁 Session data saved in: sessions/{session.session_name}/")
    
    # Show session summary
    summary = session.get_session_summary()
    print(f"\n📊 Session Summary:")
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    # Demonstrate persistence by reloading
    print(f"\n🔄 TESTING PERSISTENCE")
    print("-" * 25)
    
    print("💾 Saving current DSL...")
    persistence.save_dsl(dsl, "final_demo")
    
    print("📂 Loading DSL from disk...")
    loaded_dsl = persistence.load_dsl("final_demo")
    
    print("✅ Persistence test successful!")
    show_dsl_state(loaded_dsl, "Loaded from disk")
    
    return dsl, session

def show_dsl_state(dsl: DSL, stage: str):
    """Show current DSL state"""
    print(f"\n📋 DSL STATE - {stage}")
    print("-" * 30)
    
    primitives = []
    evolved = []
    
    for name, func in dsl.functions.items():
        if hasattr(func, 'implementation') and func.implementation and not func.body:
            primitives.append(name)
        else:
            evolved.append((name, func.fitness_score))
    
    print(f"🔧 Primitives ({len(primitives)}): {', '.join(primitives)}")
    
    if evolved:
        print(f"🧬 Evolved ({len(evolved)}):")
        for name, fitness in sorted(evolved, key=lambda x: x[1], reverse=True):
            print(f"   • {name} (fitness: {fitness:.3f})")
    else:
        print("🧬 Evolved (0): None yet")
    
    print(f"📊 Total functions: {len(dsl.functions)}")

def create_function_implementation(func: DSLFunction, dsl: DSL):
    """Create executable implementation from function body"""
    if not func.body:
        return None
    
    # Create namespace with DSL functions
    namespace = {"__builtins__": {}}
    
    # Add primitive functions
    for name, dsl_func in dsl.functions.items():
        if hasattr(dsl_func, 'implementation') and dsl_func.implementation:
            namespace[name] = dsl_func.implementation
    
    # Execute function definition
    exec(func.body, namespace)
    
    return namespace[func.name]

def test_function(func: DSLFunction, dsl: DSL):
    """Test a function with sample inputs"""
    if not func.implementation:
        print(f"   ⚠️  No implementation for {func.name}")
        return
    
    print(f"   🧪 Testing {func.name}...")
    
    try:
        if func.name == "factorial":
            result = func.implementation(5)
            print(f"      factorial(5) = {result}")
        elif func.name == "power":
            result = func.implementation(2, 3)
            print(f"      power(2, 3) = {result}")
        elif func.name == "max_two":
            result = func.implementation(7, 3)
            print(f"      max_two(7, 3) = {result}")
        elif func.name == "fib_helper":
            result = func.implementation(6)
            print(f"      fib_helper(6) = {result}")
        else:
            print(f"      No test defined for {func.name}")
    except Exception as e:
        print(f"      ❌ Test failed: {e}")

if __name__ == "__main__":
    try:
        dsl, session = demonstrate_persistence()
        print("\n✅ Demonstration completed successfully!")
        print("🔍 Check the generated files to see the evolved DSL in action!")
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()