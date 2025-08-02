import { useState, useCallback } from 'react'
import { useAppStore } from '../store'
import toast from 'react-hot-toast'

const API_BASE = `http://localhost:8000/api`

export const useEvolutionAPI = (sessionId: string) => {
  const [isLoading, setIsLoading] = useState(false)
  
  const {
    gpt4oConfig,
    mctsConfig,
    evolutionConfig,
    setIsRunning,
    setSystemStatus
  } = useAppStore()

  const startEvolution = useCallback(async () => {
    // API key is handled by backend environment variables
    console.log('Starting API composition with GPT-4o...')

    setIsLoading(true)
    
    try {
      const response = await fetch(`${API_BASE}/sessions/${sessionId}/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          gpt4o_config: gpt4oConfig,
          mcts_config: mctsConfig,
          evolution_config: evolutionConfig,
          goal: `Create comprehensive ${mctsConfig.targetTask.replace('_', ' ')} using intelligent API composition`
        })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to start evolution')
      }

      const result = await response.json()
      
      setIsRunning(true)
      toast.success('Evolution started successfully!')
      
      return true
    } catch (error) {
      console.error('Failed to start evolution:', error)
      toast.error(error instanceof Error ? error.message : 'Failed to start evolution')
      return false
    } finally {
      setIsLoading(false)
    }
  }, [sessionId, gpt4oConfig, mctsConfig, evolutionConfig, setIsRunning])

  const stopEvolution = useCallback(async () => {
    setIsLoading(true)
    
    try {
      const response = await fetch(`${API_BASE}/sessions/${sessionId}/stop`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to stop evolution')
      }

      setIsRunning(false)
      toast.success('Evolution stopped')
      
      return true
    } catch (error) {
      console.error('Failed to stop evolution:', error)
      toast.error(error instanceof Error ? error.message : 'Failed to stop evolution')
      return false
    } finally {
      setIsLoading(false)
    }
  }, [sessionId, setIsRunning])

  const getSessionStatus = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/sessions/${sessionId}/status`)
      
      if (!response.ok) {
        throw new Error('Failed to get session status')
      }

      const status = await response.json()
      
      setSystemStatus({
        isRunning: status.is_running,
        currentPhase: status.current_phase,
        progress: status.progress,
        costs: status.costs
      })
      
      return status
    } catch (error) {
      console.error('Failed to get session status:', error)
      return null
    }
  }, [sessionId, setSystemStatus])

  const getMCTSData = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/sessions/${sessionId}/mcts`)
      
      if (!response.ok) {
        throw new Error('Failed to get MCTS data')
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to get MCTS data:', error)
      return null
    }
  }, [sessionId])

  const getEvolutionData = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/sessions/${sessionId}/evolution`)
      
      if (!response.ok) {
        throw new Error('Failed to get evolution data')
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to get evolution data:', error)
      return null
    }
  }, [sessionId])

  const listSessions = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/sessions`)
      
      if (!response.ok) {
        throw new Error('Failed to list sessions')
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to list sessions:', error)
      return null
    }
  }, [])

  return {
    isLoading,
    startEvolution,
    stopEvolution,
    getSessionStatus,
    getMCTSData,
    getEvolutionData,
    listSessions
  }
}