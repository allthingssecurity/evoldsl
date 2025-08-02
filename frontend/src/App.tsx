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
  Database, 
  Settings,
  Brain,
  Activity,
  Play,
  Pause,
  RotateCcw
} from 'lucide-react'

function App() {
  const [sessionId] = useState(() => `session_${Date.now()}`)
  
  const { 
    visualizationState, 
    systemStatus,
    updateMCTSTree,
    setMCTSRoot,
    addSubProgram,
    setIsRunning
  } = useAppStore()

  // Initialize WebSocket connection and API
  const websocket = useWebSocket(sessionId)
  const evolutionAPI = useEvolutionAPI(sessionId)

  // Initialize with empty tree (but don't clear subPrograms)
  useEffect(() => {
    updateMCTSTree({})
    setMCTSRoot(null)
    // Don't clear subPrograms here - let ProgramBank handle API loading
  }, [])

  const handleStartComposition = async () => {
    setIsRunning(true)
    await evolutionAPI.startEvolution()
  }

  const handleStopComposition = async () => {
    setIsRunning(false)
    await evolutionAPI.stopEvolution()
  }

  const handleResetComposition = () => {
    setIsRunning(false)
    updateMCTSTree({})
    setMCTSRoot(null)
  }

  return (
    <div className="h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex flex-col overflow-hidden">
      <Toaster position="top-right" />
      
      {/* Professional Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200/50 px-8 py-4 flex-shrink-0 shadow-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl">
                <Brain className="text-white" size={24} />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 bg-clip-text text-transparent">
                  API Composer Pro
                </h1>
                <p className="text-sm text-gray-600">
                  Intelligent API Chain Construction with MCTS + GPT-4o
                </p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-6">
            {/* Status Indicator */}
            <div className="flex items-center gap-3">
              <div className={`flex items-center gap-2 px-3 py-2 rounded-lg ${
                systemStatus.isRunning 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-gray-100 text-gray-600'
              }`}>
                <Activity className={`${systemStatus.isRunning ? 'text-green-500 animate-pulse' : 'text-gray-400'}`} size={16} />
                <span className="text-sm font-medium">
                  {systemStatus.isRunning ? 'Composing...' : 'Ready'}
                </span>
              </div>
              
              <div className="flex items-center gap-2 px-3 py-2 bg-blue-100 text-blue-800 rounded-lg">
                <Brain className="text-blue-600" size={16} />
                <span className="text-sm font-medium">GPT-4o Enhanced</span>
              </div>
            </div>

            {/* Main Controls */}
            <div className="flex items-center gap-2">
              {!systemStatus.isRunning ? (
                <button
                  onClick={handleStartComposition}
                  disabled={evolutionAPI.isLoading}
                  className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:from-green-700 hover:to-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm"
                >
                  {evolutionAPI.isLoading ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Play size={16} />
                  )}
                  Start Composition
                </button>
              ) : (
                <button
                  onClick={handleStopComposition}
                  disabled={evolutionAPI.isLoading}
                  className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-red-600 to-rose-600 text-white rounded-lg hover:from-red-700 hover:to-rose-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm"
                >
                  {evolutionAPI.isLoading ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Pause size={16} />
                  )}
                  Stop
                </button>
              )}
              
              <button
                onClick={handleResetComposition}
                disabled={evolutionAPI.isLoading}
                className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm"
              >
                <RotateCcw size={16} />
                Reset
              </button>
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        {systemStatus.isRunning && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">{systemStatus.progress.phase}</span>
              <span className="text-sm text-gray-600">
                {systemStatus.progress.current} / {systemStatus.progress.total}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-blue-600 to-purple-600 h-2 rounded-full transition-all duration-500"
                style={{ 
                  width: `${(systemStatus.progress.current / Math.max(systemStatus.progress.total, 1)) * 100}%` 
                }}
              />
            </div>
          </motion.div>
        )}
      </header>

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - API Bank */}
        <div className="w-96 bg-white/70 backdrop-blur-sm border-r border-gray-200/50 flex flex-col shadow-sm">
          <div className="p-6 border-b border-gray-200/50">
            <div className="flex items-center gap-3 mb-2">
              <Database className="text-blue-600" size={20} />
              <h2 className="text-lg font-semibold text-gray-900">API Bank</h2>
            </div>
            <p className="text-sm text-gray-600">
              Select APIs to build intelligent chains
            </p>
          </div>
          <div className="flex-1 overflow-hidden">
            <ProgramBank />
          </div>
        </div>

        {/* Center Panel - MCTS Visualization */}
        <div className="flex-1 bg-white/50 backdrop-blur-sm flex flex-col">
          <div className="p-6 border-b border-gray-200/50">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Network className="text-purple-600" size={20} />
                <h2 className="text-lg font-semibold text-gray-900">API Chain Builder</h2>
              </div>
              <div className="text-sm text-gray-600">
                MCTS Tree Search with GPT-4o Guidance
              </div>
            </div>
          </div>
          <div className="flex-1 overflow-hidden">
            <MCTSTree />
          </div>
        </div>

        {/* Right Panel - Control & Evolution */}
        <div className="w-80 bg-white/70 backdrop-blur-sm border-l border-gray-200/50 flex flex-col shadow-sm">
          <div className="p-6 border-b border-gray-200/50">
            <div className="flex items-center gap-3 mb-2">
              <Settings className="text-orange-600" size={20} />
              <h2 className="text-lg font-semibold text-gray-900">Configuration</h2>
            </div>
            <p className="text-sm text-gray-600">
              Control composition parameters
            </p>
          </div>
          <div className="flex-1 overflow-auto">
            <ControlPanel 
              onStartEvolution={evolutionAPI.startEvolution}
              onStopEvolution={evolutionAPI.stopEvolution}
              isAPILoading={evolutionAPI.isLoading}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default App