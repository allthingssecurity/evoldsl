// MCTS Types for API Composition
export interface MCTSNode {
  id: string
  api_name: string
  inputs: Record<string, string>  // param -> source_node_id
  output_type: string
  depth: number
  visits: number
  total_reward: number
  ucb_score: number
  children: string[]
  parent?: string
  description: string
  category: string
  
  // Legacy fields for backward compatibility
  state?: ProgramState
  totalReward?: number
  isExpanded?: boolean
  isSelected?: boolean
  action?: MCTSAction
}

export interface ProgramState {
  functionName: string
  params: string[]
  returnType: string
  bodyTokens: string[]
  isComplete: boolean
  depth: number
  code: string
}

export interface MCTSAction {
  actionType: 'call_function' | 'add_literal' | 'add_condition' | 'complete' | 'use_param' | 'add_arg'
  value: string
  description: string
}

// API Composition Types
export interface APIDefinition {
  name: string
  inputs: Record<string, string>  // param_name -> type
  output_type: string
  description: string
  category: string
  cost_estimate: number
}

export interface APIBank {
  apis: Record<string, APIDefinition>
  type_compatibility: Record<string, string[]>
}

export interface APIChain {
  id: string
  nodes: MCTSNode[]
  goal: string
  fitness: number
  total_cost: number
  execution_time: number
}

export interface MCTSIteration {
  iteration: number
  selectedPath: string[]
  expandedNode?: string
  reward: number
  timestamp: number
}

// Evolution Types
export interface EvolutionCandidate {
  id: string
  function: DSLFunction
  generation: number
  parentFunctions: string[]
  fitness: number
  isSelected: boolean
  mutationStrategy?: string
}

export interface DSLFunction {
  name: string
  params: string[]
  paramTypes: string[]
  returnType: string
  body: string
  implementation?: string
  fitnessScore: number
  usageCount: number
  isEvolved: boolean
}

export interface EvolutionGeneration {
  generation: number
  population: EvolutionCandidate[]
  bestFitness: number
  averageFitness: number
  newMutations: string[]
  timestamp: number
}

// Program Bank Types
export interface SubProgram {
  id: string
  name: string
  code: string
  description: string
  parameters: string[]
  returnType: string
  complexity: number
  usageCount: number
  tags: string[]
  fitness: number
}

export interface ProgramComposition {
  id: string
  name: string
  subPrograms: string[]
  compositionType: 'sequence' | 'parallel' | 'conditional' | 'recursive'
  resultCode: string
}

// UI State Types
export interface VisualizationState {
  mode: 'mcts' | 'evolution' | 'composition'
  isRunning: boolean
  speed: number
  showDetails: boolean
  highlightedElements: string[]
}

// API Types
export interface GPT4OConfig {
  apiKey: string
  model: 'gpt-4o' | 'gpt-4o-mini'
  temperature: number
  maxTokens: number
}

export interface MCTSConfig {
  iterations: number
  explorationConstant: number
  targetTask: string
}

export interface EvolutionConfig {
  generations: number
  populationSize: number
  mutationRate: number
  selectionStrategy: 'tournament' | 'roulette' | 'elitism'
}

// WebSocket Message Types
export interface WSMessage {
  type: 'mcts_iteration' | 'evolution_generation' | 'system_status' | 'error'
  data: any
  timestamp: number
}

export interface SystemStatus {
  isRunning: boolean
  currentPhase: 'mcts' | 'evolution' | 'idle'
  progress: {
    current: number
    total: number
    phase: string
  }
  costs: {
    totalCost: number
    mctsPhase: number
    evolutionPhase: number
  }
}