#!/usr/bin/env python3
"""
Test the evolved functions to verify they work correctly
"""

# Import the evolved functions
exec(open('enhanced_evolved_functions.py').read())

def test_evolved_functions():
    """Test all evolved functions with sample inputs"""
    
    print("🧪 Testing Evolved DSL Functions")
    print("=" * 35)
    
    tests = [
        ("factorial", lambda: factorial(5), "factorial(5)", "120"),
        ("power", lambda: power(2, 3), "power(2, 3)", "8"),
        ("max_two", lambda: max_two(7, 3), "max_two(7, 3)", "7"),
        ("fib_helper", lambda: fib_helper(6), "fib_helper(6)", "8"),
        ("advanced_combo", lambda: advanced_combo(4), "advanced_combo(4)", "max(24, 16) = 24"),
    ]
    
    all_passed = True
    
    for func_name, test_func, call_desc, expected in tests:
        try:
            result = test_func()
            print(f"✅ {call_desc} = {result} (expected: {expected})")
            
            # Verify some specific results
            if func_name == "factorial" and result != 120:
                print(f"   ⚠️  Expected 120, got {result}")
                all_passed = False
            elif func_name == "power" and result != 8:
                print(f"   ⚠️  Expected 8, got {result}")
                all_passed = False
            elif func_name == "max_two" and result != 7:
                print(f"   ⚠️  Expected 7, got {result}")
                all_passed = False
            elif func_name == "fib_helper" and result != 8:
                print(f"   ⚠️  Expected 8, got {result}")
                all_passed = False
            elif func_name == "advanced_combo" and result != 24:
                print(f"   ⚠️  Expected 24, got {result}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ {call_desc} FAILED: {e}")
            all_passed = False
    
    print(f"\n{'='*35}")
    if all_passed:
        print("🎉 All tests passed! The evolved DSL functions work correctly!")
    else:
        print("⚠️  Some tests failed. Check the implementations.")
    
    # Show the evolution hierarchy
    print(f"\n🌳 Function Evolution Hierarchy:")
    print(f"   🔧 Primitives: add, sub, mul, div, eq, lt, gt, if_then_else")
    print(f"   ↓")
    print(f"   🧬 Level 1: factorial, power, max_two, fib_helper")
    print(f"   ↓") 
    print(f"   🚀 Level 2: advanced_combo (uses factorial, power, max_two)")
    
    return all_passed

if __name__ == "__main__":
    test_evolved_functions()