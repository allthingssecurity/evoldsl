import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Toaster } from 'react-hot-toast'
import { useAppStore } from './store'
import { useWebSocket } from './hooks/useWebSocket'
import { useEvolutionAPI } from './hooks/useEvolutionAPI'
import MCTSTree from './components/MCTSTree'
import EvolutionView from './components/EvolutionView'
import ProgramBank from './components/ProgramBank'
import ControlPanel from './components/ControlPanel'
import { 
  Network, 
  Zap, 
  Layers, 
  Settings,
  Brain,
  Activity,
  Code,
  Maximize2,
  Minimize2
} from 'lucide-react'

function App() {
  const [selectedTab, setSelectedTab] = useState<'mcts' | 'evolution' | 'programs'>('mcts')
  const [isControlPanelExpanded, setIsControlPanelExpanded] = useState(true)
  const [sessionId] = useState(() => `session_${Date.now()}`)
  
  const { 
    visualizationState, 
    systemStatus,
    setVisualizationMode,
    // Demo data initialization
    updateMCTSTree,
    setMCTSRoot,
    addEvolutionGeneration,
    addSubProgram
  } = useAppStore()

  // Initialize WebSocket connection and API
  const websocket = useWebSocket(sessionId)
  const evolutionAPI = useEvolutionAPI(sessionId)

  // Initialize with empty tree - API composition will populate it
  useEffect(() => {
    // Start with empty MCTS tree
    updateMCTSTree({})
    setMCTSRoot(null)
    
    // Load demo APIs into program bank
    const demoAPIs = [
      {
        id: 'search_news',
        name: 'search_news',
        code: 'search_news(query: string) -> article_list',
        description: 'Search for news articles based on query',
        parameters: ['query'],
        returnType: 'article_list',
        complexity: 2,
        usageCount: 45,
        tags: ['data', 'news', 'search'],
        fitness: 0.85
      },
      {
        id: 'analyze_sentiment',
        name: 'analyze_sentiment', 
        code: 'analyze_sentiment(text: article_list) -> sentiment_score',
        description: 'Analyze sentiment of text content',
        parameters: ['text'],
        returnType: 'sentiment_score',
        complexity: 4,
        usageCount: 32,
        tags: ['analysis', 'sentiment', 'ai'],
        fitness: 0.92
      },
      {
        id: 'create_chart',
        name: 'create_chart',
        code: 'create_chart(data: stock_data) -> chart_url',
        description: 'Create data visualization charts',
        parameters: ['data'],
        returnType: 'chart_url',
        complexity: 3,
        usageCount: 28,
        tags: ['visualization', 'charts', 'data'],
        fitness: 0.78
      },
      {
        id: 'generate_report',
        name: 'generate_report',
        code: 'generate_report(summary: summary, analysis: trend_analysis) -> final_report',
        description: 'Generate comprehensive business report',
        parameters: ['summary', 'analysis'],
        returnType: 'final_report',
        complexity: 5,
        usageCount: 15,
        tags: ['output', 'report', 'business'],
        fitness: 0.88
      }
    ]
    
    demoAPIs.forEach(api => addSubProgram(api))
  }, [])

  const tabs = [
          returnType: 'int',
          bodyTokens: ['def', 'factorial(n):'],
          isComplete: false,
          depth: 0,
          code: 'def factorial(n):'
        },
        parent: undefined,
        children: ['base_case', 'recursive_case'],
        visits: 45,
        totalReward: 38.2,
        ucbScore: 2.1,
        isExpanded: true,
        isSelected: false,
        action: {
          actionType: 'define_function' as const,
          value: 'def factorial(n):',
          description: 'Define factorial function'
        },
        depth: 0
      },
      'base_case': {
        id: 'base_case',
        state: {
          functionName: 'factorial',
          params: ['n'],
          returnType: 'int', 
          bodyTokens: ['if', 'eq(n,', '0):'],
          isComplete: false,
          depth: 1,
          code: 'def factorial(n):\n    if eq(n, 0):'
        },
        parent: 'root',
        children: ['return_one'],
        visits: 28,
        totalReward: 25.1,
        ucbScore: 1.8,
        isExpanded: true,
        isSelected: false,
        action: {
          actionType: 'add_base_case' as const,
          value: 'if eq(n, 0):',
          description: 'Add base case check'
        },
        depth: 1
      },
      'recursive_case': {
        id: 'recursive_case',
        state: {
          functionName: 'factorial',
          params: ['n'],
          returnType: 'int',
          bodyTokens: ['else:'],
          isComplete: false,
          depth: 1,
          code: 'def factorial(n):\n    if eq(n, 0):\n        return 1\n    else:'
        },
        parent: 'root',
        children: ['recursive_call'],
        visits: 22,
        totalReward: 19.8,
        ucbScore: 1.6,
        isExpanded: true,
        isSelected: false,
        action: {
          actionType: 'add_else_clause' as const,
          value: 'else:',
          description: 'Add else clause for recursion'
        },
        depth: 1
      },
      'return_one': {
        id: 'return_one',
        state: {
          functionName: 'factorial',
          params: ['n'],
          returnType: 'int',
          bodyTokens: ['return', '1'],
          isComplete: true,
          depth: 2,
          code: 'def factorial(n):\n    if eq(n, 0):\n        return 1'
        },
        parent: 'base_case',
        children: [],
        visits: 18,
        totalReward: 17.1,
        ucbScore: 1.4,
        isExpanded: false,
        isSelected: false,
        action: {
          actionType: 'return_one' as const,
          value: 'return 1',
          description: 'Return 1 for base case'
        },
        depth: 2
      },
      'recursive_call': {
        id: 'recursive_call',
        state: {
          functionName: 'factorial',
          params: ['n'],
          returnType: 'int',
          bodyTokens: ['return', 'mul(n,', 'factorial(sub(n,', '1)))'],
          isComplete: true,
          depth: 2,
          code: 'def factorial(n):\n    if eq(n, 0):\n        return 1\n    else:\n        return mul(n, factorial(sub(n, 1)))'
        },
        parent: 'recursive_case',
        children: [],
        visits: 35,
        totalReward: 33.2,
        ucbScore: 1.9,
        isExpanded: false,
        isSelected: true,
        action: {
          actionType: 'recursive_call' as const,
          value: 'return mul(n, factorial(sub(n, 1)))',
          description: 'Add recursive multiplication call'
        },
        depth: 2
      }
    }

    // updateMCTSTree(demoMCTSTree)
    // setMCTSRoot('root')
    */

    // Demo evolution data
    const demoGeneration = {
      generation: 0,
      population: [
        {
          id: 'candidate_1',
          function: {
            name: 'factorial',
            params: ['n'],
            paramTypes: ['int'],
            returnType: 'int',
            body: 'def factorial(n):\n    if eq(n, 0):\n        return 1\n    else:\n        return mul(n, factorial(sub(n, 1)))',
            implementation: '',
            fitnessScore: 0.85,
            usageCount: 12,
            isEvolved: true
          },
          generation: 0,
          parentFunctions: [],
          fitness: 0.85,
          isSelected: false,
          mutationStrategy: 'add_recursion'
        },
        {
          id: 'candidate_2',
          function: {
            name: 'power',
            params: ['base', 'exp'],
            paramTypes: ['int', 'int'],
            returnType: 'int',
            body: 'def power(base, exp):\n    if eq(exp, 0):\n        return 1\n    else:\n        return mul(base, power(base, sub(exp, 1)))',
            implementation: '',
            fitnessScore: 0.78,
            usageCount: 8,
            isEvolved: true
          },
          generation: 0,
          parentFunctions: [],
          fitness: 0.78,
          isSelected: false,
          mutationStrategy: 'add_recursion'
        },
        {
          id: 'candidate_3',
          function: {
            name: 'max_two',
            params: ['a', 'b'],
            paramTypes: ['int', 'int'],
            returnType: 'int',
            body: 'def max_two(a, b):\n    return if_then_else(gt(a, b), a, b)',
            implementation: '',
            fitnessScore: 0.72,
            usageCount: 15,
            isEvolved: true
          },
          generation: 0,
          parentFunctions: [],
          fitness: 0.72,
          isSelected: false,
          mutationStrategy: 'combine_functions'
        }
      ],
      bestFitness: 0.85,
      averageFitness: 0.78,
      newMutations: ['add_recursion', 'combine_functions'],
      timestamp: Date.now()
    }

    addEvolutionGeneration(demoGeneration)

    // Demo program bank data
    const demoPrograms = [
      {
        id: 'prog_1',
        name: 'add',
        code: 'def add(x, y):\n    return x + y',
        description: 'Basic addition operation',
        parameters: ['x', 'y'],
        returnType: 'number',
        complexity: 1,
        usageCount: 45,
        tags: ['arithmetic', 'basic', 'primitive'],
        fitness: 0.95
      },
      {
        id: 'prog_2',
        name: 'factorial',
        code: 'def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)',
        description: 'Recursive factorial computation',
        parameters: ['n'],
        returnType: 'number',
        complexity: 5,
        usageCount: 23,
        tags: ['recursive', 'mathematical', 'evolved'],
        fitness: 0.87
      },
      {
        id: 'prog_3',
        name: 'fibonacci',
        code: 'def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)',
        description: 'Fibonacci sequence generator',
        parameters: ['n'],
        returnType: 'number',
        complexity: 6,
        usageCount: 18,
        tags: ['recursive', 'sequence', 'evolved'],
        fitness: 0.82
      },
      {
        id: 'prog_4',
        name: 'max_two',
        code: 'def max_two(a, b):\n    return a if a > b else b',
        description: 'Return maximum of two numbers',
        parameters: ['a', 'b'],
        returnType: 'number',
        complexity: 2,
        usageCount: 31,
        tags: ['comparison', 'utility', 'basic'],
        fitness: 0.78
      },
      {
        id: 'prog_5',
        name: 'power',
        code: 'def power(base, exp):\n    if exp == 0:\n        return 1\n    return base * power(base, exp - 1)',
        description: 'Exponentiation using recursion',
        parameters: ['base', 'exp'],
        returnType: 'number',
        complexity: 4,
        usageCount: 12,
        tags: ['recursive', 'mathematical', 'evolved'],
        fitness: 0.84
      }
    ]

    demoPrograms.forEach(prog => addSubProgram(prog))
  }, [])

  const tabs = [
    { id: 'mcts', label: 'MCTS Tree', icon: Network, color: 'blue' },
    { id: 'evolution', label: 'Evolution', icon: Zap, color: 'purple' },
    { id: 'programs', label: 'Program Bank', icon: Layers, color: 'green' }
  ]

  return (
    <div className="h-screen bg-gray-50 flex flex-col overflow-hidden">
      <Toaster position="top-right" />
      
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <Brain className="text-blue-600" size={28} />
              <h1 className="text-2xl font-bold text-gray-900">EvolDSL</h1>
            </div>
            <div className="text-sm text-gray-600 border-l border-gray-300 pl-3">
              MCTS + Evolution Programming
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Status Indicators */}
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 text-sm">
                <Activity className={`${systemStatus.isRunning ? 'text-green-500' : 'text-gray-400'}`} size={16} />
                <span className="text-gray-600">
                  {systemStatus.currentPhase === 'idle' ? 'Ready' : systemStatus.currentPhase.toUpperCase()}
                </span>
              </div>
              
              <div className="flex items-center gap-2 text-sm">
                <Code className="text-blue-500" size={16} />
                <span className="text-gray-600">
                  GPT-4o {systemStatus.isRunning ? 'Active' : 'Standby'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Control Panel */}
        <div className={`${isControlPanelExpanded ? 'w-80' : 'w-12'} bg-gray-50 border-r border-gray-200 transition-all duration-300 flex-shrink-0`}>
          <div className="h-full flex flex-col">
            {/* Toggle Button */}
            <button
              onClick={() => setIsControlPanelExpanded(!isControlPanelExpanded)}
              className="p-3 bg-white border-b border-gray-200 hover:bg-gray-50 flex items-center justify-center"
            >
              {isControlPanelExpanded ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
            </button>
            
            {/* Control Panel Content */}
            <div className="flex-1 overflow-hidden">
              <AnimatePresence>
                {isControlPanelExpanded && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="h-full p-4 overflow-y-auto"
                  >
                    <ControlPanel 
                      onStartEvolution={evolutionAPI.startEvolution}
                      onStopEvolution={evolutionAPI.stopEvolution}
                      isAPILoading={evolutionAPI.isLoading}
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Tab Navigation */}
          <div className="bg-white border-b border-gray-200 px-6 py-2 flex-shrink-0">
            <div className="flex gap-1">
              {tabs.map(({ id, label, icon: Icon, color }) => (
                <button
                  key={id}
                  onClick={() => {
                    setSelectedTab(id as any)
                    setVisualizationMode(id as any)
                  }}
                  className={`px-4 py-2 rounded-lg transition-all flex items-center gap-2 ${
                    selectedTab === id
                      ? `bg-${color}-100 text-${color}-700`
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                  }`}
                >
                  <Icon size={16} />
                  {label}
                </button>
              ))}
            </div>
          </div>

          {/* Tab Content */}
          <div className="flex-1 p-6 overflow-hidden">
            <AnimatePresence mode="wait">
              <motion.div
                key={selectedTab}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.2 }}
                className="h-full"
              >
                {selectedTab === 'mcts' && <MCTSTree />}
                {selectedTab === 'evolution' && <EvolutionView />}
                {selectedTab === 'programs' && <ProgramBank />}
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App