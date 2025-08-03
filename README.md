# MCTS (Monte Carlo Tree Search) + GPT-4o + Self Evolution for API discovering novel API Composition scenarios

An intelligent API composition system that uses **MCTS (Monte Carlo Tree Search) + GPT-4o + Self Evolution** to automatically discover and build novel API composition scenarios for business intelligence and data analysis tasks.

![Architecture](architecture_diagram.svg)

*Clean 3-phase architecture showing MCTS exploration, Evolution optimization, and Self-Evolution for continuous improvement*

## 🚀 Features

- **GPT-4o Neural Guidance**: Uses GPT-4o as both policy and value network for intelligent API selection
- **MCTS Tree Search**: Systematically explores API composition space with UCB1 selection
- **Evolution Engine**: Optimizes API chains through mutation and selection
- **Real-time Visualization**: Professional React frontend with live MCTS tree and evolution progress
- **25+ API Bank**: Comprehensive set of APIs for data analysis, visualization, and reporting
- **Type Safety**: Automatic type compatibility checking and data flow validation
- **WebSocket Communication**: Real-time updates of composition progress

## 🏗️ Architecture

The system combines three powerful techniques:

1. **GPT-4o Neural Network**: Provides semantic understanding and intelligent guidance
2. **MCTS Tree Search**: Explores API composition space systematically
3. **Evolution Engine**: Optimizes the best candidates through genetic algorithms

### Key Components:

- **Backend**: FastAPI with WebSocket support
- **Frontend**: React with TypeScript, Tailwind CSS, and Framer Motion
- **AI Integration**: GPT-4o for policy and value networks
- **Visualization**: Real-time D3.js tree visualization and evolution progress

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- OpenAI API key
- Git

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd mcts-evolution-coding-agent
```

### 2. Backend Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements_api.txt

# Set up environment variables
cp .env.template .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Frontend Setup
```bash
cd frontend
npm install
cd ..
```

## 🚀 Quick Start

### 1. Start the Backend
```bash
source venv/bin/activate
python api_composition_backend.py
```
The backend will start on `http://localhost:8000`

### 2. Start the Frontend
```bash
cd frontend
npm run dev
```
The frontend will start on `http://localhost:3000`

### 3. Open the Application
Navigate to `http://localhost:3000` in your browser.

## 🎯 Usage

1. **Configure Parameters**: Set MCTS iterations, evolution generations, and business objectives
2. **Start Composition**: Click "Start Composition" to begin the intelligent API chain building
3. **Watch Progress**: Observe real-time MCTS tree construction and evolution progress
4. **View Results**: See the optimized API chain with type compatibility and data flow

### Example Business Goals:
- Business Intelligence Dashboard
- Financial Risk Analysis  
- Market Research Report
- Competitive Analysis
- Investment Insights

## 🔧 Configuration

### MCTS Parameters:
- **Iterations**: Number of MCTS search iterations (5-30)
- **Exploration Constant**: UCB1 exploration parameter (0.5-2.0)
- **Target Task**: Business objective for API composition

### Evolution Parameters:
- **Generations**: Number of evolution generations (5-20)
- **Population Size**: Size of candidate population (10-50)
- **Mutation Rate**: Probability of mutations (0.1-1.0)

### GPT-4o Parameters:
- **Model**: gpt-4o or gpt-4o-mini
- **Temperature**: Creativity level (0.1-1.0)
- **Max Tokens**: Response length limit (100-2000)

## 📊 API Bank

The system includes 25+ APIs across 5 categories:

- **Data Sources**: News search, stock data, weather, company info
- **Analysis**: Sentiment analysis, trend analysis, entity extraction
- **Processing**: Text summarization, data filtering, normalization
- **Visualization**: Charts, heatmaps, timelines, plots
- **Output**: Reports, dashboards, alerts, presentations

## 🔬 How It Works

### 1. MCTS Phase
- **Selection**: Choose nodes using UCB1 + GPT-4o guidance
- **Expansion**: Add new APIs based on GPT-4o suggestions
- **Evaluation**: Score API chains using GPT-4o value network
- **Backpropagation**: Update node statistics

### 2. Evolution Phase
- **Population**: Initialize with best MCTS candidates
- **Mutation**: Modify API chains (add/remove/replace APIs)
- **Selection**: Choose fittest candidates for next generation
- **Optimization**: Converge to optimal API compositions

### 3. Real-time Visualization
- Live MCTS tree construction
- Evolution progress tracking
- API chain flow visualization
- Performance metrics dashboard

## 🍕 Simple Explanation: The Pizza Analogy

Think of building API compositions like **making the perfect pizza**:

### **MCTS = Smart Chef** 🧑‍🍳
- Tries different ingredient combinations systematically
- "Let me try pepperoni... now add mushrooms... now cheese..."
- GPT-4o guides: "Based on customer preferences, try adding basil next"
- Finds 5 good pizza recipes (API chains)

