# 🧬 EvolDSL: Self-Bootstrapping Programming with MCTS + Evolution

A **self-bootstrapping coding agent** that combines Monte Carlo Tree Search (MCTS) and Evolutionary Programming, guided by GPT-4o, to automatically discover and evolve Domain Specific Languages (DSLs).

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI GPT-4o](https://img.shields.io/badge/OpenAI-GPT--4o-green.svg)](https://openai.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Quick Start

### Prerequisites

```bash
# Clone the repository
git clone https://github.com/allthingssecurity/evoldsl.git
cd evoldsl

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.template .env
# Edit .env and add your OpenAI API key
```

### Run Evolution Demo

```bash
# Simple demonstration showing persistence
python demo_simple.py

# Full GPT-4o integration (requires API key)
python run_evolution_demo.py

# Test evolved functions
python test_evolved_functions.py
```

## 🧠 How It Works

The system works in **bootstrap cycles**:

1. **🔍 MCTS Phase**: Uses GPT-4o as policy/value networks to search the space of possible programs
2. **🧬 Evolution Phase**: Uses GPT-4o to guide mutations of successful programs  
3. **🔗 Integration Phase**: Adds the best evolved functions back to the DSL as new primitives
4. **♻️ Bootstrap**: Repeats with expanded DSL, enabling more complex program synthesis

### Architecture

```
DSL (Domain Specific Language)
├── Basic Primitives (add, mul, if_then_else, etc.)
└── Evolved Functions (discovered by MCTS + Evolution)

MCTS Program Synthesis
├── GPT-4o Policy Model (suggests next programming actions)
├── GPT-4o Value Model (evaluates program quality)
└── Tree Search (explores program construction space)

Evolution Engine  
├── GPT-4o Evolution Guide (suggests mutations)
├── Population Management (selection, survival)
└── Function Integration (adds successful functions to DSL)
```

## 🌳 Example: DSL Evolution in Action

### Starting State (Cycle 0)
```python
# 9 primitive functions
add, sub, mul, div, eq, lt, gt, if_then_else, identity
```

### After Evolution (Cycle 5)
```python
# 14 total functions - 5 evolved functions discovered!

# Level 1: Basic evolved functions
def factorial(n):
    if eq(n, 0):
        return 1
    else:
        return mul(n, factorial(sub(n, 1)))
# fitness: 0.850

def power(base, exp):
    if eq(exp, 0):
        return 1
    else:
        return mul(base, power(base, sub(exp, 1)))
# fitness: 0.780

def max_two(a, b):
    return if_then_else(gt(a, b), a, b)
# fitness: 0.720

def fib_helper(n):
    if lt(n, 2):
        return n
    else:
        return add(fib_helper(sub(n, 1)), fib_helper(sub(n, 2)))
# fitness: 0.690

# Level 2: Composed function using Level 1 functions!
def advanced_combo(n):
    fact_n = factorial(n)          # Uses evolved function
    power_n = power(n, 2)          # Uses evolved function  
    return max_two(fact_n, power_n) # Uses evolved function
# fitness: 0.920 ← Highest fitness!
```

### Verified Results
```bash
✅ factorial(5) = 120
✅ power(2, 3) = 8
✅ max_two(7, 3) = 7
✅ fib_helper(6) = 8
✅ advanced_combo(4) = 24  # max(factorial(4), power(4,2)) = max(24, 16) = 24
```

## 💾 Persistent Evolution

The system automatically saves and resumes evolution state:

```bash
sessions/my_evolution/
├── latest.json              # Current DSL state
├── dsl_cycle_0.json        # Backup after cycle 0
├── dsl_cycle_1.json        # Backup after cycle 1
├── session_log.json        # Evolution timeline
└── evolved_functions.py    # Standalone Python code
```

**Cross-session evolution**: Stop and resume anytime - the DSL continues evolving from where you left off!

## 🎯 Key Features

### 🧠 **AI-Guided Discovery**
- **GPT-4o Policy**: Suggests promising programming moves
- **GPT-4o Value**: Evaluates code quality holistically  
- **GPT-4o Evolution**: Proposes meaningful mutations

### 🔄 **Self-Bootstrapping**
- **Incremental Complexity**: Each cycle builds on previous discoveries
- **Emergent Functionality**: Complex behaviors emerge from simple primitives
- **Compositionality**: Higher-level functions naturally compose lower-level ones

### 🎮 **Efficient Search**
- **MCTS**: Focuses exploration on promising program paths
- **Fitness-Driven**: Only high-quality functions survive evolution
- **Type-Safe**: Maintains type safety across evolution cycles

### 💾 **Production Ready**
- **Persistent State**: Evolution survives system restarts
- **Standalone Export**: Generate immediately usable Python code
- **Session Management**: Track multiple evolution experiments
- **Cost Control**: Configurable LLM usage for budget management

## 📁 Project Structure

```
evoldsl/
├── dsl.py                 # Domain Specific Language core
├── mcts.py                # MCTS program synthesis engine
├── evolution.py           # Evolution engine for function discovery
├── llm_integration.py     # GPT-4o policy/value/mutation models
├── mcts_gpt4o.py         # Main GPT-4o integrated system
├── persistence.py         # Save/load DSL state across sessions
├── main_system.py        # Original mock system (for comparison)
├── demo_simple.py        # Simple evolution demonstration
├── run_evolution_demo.py # Full GPT-4o demonstration
├── test_evolved_functions.py # Test evolved functions
├── requirements.txt      # Python dependencies
├── .env.template         # Environment variables template
└── README.md            # This file
```

## ⚙️ Configuration

### LLM Settings
```python
from llm_integration import LLMConfig

config = LLMConfig(
    model="gpt-4o-mini",      # Use mini for cost efficiency
    temperature=0.7,          # Creativity vs consistency
    max_tokens=300,           # Response length limit
    rate_limit_delay=0.3,     # Delay between API calls
    max_retries=2             # Retry failed requests
)
```

### Evolution Parameters
```python
await system.run_bootstrap_cycle_async(
    target_tasks=["factorial", "fibonacci"],  # Tasks to solve
    mcts_iterations=20,                      # MCTS search depth  
    evolution_generations=5,                 # Evolution cycles
    cycle_id=0                              # Cycle identifier
)
```

## 💰 Cost Estimation

Approximate OpenAI API costs per cycle with `gpt-4o-mini`:
- **MCTS Phase**: ~$0.05-0.20 per cycle
- **Evolution Phase**: ~$0.02-0.10 per cycle
- **Total per cycle**: ~$0.07-0.30

**5-cycle evolution run**: ~$0.35-1.50

Costs scale with:
- Number of iterations/generations
- Task complexity
- Model choice (gpt-4o vs gpt-4o-mini)

## 🔬 Research Applications

This system demonstrates key concepts in:

- **🤖 Neural-Guided Search**: Using LLMs as heuristics for combinatorial spaces
- **🔄 Self-Improving Systems**: Programs that enhance their own capabilities  
- **🧩 Compositional Learning**: Building complexity from simple primitives
- **📚 Meta-Learning**: Learning to learn better programming strategies
- **💾 Persistent AI**: AI systems that remember and build on past discoveries

## 🚀 Advanced Usage

### Custom Evolution Session
```python
from mcts_gpt4o import GPT4BootstrapSystem
from persistence import SessionManager

# Create persistent session
session = SessionManager("my_custom_evolution")
dsl = session.start_session(resume=True)

# Run custom evolution
system = GPT4BootstrapSystem(initial_dsl=dsl)
summary = await system.run_bootstrap_cycle_async(
    target_tasks=["sorting", "searching", "optimization"],
    mcts_iterations=50,
    evolution_generations=10
)

# Save results
session.save_cycle(dsl, 0, summary)
```

### Export Evolved Functions
```python
from persistence import DSLPersistence

persistence = DSLPersistence("my_session")
python_file = persistence.export_to_python(dsl, "my_evolved_functions.py")
print(f"Evolved functions exported to: {python_file}")
```

## 🛠️ Development

### Running Tests
```bash
# Test persistence system
python test_resume.py

# Test evolved functions work correctly  
python test_evolved_functions.py

# Run evolution with debugging
python demo_simple.py
```

### Adding New Primitives
```python
from dsl import DSLFunction, DSLType

# Add new primitive to DSL
new_primitive = DSLFunction(
    name="mod",
    params=["x", "y"], 
    param_types=[DSLType.INT, DSLType.INT],
    return_type=DSLType.INT,
    implementation=lambda x, y: x % y if y != 0 else 0
)

dsl.add_function(new_primitive)
```

## 🤝 Contributing

Contributions welcome! Areas of interest:

- **🔬 Novel mutation strategies** for evolution
- **📊 Better program evaluation metrics**
- **💰 Cost optimization techniques** 
- **🎯 Domain-specific applications**
- **🔧 Performance improvements**
- **📚 Documentation and examples**

### Development Setup
```bash
git clone https://github.com/allthingssecurity/evoldsl.git
cd evoldsl
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
# Add your OpenAI API key to .env
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT-4o API
- **Monte Carlo Tree Search** research community
- **Evolutionary Programming** research community  
- **Program Synthesis** research community

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/allthingssecurity/evoldsl/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/allthingssecurity/evoldsl/discussions)
- 📧 **Contact**: Open an issue for questions

---

**🧠 EvolDSL: Where AI learns to program by programming itself! ⚡**

*Built with ❤️ for the future of autonomous programming*