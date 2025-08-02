import { useEffect, useRef, useCallback } from 'react'
import { useAppStore } from '../store'
import { WSMessage } from '../types'
import toast from 'react-hot-toast'

export const useWebSocket = (sessionId: string) => {
  const ws = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<number | null>(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5
  
  const {
    updateMCTSTree,
    addMCTSIteration,
    addEvolutionGeneration,
    setSystemStatus,
    setIsRunning,
    setMCTSRoot
  } = useAppStore()

  const setupWebSocketHandlers = useCallback(() => {
    if (!ws.current) return

      ws.current.onopen = () => {
        console.log('WebSocket connected successfully')
        reconnectAttempts.current = 0
        toast.success('Connected to server')
      }

      ws.current.onmessage = (event) => {
        try {
          const message: WSMessage = JSON.parse(event.data)
          handleMessage(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.current.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason)
        
        if (event.code !== 1000 && reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 10000)
          reconnectTimeoutRef.current = window.setTimeout(() => {
            reconnectAttempts.current++
            console.log(`Reconnect attempt ${reconnectAttempts.current}`)
            connect()
          }, delay)
        } else if (reconnectAttempts.current >= maxReconnectAttempts) {
          toast.error('Lost connection to server')
        }
      }

      ws.current.onerror = (error) => {
        console.error('WebSocket connection error:', error)
        if (reconnectAttempts.current === 0) {
          toast.error('Failed to connect to server - ensure backend is running')
        }
      }
  }, [])

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      return
    }

    // Add small delay to ensure backend is ready
    setTimeout(() => {
      const apiUrl = 'http://localhost:8000'
      const wsUrl = `${apiUrl.replace('http', 'ws')}/ws/${sessionId}`
      
      console.log(`Connecting to WebSocket: ${wsUrl}`)
      ws.current = new WebSocket(wsUrl)
      
      setupWebSocketHandlers()
    }, 500)
  }, [sessionId, setupWebSocketHandlers])

  const handleMessage = useCallback((message: WSMessage) => {
    console.log('Received WebSocket message:', message.type, message.data)
    
    switch (message.type) {
      case 'mcts_update':
        // Handle MCTS tree updates from backend
        if (message.data.nodes) {
          console.log('Updating MCTS tree with nodes:', Object.keys(message.data.nodes))
          updateMCTSTree(message.data.nodes)
          
          // Set root if we have nodes
          if (message.data.root_id) {
            setMCTSRoot(message.data.root_id)
          } else if (message.data.nodes['START']) {
            setMCTSRoot('START')
          }
        }
        if (message.data.iteration !== undefined) {
          addMCTSIteration({
            iteration: message.data.iteration,
            selectedPath: [],
            reward: message.data.reward || 0,
            timestamp: message.timestamp
          })
        }
        break

      case 'system_status':
        console.log('System status update:', message.data)
        setSystemStatus(message.data)
        setIsRunning(message.data.isRunning)
        break

      case 'error':
        console.error('Server error:', message.data)
        toast.error(message.data.message || 'Server error')
        break

      default:
        console.log('Unknown message type:', message.type, message.data)
    }
  }, [updateMCTSTree, addMCTSIteration, setSystemStatus, setIsRunning, setMCTSRoot])

  const sendMessage = useCallback((message: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message))
    }
  }, [])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    
    if (ws.current) {
      ws.current.close(1000, 'Intentional disconnect')
      ws.current = null
    }
  }, [])

  useEffect(() => {
    // Delay initial connection to ensure proper app initialization
    const timer = setTimeout(() => {
      connect()
    }, 1000)
    
    return () => {
      clearTimeout(timer)
      disconnect()
    }
  }, [connect, disconnect])

  return {
    isConnected: ws.current?.readyState === WebSocket.OPEN,
    sendMessage,
    disconnect,
    reconnect: connect
  }
}