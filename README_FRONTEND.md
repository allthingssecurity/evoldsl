# 🎨 EvolDSL Professional Frontend

A beautiful, interactive frontend for visualizing MCTS + Evolution programming in real-time.

## ✨ Features

### 🌳 **MCTS Tree Visualization**
- **Interactive tree display** showing node selection and program construction
- **Real-time updates** as GPT-4o drives the search
- **Node details panel** with UCB scores, visit counts, and program states
- **Animated tree growth** with smooth transitions
- **Click to explore** - select nodes to see detailed information

### 🧬 **Evolution Display**
- **Population visualization** with fitness vs complexity scatter plots
- **Generation tracking** showing fitness evolution over time
- **Mutation strategy breakdown** with color-coded strategies
- **Candidate details** with function code and lineage
- **Real-time population updates** during evolution

### 📚 **Program Bank**
- **Searchable library** of subprograms and evolved functions
- **Composition mode** for combining programs
- **Filtering and sorting** by fitness, usage, complexity
- **Code preview** and detailed metrics
- **Tag-based organization** for easy discovery

### 🎛️ **Professional Control Panel**
- **GPT-4o integration** with API key management
- **MCTS configuration** (iterations, exploration, target tasks)
- **Evolution parameters** (generations, population, mutation rate)
- **Cost estimation** with real-time tracking
- **Session management** for saving/loading progress

### ⚡ **Real-time Updates**
- **WebSocket connection** for live data streaming
- **Progress tracking** with phase indicators
- **Error handling** with user-friendly messages
- **Connection status** with automatic reconnection

## 🚀 Quick Start

### 1. Install Dependencies

First, make sure you have Python 3.8+ and Node.js 16+ installed.

```bash
# Install Python backend dependencies
pip install -r requirements_api.txt

# Install frontend dependencies (automatically handled by startup script)
cd frontend && npm install
```

### 2. Start EvolDSL

```bash
# One-command startup (recommended)
python start_evoldsl.py
```

This will:
- ✅ Check all dependencies
- 🚀 Start the backend API server (port 8000)
- 🎨 Start the frontend dev server (port 3000)
- 🌐 Open your browser to http://localhost:3000

### 3. Configure & Run

1. **Enter your GPT-4o API key** in the control panel
2. **Configure MCTS parameters** (iterations, exploration constant, target task)
3. **Set evolution parameters** (generations, population size, mutation rate)
4. **Click "Start Evolution"** and watch the magic happen!

## 🛠️ Manual Setup (Alternative)

If you prefer to run components separately:

### Backend API
```bash
# Start the backend server
python backend_api.py
# API will be available at http://localhost:8000
# Documentation at http://localhost:8000/docs
```

### Frontend Development Server
```bash
cd frontend
npm run dev
# Frontend will be available at http://localhost:3000
```

## 🎯 How It Works

### Architecture Overview

```
┌─────────────────┐    WebSocket     ┌──────────────────┐
│   React Frontend │◄─────────────────┤  FastAPI Backend │
│                 │                  │                  │
│ • MCTS Tree     │    REST API      │ • MCTS Engine    │
│ • Evolution     │◄─────────────────┤ • Evolution      │
│ • Program Bank  │                  │ • GPT-4o         │
│ • Control Panel │                  │ • Session Mgmt   │
└─────────────────┘                  └──────────────────┘
                                              │
                                              ▼
                                     ┌──────────────────┐
                                     │   Your Existing  │
                                     │   MCTS/Evolution │
                                     │   Python Code    │
                                     └──────────────────┘
```

### Data Flow

1. **User Configuration** → Frontend stores settings in Zustand store
2. **Start Evolution** → Frontend sends request to backend API
3. **MCTS/Evolution** → Backend runs your existing algorithms
4. **Real-time Updates** → Backend streams progress via WebSocket
5. **Visualization** → Frontend updates D3.js visualizations in real-time
6. **User Interaction** → Click nodes/candidates to explore details

