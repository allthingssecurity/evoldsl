import { create } from 'zustand'
import { subscribeWithSelector } from 'zustand/middleware'
import { 
  MCTSNode, 
  EvolutionCandidate, 
  SubProgram, 
  VisualizationState, 
  GPT4OConfig,
  MCTSConfig,
  EvolutionConfig,
  MCTSIteration,
  EvolutionGeneration,
  SystemStatus
} from '../types'

interface AppState {
  // Configuration
  gpt4oConfig: GPT4OConfig
  mctsConfig: MCTSConfig
  evolutionConfig: EvolutionConfig
  
  // MCTS State
  mctsTree: Record<string, MCTSNode>
  mctsRoot: string | null
  mctsIterations: MCTSIteration[]
  currentMCTSIteration: number
  
  // Evolution State
  evolutionGenerations: EvolutionGeneration[]
  currentGeneration: number
  allCandidates: Record<string, EvolutionCandidate>
  
  // Program Bank
  subPrograms: Record<string, SubProgram>
  selectedPrograms: string[]
  
  // UI State
  visualizationState: VisualizationState
  systemStatus: SystemStatus
  
  // Actions
  setGPT4OConfig: (config: Partial<GPT4OConfig>) => void
  setMCTSConfig: (config: Partial<MCTSConfig>) => void
  setEvolutionConfig: (config: Partial<EvolutionConfig>) => void
  
  // MCTS Actions
  updateMCTSTree: (nodes: Record<string, MCTSNode>) => void
  setMCTSRoot: (rootId: string) => void
  addMCTSIteration: (iteration: MCTSIteration) => void
  selectMCTSNode: (nodeId: string) => void
  
  // Evolution Actions
  addEvolutionGeneration: (generation: EvolutionGeneration) => void
  updateCandidate: (candidate: EvolutionCandidate) => void
  
  // Program Bank Actions
  addSubProgram: (program: SubProgram) => void
  toggleProgramSelection: (programId: string) => void
  
  // UI Actions
  setVisualizationMode: (mode: 'mcts' | 'evolution' | 'composition') => void
  setIsRunning: (isRunning: boolean) => void
  setSystemStatus: (status: Partial<SystemStatus>) => void
  highlightElements: (elementIds: string[]) => void
}

export const useAppStore = create<AppState>()(
  subscribeWithSelector((set, get) => ({
    // Initial Configuration (API key handled by backend)
    gpt4oConfig: {
      apiKey: '', // Backend handles this
      model: 'gpt-4o',
      temperature: 0.7,
      maxTokens: 500,
    },
    mctsConfig: {
      iterations: 15,
      explorationConstant: 1.414,
      targetTask: 'business_intelligence',
    },
    evolutionConfig: {
      generations: 10,
      populationSize: 20,
      mutationRate: 0.3,
      selectionStrategy: 'tournament',
    },
    
    // Initial MCTS State
    mctsTree: {},
    mctsRoot: null,
    mctsIterations: [],
    currentMCTSIteration: 0,
    
    // Initial Evolution State
    evolutionGenerations: [],
    currentGeneration: 0,
    allCandidates: {},
    
    // Initial Program Bank
    subPrograms: {},
    selectedPrograms: [],
    
    // Initial UI State
    visualizationState: {
      mode: 'mcts',
      isRunning: false,
      speed: 1,
      showDetails: true,
      highlightedElements: [],
    },
    systemStatus: {
      isRunning: false,
      currentPhase: 'idle',
      progress: {
        current: 0,
        total: 0,
        phase: 'Idle',
      },
      costs: {
        totalCost: 0,
        mctsPhase: 0,
        evolutionPhase: 0,
      },
    },
    
    // Configuration Actions
    setGPT4OConfig: (config) => set((state) => ({
      gpt4oConfig: { ...state.gpt4oConfig, ...config }
    })),
    
    setMCTSConfig: (config) => set((state) => ({
      mctsConfig: { ...state.mctsConfig, ...config }
    })),
    
    setEvolutionConfig: (config) => set((state) => ({
      evolutionConfig: { ...state.evolutionConfig, ...config }
    })),
    
    // MCTS Actions
    updateMCTSTree: (nodes) => set({ mctsTree: nodes }),
    
    setMCTSRoot: (rootId) => set({ mctsRoot: rootId }),
    
    addMCTSIteration: (iteration) => set((state) => ({
      mctsIterations: [...state.mctsIterations, iteration],
      currentMCTSIteration: iteration.iteration,
    })),
    
    selectMCTSNode: (nodeId) => set((state) => {
      const updatedTree = { ...state.mctsTree }
      // Deselect all nodes
      Object.values(updatedTree).forEach(node => {
        node.isSelected = false
      })
      // Select the target node
      if (updatedTree[nodeId]) {
        updatedTree[nodeId].isSelected = true
      }
      return { mctsTree: updatedTree }
    }),
    
    // Evolution Actions
    addEvolutionGeneration: (generation) => set((state) => {
      const newCandidates = { ...state.allCandidates }
      generation.population.forEach(candidate => {
        newCandidates[candidate.id] = candidate
      })
      
      return {
        evolutionGenerations: [...state.evolutionGenerations, generation],
        currentGeneration: generation.generation,
        allCandidates: newCandidates,
      }
    }),
    
    updateCandidate: (candidate) => set((state) => ({
      allCandidates: {
        ...state.allCandidates,
        [candidate.id]: candidate,
      }
    })),
    
    // Program Bank Actions
    addSubProgram: (program) => set((state) => ({
      subPrograms: {
        ...state.subPrograms,
        [program.id]: program,
      }
    })),
    
    toggleProgramSelection: (programId) => set((state) => {
      const isSelected = state.selectedPrograms.includes(programId)
      return {
        selectedPrograms: isSelected 
          ? state.selectedPrograms.filter(id => id !== programId)
          : [...state.selectedPrograms, programId]
      }
    }),
    
    // UI Actions
    setVisualizationMode: (mode) => set((state) => ({
      visualizationState: { ...state.visualizationState, mode }
    })),
    
    setIsRunning: (isRunning) => set((state) => ({
      visualizationState: { ...state.visualizationState, isRunning },
      systemStatus: { ...state.systemStatus, isRunning }
    })),
    
    setSystemStatus: (status) => set((state) => ({
      systemStatus: { ...state.systemStatus, ...status }
    })),
    
    highlightElements: (elementIds) => set((state) => ({
      visualizationState: { 
        ...state.visualizationState, 
        highlightedElements: elementIds 
      }
    })),
  }))
)