### **Evolution = Recipe Improver** 🧬  
- Takes those 5 good pizzas and creates variations
- Makes small changes: "What if I add more cheese? Less sauce? Different crust?"
- Creates a **population** of 10 pizza variations
- Keeps the tastiest ones, discards the bad ones
- Repeats to make them even better over generations

### **Real Example: Financial Dashboard**

**MCTS Exploration:**
```
Iteration 1: START → get_stock_data("AAPL")
Iteration 5: START → get_stock_data → calculate_risk  
Iteration 10: START → get_stock_data → search_news → analyze_sentiment
Iteration 15: START → get_stock_data → calculate_risk → create_chart → generate_report
```

**Evolution Optimization:**
```
Generation 1: 5 different financial API chains
Best: Stock → Risk → Chart → Report (Score: 0.75)

Generation 3: Evolved variations  
Better: Stock → News → Sentiment → Risk → Prediction → Dashboard (Score: 0.85)

Generation 5: Further optimized
Best: Stock → News → Social → Sentiment → Risk → Timeline → Alert → Dashboard (Score: 0.92)
```

## ♾️ Self-Evolution: Never-Ending Improvement

The system keeps evolving forever by:

### **1. New Ingredients (APIs)**: Automatically discovers and adds new APIs
- **Month 1**: 25 APIs (basic financial)
- **Month 6**: 40 APIs (added social media)  
- **Month 12**: 60 APIs (added crypto, ESG, supply chain)

### **2. Changing Tastes (Goals)**: Adapts to new business needs
- **January**: "Create fastest dashboard"
- **June**: "Optimize for accuracy" 
- **December**: "Minimize costs"

### **3. New Customers (Domains)**: Expands to new business areas
- **Start**: Financial analysis
- **Later**: Healthcare, retail, manufacturing
- **Future**: Space exploration, quantum computing

### **The Never-Ending Cycle:**
1. **Evolve** current chains (make them better) ✅
2. **Add** new APIs when available (more ingredients) ✅  
3. **Change** goals when needs shift (new preferences) ✅
4. **Expand** to new domains (new customers) ✅
5. **Repeat** forever 🔄

### **Population Evolution Example:**

**Generation 1:** 5 API chains from MCTS
```
Chain A: News → Sentiment → Report
Chain B: Stock → Risk → Chart  
Chain C: Weather → Analysis → Dashboard
Chain D: Company → Patents → Summary
Chain E: Social → Trends → Visualization
```

**Evolution creates variations:**
```
Chain A1: News → Sentiment → Summary → Report (added step)
Chain A2: News → Sentiment (removed report)
Chain B1: Stock → Risk → Chart → Dashboard (added dashboard)
Chain B2: Stock → News → Risk → Chart (added news)
```

**Generation 2:** Keep best 5, create 5 more variations  
**Generation 3:** Keep best 5, create 5 more variations  
...and the cycle continues infinitely!

### **Real-World Adaptation Example:**

**Week 1:** System creates financial dashboards
- Population: 10 different financial API chains
- Best: `Stock → Risk → Chart → Report`

**Week 10:** Market crashes, need faster alerts  
- Goal changes to "speed over accuracy"
- Population evolves: `Stock → Quick-Risk → Alert`

**Week 20:** New crypto APIs become available
- System adds Bitcoin, Ethereum APIs
- Population evolves: `Stock → Crypto → Combined-Risk → Alert`

**Week 30:** Users want social sentiment
- System adds Twitter, Reddit APIs  
- Population evolves: `Stock → Crypto → Social → Sentiment → Risk → Alert`

This creates a system that **never stops discovering** novel API composition scenarios!



## 🛡️ Type Safety

The system ensures type compatibility through:
- **Type Compatibility Graph**: Maps valid type conversions
- **Automatic Validation**: Checks input/output type matching
- **Data Flow Analysis**: Ensures valid API chaining

## 🌐 WebSocket API

Real-time communication endpoints:
- `ws://localhost:8000/ws/{session_id}` - WebSocket connection
- Message types: `mcts_update`, `evolution_generation`, `system_status`

## 📁 Project Structure

```
├── api_composition_backend.py    # Main FastAPI backend
├── frontend/                     # React frontend
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── hooks/               # Custom hooks
│   │   ├── store/               # Zustand state management
│   │   └── types/               # TypeScript definitions
├── architecture_diagram.svg     # System architecture
├── requirements_api.txt         # Python dependencies
└── README.md                    # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4o API
- FastAPI for the excellent web framework
- React and the amazing frontend ecosystem
- D3.js for powerful visualizations

## 📞 Support

For questions and support, please open an issue on GitHub.

---

**Built with ❤️ using GPT-4o, MCTS, and Evolution**