### Key Technologies

**Frontend:**
- ⚛️ **React 19** with TypeScript
- 🎨 **Tailwind CSS** for styling
- 📊 **D3.js** for tree visualizations
- 📈 **Recharts** for evolution charts
- 🌊 **Framer Motion** for animations
- 🏪 **Zustand** for state management

**Backend:**
- ⚡ **FastAPI** for REST API
- 🔌 **WebSockets** for real-time updates
- 🧠 **Your existing MCTS/Evolution code**
- 🤖 **GPT-4o integration**

## 📊 Visualization Features

### MCTS Tree
- **Node size** represents visit count
- **Node color** represents reward/value
- **Edge thickness** shows selection frequency
- **Animations** for node expansion and selection
- **Zoom and pan** for large trees

### Evolution Population
- **Scatter plot** of fitness vs complexity
- **Color coding** by mutation strategy
- **Time series** of fitness evolution
- **Population details** with lineage tracking

### Program Bank
- **Grid view** with search and filters
- **Composition mode** for program building
- **Usage statistics** and fitness metrics
- **Code preview** with syntax highlighting

## 🎛️ Configuration Options

### GPT-4o Settings
- **API Key**: Your OpenAI API key
- **Model**: `gpt-4o` or `gpt-4o-mini`
- **Temperature**: Creativity vs consistency (0.0-1.0)
- **Max Tokens**: Response length limit

### MCTS Parameters
- **Iterations**: Number of MCTS search iterations
- **Exploration Constant**: UCB exploration parameter
- **Target Task**: Programming task to solve

### Evolution Settings
- **Generations**: Number of evolution cycles
- **Population Size**: Candidates per generation
- **Mutation Rate**: Probability of mutations
- **Selection Strategy**: Tournament, roulette, or elitism

## 💰 Cost Estimation

The control panel provides real-time cost estimates based on:
- **MCTS Phase**: ~$0.05-0.20 per cycle with gpt-4o-mini
- **Evolution Phase**: ~$0.02-0.10 per cycle
- **Total**: ~$0.35-1.50 for a 5-cycle evolution run

Costs scale with iterations, generations, and model choice.

## 🔧 Customization

### Adding New Visualizations
1. Create component in `frontend/src/components/`
2. Add to main tabs in `App.tsx`
3. Connect to store data in `store/index.ts`

### Extending the API
1. Add endpoints in `backend_api.py`
2. Update types in `frontend/src/types/`
3. Add API methods in `hooks/useEvolutionAPI.ts`

### Custom MCTS/Evolution Integration
1. Replace mock data in `backend_api.py` with your algorithms
2. Ensure data matches the expected interfaces
3. Add custom metrics and visualizations as needed

## 🐛 Troubleshooting

### Common Issues

**"Failed to connect to backend"**
- Ensure backend is running on port 8000
- Check firewall settings
- Verify API dependencies are installed

**"Frontend won't start"**
- Run `npm install` in the frontend directory
- Check Node.js version (16+ required)
- Clear npm cache: `npm cache clean --force`

**"Evolution not starting"**
- Verify GPT-4o API key is valid
- Check OpenAI account has credits
- Ensure all Python dependencies are installed

**"Tree visualization not showing"**
- Check browser console for D3.js errors
- Ensure WebSocket connection is active
- Try refreshing the page

### Debug Mode

Add `?debug=true` to the URL for additional logging:
```
http://localhost:3000?debug=true
```

## 🤝 Contributing

This frontend is designed to showcase your MCTS + Evolution research! Feel free to:

- 🎨 Customize the visualizations
- 📊 Add new metrics and charts
- 🔧 Integrate with your specific algorithms
- 📚 Extend the program bank features
- 🌍 Share with the research community

## 📄 License

MIT License - see your main project LICENSE file.

---

**🧠 EvolDSL: Where AI learns to program by programming itself! ⚡**

*Built with ❤️ for the future of autonomous programming*