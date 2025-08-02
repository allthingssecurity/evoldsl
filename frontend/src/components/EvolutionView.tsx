import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAppStore } from '../store'
import { 
  Zap, 
  TrendingUp, 
  Users, 
  Shuffle, 
  Target,
  BarChart3,
  Clock,
  Award,
  GitBranch,
  Dna
} from 'lucide-react'

const EvolutionView: React.FC = () => {
  const [selectedGeneration, setSelectedGeneration] = useState<number | null>(null)
  
  const {
    evolutionGenerations,
    currentGeneration,
    allCandidates,
    systemStatus
  } = useAppStore()

  const renderEvolutionProgress = () => {
    if (evolutionGenerations.length === 0) {
      return (
        <div className="flex items-center justify-center h-full text-gray-500">
          <div className="text-center">
            <Dna className="mx-auto mb-4 text-gray-300" size={64} />
            <h3 className="text-lg font-medium text-gray-700 mb-2">Evolution Not Started</h3>
            <p className="text-gray-500">Evolution will begin after MCTS completes</p>
          </div>
        </div>
      )
    }

    return (
      <div className="space-y-4">
        {evolutionGenerations.map((generation, index) => (
          <motion.div
            key={generation.generation}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className={`bg-white/80 backdrop-blur-sm border rounded-xl p-4 cursor-pointer transition-all hover:shadow-md ${
              selectedGeneration === generation.generation
                ? 'border-purple-300 bg-purple-50/80 ring-2 ring-purple-200'
                : 'border-gray-200 hover:border-gray-300'
            }`}
            onClick={() => setSelectedGeneration(
              selectedGeneration === generation.generation ? null : generation.generation
            )}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-purple-500 rounded-lg">
                  <GitBranch className="text-white" size={16} />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">
                    Generation {generation.generation}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {generation.population.length} candidates
                  </p>
                </div>
              </div>
              
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <div className="text-sm font-medium text-green-600">
                    Best: {(generation.bestFitness * 100).toFixed(1)}%
                  </div>
                  <div className="text-xs text-gray-500">
                    Avg: {(generation.averageFitness * 100).toFixed(1)}%
                  </div>
                </div>
                <div className="w-12 h-12 bg-gradient-to-br from-purple-400 to-pink-400 rounded-full flex items-center justify-center">
                  <span className="text-white font-bold text-sm">
                    {generation.generation}
                  </span>
                </div>
              </div>
            </div>

            {/* Fitness Progress Bar */}
            <div className="mb-3">
              <div className="flex justify-between text-xs text-gray-600 mb-1">
                <span>Fitness Progress</span>
                <span>{(generation.bestFitness * 100).toFixed(1)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all duration-500"
                  style={{ width: `${generation.bestFitness * 100}%` }}
                />
              </div>
            </div>

            {/* Mutations */}
            {generation.newMutations.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {generation.newMutations.map((mutation, idx) => (
                  <span 
                    key={idx}
                    className="px-2 py-1 bg-orange-100 text-orange-700 text-xs rounded"
                  >
                    {mutation}
                  </span>
                ))}
              </div>
            )}

            {/* Expanded Details */}
            <AnimatePresence>
              {selectedGeneration === generation.generation && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="mt-4 pt-4 border-t border-gray-200"
                >
                  <div className="grid grid-cols-2 gap-4">
                    {/* Top Candidates */}
                    <div>
                      <h4 className="font-medium text-gray-700 mb-2">Top Candidates</h4>
                      <div className="space-y-2">
                        {generation.population
                          .sort((a, b) => b.fitness - a.fitness)
                          .slice(0, 3)
                          .map((candidate, idx) => (
                            <div key={candidate.id} className="bg-gray-50 rounded p-2">
                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium">
                                  #{idx + 1} {candidate.function.name}
                                </span>
                                <span className="text-xs text-green-600">
                                  {(candidate.fitness * 100).toFixed(1)}%
                                </span>
                              </div>
                              <div className="text-xs text-gray-500 mt-1">
                                {candidate.function.params.length} params, 
                                complexity: {candidate.function.paramTypes.length}
                              </div>
                            </div>
                          ))}
                      </div>
                    </div>

                    {/* Generation Stats */}
                    <div>
                      <h4 className="font-medium text-gray-700 mb-2">Statistics</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Population Size:</span>
                          <span className="font-medium">{generation.population.length}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Best Fitness:</span>
                          <span className="font-medium text-green-600">
                            {(generation.bestFitness * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Average Fitness:</span>
                          <span className="font-medium text-blue-600">
                            {(generation.averageFitness * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>New Mutations:</span>
                          <span className="font-medium text-orange-600">
                            {generation.newMutations.length}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-gray-200/50">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Evolution Progress</h3>
          <div className="flex items-center gap-2">
            <Shuffle className="text-purple-600" size={18} />
            <span className="text-sm text-gray-600">
              {systemStatus.currentPhase === 'evolution' ? 'Evolving...' : 'Waiting for MCTS'}
            </span>
          </div>
        </div>
        
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div className="text-center p-3 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-800">{currentGeneration}</div>
            <div className="text-purple-600">Generation</div>
          </div>
          <div className="text-center p-3 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-800">
              {Object.keys(allCandidates).length}
            </div>
            <div className="text-blue-600">Total Candidates</div>
          </div>
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-800">
              {evolutionGenerations.length > 0 
                ? (Math.max(...evolutionGenerations.map(g => g.bestFitness)) * 100).toFixed(0)
                : 0}%
            </div>
            <div className="text-green-600">Best Fitness</div>
          </div>
        </div>
      </div>

      {/* Evolution Timeline */}
      <div className="flex-1 overflow-auto p-6">
        {renderEvolutionProgress()}
      </div>

      {/* Evolution Status */}
      {systemStatus.currentPhase === 'evolution' && (
        <div className="p-4 border-t border-gray-200/50 bg-purple-50/50">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 bg-purple-500 rounded-full animate-pulse"></div>
            <span className="text-sm font-medium text-purple-800">
              Evolution in progress...
            </span>
            <div className="flex-1 bg-purple-200 rounded-full h-2 ml-3">
              <div 
                className="bg-purple-500 h-2 rounded-full transition-all duration-300"
                style={{ 
                  width: `${(systemStatus.progress.current / Math.max(systemStatus.progress.total, 1)) * 100}%` 
                }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default EvolutionView