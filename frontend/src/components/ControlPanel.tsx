import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAppStore } from '../store'
import { 
  Settings, 
  DollarSign,
  Cpu,
  Key,
  Target,
  Shuffle,
  ChevronDown,
  ChevronUp,
  Brain,
  Zap,
  BarChart3,
  TrendingUp
} from 'lucide-react'

interface ControlPanelProps {
  onStartEvolution?: () => Promise<void>
  onStopEvolution?: () => Promise<void>
  isAPILoading?: boolean
}

const ControlPanel: React.FC<ControlPanelProps> = ({ 
  onStartEvolution, 
  onStopEvolution,
  isAPILoading = false 
}) => {
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [showCosts, setShowCosts] = useState(false)
  
  const {
    gpt4oConfig,
    mctsConfig,
    evolutionConfig,
    systemStatus,
    visualizationState,
    setGPT4OConfig,
    setMCTSConfig,
    setEvolutionConfig
  } = useAppStore()

  const estimatedCostPerIteration = 0.005
  const totalEstimatedCost = (mctsConfig.iterations * estimatedCostPerIteration) + 
                           (evolutionConfig.generations * evolutionConfig.populationSize * 0.002)

  return (
    <div className="p-6 space-y-6">
      {/* GPT-4o Status */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4">
        <div className="flex items-center gap-3 mb-3">
          <div className="p-2 bg-blue-500 rounded-lg">
            <Brain className="text-white" size={16} />
          </div>
          <div>
            <h3 className="font-semibold text-blue-900">GPT-4o Integration</h3>
            <p className="text-sm text-blue-700">AI-powered value & policy networks</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-sm font-medium text-green-800">Connected & Ready</span>
        </div>
      </div>

      {/* MCTS Configuration */}
      <div className="bg-white/80 backdrop-blur-sm border border-gray-200 rounded-xl p-4">
        <div className="flex items-center gap-3 mb-4">
          <Target className="text-purple-600" size={18} />
          <h3 className="font-semibold text-gray-900">MCTS Configuration</h3>
        </div>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Iterations
            </label>
            <input
              type="range"
              min="5"
              max="30"
              value={mctsConfig.iterations}
              onChange={(e) => setMCTSConfig({ iterations: parseInt(e.target.value) })}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>5</span>
              <span className="font-medium text-purple-600">{mctsConfig.iterations}</span>
              <span>30</span>
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Business Objective
            </label>
            <select
              value={mctsConfig.targetTask}
              onChange={(e) => setMCTSConfig({ targetTask: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white"
            >
              <option value="business_intelligence">Business Intelligence Dashboard</option>
              <option value="risk_analysis">Financial Risk Analysis</option>
              <option value="market_research">Market Research Report</option>
              <option value="competitive_analysis">Competitive Analysis</option>
              <option value="investment_insights">Investment Insights</option>
            </select>
          </div>
        </div>
      </div>

      {/* Evolution Configuration */}
      <div className="bg-white/80 backdrop-blur-sm border border-gray-200 rounded-xl p-4">
        <div className="flex items-center gap-3 mb-4">
          <Zap className="text-orange-600" size={18} />
          <h3 className="font-semibold text-gray-900">Evolution Settings</h3>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Generations
            </label>
            <input
              type="number"
              value={evolutionConfig.generations}
              onChange={(e) => setEvolutionConfig({ generations: parseInt(e.target.value) })}
              min="1"
              max="20"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Population
            </label>
            <input
              type="number"
              value={evolutionConfig.populationSize}
              onChange={(e) => setEvolutionConfig({ populationSize: parseInt(e.target.value) })}
              min="5"
              max="50"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            />
          </div>
        </div>
        
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Mutation Rate: {evolutionConfig.mutationRate}
          </label>
          <input
            type="range"
            min="0.1"
            max="1"
            step="0.1"
            value={evolutionConfig.mutationRate}
            onChange={(e) => setEvolutionConfig({ mutationRate: parseFloat(e.target.value) })}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
          />
        </div>
      </div>

      {/* Performance Metrics */}
      {systemStatus.isRunning && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-4"
        >
          <div className="flex items-center gap-3 mb-3">
            <BarChart3 className="text-green-600" size={18} />
            <h3 className="font-semibold text-green-900">Live Metrics</h3>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-800">
                {systemStatus.progress.current}
              </div>
              <div className="text-sm text-green-600">Iterations</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-800">
                {((systemStatus.progress.current / Math.max(systemStatus.progress.total, 1)) * 100).toFixed(0)}%
              </div>
              <div className="text-sm text-green-600">Complete</div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Cost Estimation */}
      <div className="bg-white/80 backdrop-blur-sm border border-gray-200 rounded-xl">
        <button
          onClick={() => setShowCosts(!showCosts)}
          className="w-full flex items-center justify-between p-4 hover:bg-gray-50/50 transition-colors rounded-xl"
        >
          <div className="flex items-center gap-3">
            <DollarSign className="text-yellow-600" size={18} />
            <span className="font-semibold text-gray-900">Cost Estimation</span>
          </div>
          {showCosts ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>
        
        <AnimatePresence>
          {showCosts && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="px-4 pb-4"
            >
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                <div className="grid grid-cols-2 gap-3 text-sm mb-3">
                  <div>
                    <span className="text-gray-600">MCTS Phase:</span>
                    <div className="font-semibold text-yellow-800">
                      ${(mctsConfig.iterations * estimatedCostPerIteration).toFixed(3)}
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-600">Evolution:</span>
                    <div className="font-semibold text-yellow-800">
                      ${(evolutionConfig.generations * evolutionConfig.populationSize * 0.002).toFixed(3)}
                    </div>
                  </div>
                </div>
                <div className="pt-3 border-t border-yellow-200">
                  <span className="text-gray-600">Total Estimated:</span>
                  <div className="font-bold text-lg text-yellow-900">
                    ${totalEstimatedCost.toFixed(3)}
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Advanced Settings */}
      <div className="bg-white/80 backdrop-blur-sm border border-gray-200 rounded-xl">
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="w-full flex items-center justify-between p-4 hover:bg-gray-50/50 transition-colors rounded-xl"
        >
          <div className="flex items-center gap-3">
            <Cpu className="text-gray-600" size={18} />
            <span className="font-semibold text-gray-900">Advanced Settings</span>
          </div>
          {showAdvanced ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>
        
        <AnimatePresence>
          {showAdvanced && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="px-4 pb-4 space-y-4"
            >
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Max Tokens per Request
                </label>
                <input
                  type="number"
                  value={gpt4oConfig.maxTokens}
                  onChange={(e) => setGPT4OConfig({ maxTokens: parseInt(e.target.value) })}
                  min="100"
                  max="2000"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Temperature: {gpt4oConfig.temperature}
                </label>
                <input
                  type="range"
                  min="0.1"
                  max="1.0"
                  step="0.1"
                  value={gpt4oConfig.temperature}
                  onChange={(e) => setGPT4OConfig({ temperature: parseFloat(e.target.value) })}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Exploration Constant: {mctsConfig.explorationConstant}
                </label>
                <input
                  type="range"
                  min="0.5"
                  max="2.0"
                  step="0.1"
                  value={mctsConfig.explorationConstant}
                  onChange={(e) => setMCTSConfig({ explorationConstant: parseFloat(e.target.value) })}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

export default ControlPanel