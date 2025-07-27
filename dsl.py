from typing import Any, Dict, List, Union, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import ast

class DSLType(Enum):
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    BOOL = "bool"
    LIST = "list"
    FUNCTION = "function"
    ANY = "any"

@dataclass
class DSLFunction:
    name: str
    params: List[str]
    param_types: List[DSLType]
    return_type: DSLType
    body: Optional[str] = None
    implementation: Optional[Callable] = None
    fitness_score: float = 0.0
    usage_count: int = 0
    
    def __call__(self, *args):
        if self.implementation:
            return self.implementation(*args)
        else:
            raise NotImplementedError(f"Function {self.name} not implemented")

class DSL:
    def __init__(self):
        self.functions: Dict[str, DSLFunction] = {}
        self.types = DSLType
        self._init_primitives()
    
    def _init_primitives(self):
        """Initialize basic DSL primitives"""
        primitives = [
            DSLFunction("add", ["x", "y"], [DSLType.INT, DSLType.INT], DSLType.INT, 
                       implementation=lambda x, y: x + y),
            DSLFunction("sub", ["x", "y"], [DSLType.INT, DSLType.INT], DSLType.INT,
                       implementation=lambda x, y: x - y),
            DSLFunction("mul", ["x", "y"], [DSLType.INT, DSLType.INT], DSLType.INT,
                       implementation=lambda x, y: x * y),
            DSLFunction("div", ["x", "y"], [DSLType.INT, DSLType.INT], DSLType.INT,
                       implementation=lambda x, y: x // y if y != 0 else 0),
            DSLFunction("eq", ["x", "y"], [DSLType.ANY, DSLType.ANY], DSLType.BOOL,
                       implementation=lambda x, y: x == y),
            DSLFunction("lt", ["x", "y"], [DSLType.INT, DSLType.INT], DSLType.BOOL,
                       implementation=lambda x, y: x < y),
            DSLFunction("gt", ["x", "y"], [DSLType.INT, DSLType.INT], DSLType.BOOL,
                       implementation=lambda x, y: x > y),
            DSLFunction("if_then_else", ["cond", "then_val", "else_val"], 
                       [DSLType.BOOL, DSLType.ANY, DSLType.ANY], DSLType.ANY,
                       implementation=lambda c, t, e: t if c else e),
            DSLFunction("identity", ["x"], [DSLType.ANY], DSLType.ANY,
                       implementation=lambda x: x),
        ]
        
        for func in primitives:
            self.functions[func.name] = func
    
    def add_function(self, function: DSLFunction):
        """Add a new function to the DSL"""
        self.functions[function.name] = function
    
    def get_function(self, name: str) -> Optional[DSLFunction]:
        """Get a function by name"""
        return self.functions.get(name)
    
    def list_functions(self) -> List[str]:
        """List all available function names"""
        return list(self.functions.keys())
    
    def evaluate_expression(self, expr: str, context: Dict[str, Any] = None) -> Any:
        """Evaluate a simple expression using DSL functions"""
        if context is None:
            context = {}
        
        # Add DSL functions to context
        context.update({name: func for name, func in self.functions.items()})
        
        try:
            # Parse and evaluate the expression
            tree = ast.parse(expr, mode='eval')
            return eval(compile(tree, '<string>', 'eval'), {"__builtins__": {}}, context)
        except Exception as e:
            return f"Error: {e}"
    
    def can_compose(self, func1: str, func2: str) -> bool:
        """Check if two functions can be composed (output type matches input type)"""
        f1 = self.get_function(func1)
        f2 = self.get_function(func2)
        
        if not f1 or not f2:
            return False
            
        # Simple type compatibility check
        return (f1.return_type == f2.param_types[0] if f2.param_types 
                else f1.return_type == DSLType.ANY or f2.param_types[0] == DSLType.ANY)