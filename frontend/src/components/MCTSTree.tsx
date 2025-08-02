import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAppStore } from '../store'
import { MCTSNode } from '../types'
import { 
  ChevronDown, 
  ChevronRight, 
  Database,
  BarChart3,
  FileText,
  Settings,
  Zap,
  ArrowRight,
  TrendingUp,
  Eye,
  EyeOff,
  Target
} from 'lucide-react'

const MCTSTree: React.FC = () => {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set(['START']))
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [showDetails, setShowDetails] = useState(true)
  
  const {
    mctsTree,
    mctsRoot,
    mctsIterations,
    currentMCTSIteration,
    visualizationState,
    selectMCTSNode
  } = useAppStore()

  // Get category icon and color
  const getCategoryConfig = (category: string) => {
    const configs = {
      'data_source': { 
        icon: Database, 
        color: 'bg-blue-50 text-blue-700 border-blue-200',
        bgColor: 'bg-blue-500'
      },
      'analysis': { 
        icon: BarChart3, 
        color: 'bg-purple-50 text-purple-700 border-purple-200',
        bgColor: 'bg-purple-500'
      },
      'processing': { 
        icon: Settings, 
        color: 'bg-orange-50 text-orange-700 border-orange-200',
        bgColor: 'bg-orange-500'
      },
      'visualization': { 
        icon: BarChart3, 
        color: 'bg-green-50 text-green-700 border-green-200',
        bgColor: 'bg-green-500'
      },
      'output': { 
        icon: FileText, 
        color: 'bg-red-50 text-red-700 border-red-200',
        bgColor: 'bg-red-500'
      }
    }
    return configs[category as keyof typeof configs] || { 
      icon: Zap, 
      color: 'bg-gray-50 text-gray-700 border-gray-200',
      bgColor: 'bg-gray-500'
    }
  }

  const toggleNode = (nodeId: string) => {
    const newExpanded = new Set(expandedNodes)
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId)
    } else {
      newExpanded.add(nodeId)
    }
    setExpandedNodes(newExpanded)
  }

  const renderAPIChain = () => {
    const nodes = Object.values(mctsTree)
    if (nodes.length === 0) {
      return (
        <div className="flex items-center justify-center h-full text-gray-500">
          <div className="text-center">
            <Target className="mx-auto mb-4 text-gray-300" size={64} />
            <h3 className="text-lg font-medium text-gray-700 mb-2">No API Chain Yet</h3>
            <p className="text-gray-500">Start composition to see the chain grow</p>
          </div>
        </div>
      )
    }

    // Build the actual chain by following connections
    const buildChain = () => {
      const chains: any[] = []
      const visited = new Set<string>()
      
      // Find all nodes that connect to START
      const startConnected = nodes.filter(node => 
        node.api_name !== 'START' && 
        Object.values(node.inputs).includes('START')
      )
      
      // Build chains from each starting point
      startConnected.forEach(startNode => {
        if (visited.has(startNode.id)) return
        
        const chain = [startNode]
        visited.add(startNode.id)
        
        // Follow the chain
        let currentNode = startNode
        while (true) {
          const nextNode = nodes.find(node => 
            node.api_name !== 'START' && 
            !visited.has(node.id) &&
            Object.values(node.inputs).includes(currentNode.id)
          )
          
          if (!nextNode) break
          
          chain.push(nextNode)
          visited.add(nextNode.id)
          currentNode = nextNode
        }
        
        chains.push(chain)
      })
      
      return chains
    }

    const chains = buildChain()
    
    return (
      <div className="space-y-6">
        {/* START Node */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-4"
        >
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-500 rounded-lg">
              <Zap className="text-white" size={16} />
            </div>
            <div>
              <h3 className="font-semibold text-green-900">START</h3>
              <p className="text-sm text-green-700">Initial input: Business Intelligence Goal</p>
            </div>
          </div>
        </motion.div>

        {/* API Chains */}
        {chains.map((chain, chainIndex) => (
          <div key={chainIndex} className="space-y-3">
            <div className="text-sm font-medium text-gray-700 mb-2">
              Chain {chainIndex + 1}: {chain.length} APIs
            </div>
            
            {chain.map((node, index) => {
              const config = getCategoryConfig(node.category)
              const Icon = config.icon
              const isSelected = selectedNode === node.id
              
              return (
                <motion.div
                  key={node.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="relative"
                >
                  {/* Connection Arrow */}
                  {index > 0 && (
                    <div className="flex justify-center mb-2">
                      <ArrowRight className="text-gray-400" size={20} />
                    </div>
                  )}

                  {/* API Node */}
                  <div
                    className={`bg-white/80 backdrop-blur-sm border rounded-xl p-4 cursor-pointer transition-all hover:shadow-md ${
                      isSelected 
                        ? 'border-blue-300 bg-blue-50/80 ring-2 ring-blue-200' 
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => {
                      setSelectedNode(node.id === selectedNode ? null : node.id)
                      selectMCTSNode(node.id)
                    }}
                  >
                    <div className="flex items-start gap-3">
                      <div className={`p-2 rounded-lg ${config.bgColor}`}>
                        <Icon className="text-white" size={16} />
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="font-semibold text-gray-900">{node.api_name}</h3>
                          <div className="flex items-center gap-2">
                            <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">
                              V: {node.visits || 0}
                            </span>
                            <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded">
                              UCB: {(node.ucb_score || 0).toFixed(2)}
                            </span>
                          </div>
                        </div>
                        
                        <p className="text-sm text-gray-600 mb-3">{node.description}</p>
                        
                        {/* Input/Output Flow */}
                        <div className="bg-gray-50 rounded-lg p-3">
                          <div className="grid grid-cols-2 gap-3 text-xs">
                            <div>
                              <span className="font-medium text-gray-700">Inputs:</span>
                              <div className="mt-1 space-y-1">
                                {Object.entries(node.inputs).map(([param, sourceId]) => (
                                  <div key={param} className="flex items-center gap-1">
                                    <span className="text-blue-600">{param}</span>
                                    <span className="text-gray-400">←</span>
                                    <span className="text-gray-600 text-xs">{sourceId}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                            <div>
                              <span className="font-medium text-gray-700">Output:</span>
                              <div className="mt-1">
                                <span className="text-green-600 font-mono text-xs">{node.output_type}</span>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* MCTS Statistics */}
                        {showDetails && (
                          <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
                            <div className="text-center p-2 bg-blue-50 rounded">
                              <div className="font-semibold text-blue-800">{node.visits || 0}</div>
                              <div className="text-blue-600">Visits</div>
                            </div>
                            <div className="text-center p-2 bg-green-50 rounded">
                              <div className="font-semibold text-green-800">
                                {((node.total_reward || 0) / Math.max(node.visits || 1, 1)).toFixed(2)}
                              </div>
                              <div className="text-green-600">Avg Reward</div>
                            </div>
                            <div className="text-center p-2 bg-purple-50 rounded">
                              <div className="font-semibold text-purple-800">{node.depth}</div>
                              <div className="text-purple-600">Depth</div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </div>
        ))}

        {/* Show all remaining nodes that aren't in chains */}
        {(() => {
          const chainNodeIds = new Set(chains.flat().map(node => node.id))
          const remainingNodes = nodes.filter(node => 
            node.api_name !== 'START' && !chainNodeIds.has(node.id)
          )
          
          if (remainingNodes.length === 0) return null
          
          return (
            <div className="mt-8 space-y-3">
              <div className="text-sm font-medium text-gray-700 mb-2">
                Other Explored APIs ({remainingNodes.length})
              </div>
              <div className="grid grid-cols-2 gap-3">
                {remainingNodes.map(node => {
                  const config = getCategoryConfig(node.category)
                  const Icon = config.icon
                  
                  return (
                    <motion.div
                      key={node.id}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="bg-white/60 border border-gray-200 rounded-lg p-3"
                    >
                      <div className="flex items-center gap-2">
                        <div className={`p-1 rounded ${config.bgColor}`}>
                          <Icon className="text-white" size={12} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-medium text-gray-800 truncate">
                            {node.api_name}
                          </div>
                          <div className="text-xs text-gray-500">
                            V: {node.visits} | UCB: {(node.ucb_score || 0).toFixed(2)}
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  )
                })}
              </div>
            </div>
          )
        })()}
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-gray-200/50">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">API Chain Construction</h3>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
              title={showDetails ? 'Hide Details' : 'Show Details'}
            >
              {showDetails ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
        </div>
        
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div className="text-center p-3 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-800">{currentMCTSIteration}</div>
            <div className="text-blue-600">Iteration</div>
          </div>
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-800">{Object.keys(mctsTree).length}</div>
            <div className="text-green-600">APIs</div>
          </div>
          <div className="text-center p-3 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-800">
              {Object.values(mctsTree).reduce((sum, node) => sum + (node.visits || 0), 0)}
            </div>
            <div className="text-purple-600">Total Visits</div>
          </div>
        </div>
      </div>

      {/* Chain Visualization */}
      <div className="flex-1 overflow-auto p-6">
        {renderAPIChain()}
      </div>
    </div>
  )
}

export default MCTSTree