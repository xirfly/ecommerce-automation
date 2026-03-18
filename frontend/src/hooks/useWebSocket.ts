import { useEffect, useRef, useCallback, useState } from 'react'
import { message as antdMessage } from 'antd'

interface WebSocketMessage {
  type: string
  data?: any
  message?: string
  timestamp?: number
}

interface UseWebSocketOptions {
  onTaskUpdate?: (task: any) => void
  onNotification?: (notification: any) => void
  onConnected?: () => void
  onDisconnected?: () => void
}

export const useWebSocket = (options: UseWebSocketOptions = {}) => {
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()
  const heartbeatIntervalRef = useRef<NodeJS.Timeout>()
  const optionsRef = useRef(options)

  // 更新 options ref
  useEffect(() => {
    optionsRef.current = options
  }, [options])

  const connect = useCallback(() => {
    // 防止重复连接
    if (wsRef.current?.readyState === WebSocket.OPEN ||
        wsRef.current?.readyState === WebSocket.CONNECTING) {
      console.log('WebSocket 已连接或正在连接，跳过')
      return
    }

    const token = localStorage.getItem('access_token')
    if (!token) {
      console.warn('未找到 Token，无法建立 WebSocket 连接')
      return
    }

    try {
      // 建立 WebSocket 连接
      const wsUrl = `ws://localhost:8000/ws?token=${token}`
      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        console.log('WebSocket 连接已建立')
        setIsConnected(true)
        optionsRef.current.onConnected?.()

        // 立即发送一次心跳，确保连接保持活跃
        setTimeout(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
              type: 'ping',
              timestamp: Date.now()
            }))
          }
        }, 1000)

        // 启动心跳定时器
        heartbeatIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
              type: 'ping',
              timestamp: Date.now()
            }))
          }
        }, 30000) // 每30秒发送一次心跳
      }

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)

          switch (message.type) {
            case 'connected':
              console.log('WebSocket 连接成功:', message.message)
              break

            case 'task_update':
              // 任务更新
              console.log('收到任务更新:', message.data)
              optionsRef.current.onTaskUpdate?.(message.data)
              break

            case 'notification':
              // 通知消息
              console.log('收到通知:', message.data)
              const notification = message.data

              // 显示 Ant Design 通知
              if (notification) {
                const messageFunc = notification.level === 'error'
                  ? antdMessage.error
                  : notification.level === 'warning'
                  ? antdMessage.warning
                  : notification.level === 'success'
                  ? antdMessage.success
                  : antdMessage.info

                messageFunc(notification.content)
              }

              optionsRef.current.onNotification?.(notification)
              break

            case 'pong':
              // 心跳响应
              console.log('收到心跳响应')
              break

            case 'error':
              console.error('WebSocket 错误:', message.message)
              antdMessage.error(message.message || 'WebSocket 错误')
              break

            default:
              console.log('未知消息类型:', message.type)
          }
        } catch (error) {
          console.error('解析 WebSocket 消息失败:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket 错误:', error)
        console.error('WebSocket URL:', wsUrl)
        console.error('WebSocket readyState:', ws.readyState)
        console.error('Token 前10位:', token.substring(0, 10))
        setIsConnected(false)
      }

      ws.onclose = () => {
        console.log('WebSocket 连接已关闭')
        setIsConnected(false)
        optionsRef.current.onDisconnected?.()

        // 清理心跳
        if (heartbeatIntervalRef.current) {
          clearInterval(heartbeatIntervalRef.current)
        }

        // 5秒后尝试重连
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('尝试重新连接 WebSocket...')
          connect()
        }, 5000)
      }

      wsRef.current = ws
    } catch (error) {
      console.error('创建 WebSocket 连接失败:', error)
    }
  }, [])

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }

    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current)
    }

    setIsConnected(false)
  }, [])

  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket 未连接，无法发送消息')
    }
  }, [])

  useEffect(() => {
    // 组件挂载时建立连接
    connect()

    // 组件卸载时断开连接
    return () => {
      disconnect()
    }
  }, [connect, disconnect])

  return {
    isConnected,
    sendMessage,
    reconnect: connect,
    disconnect,
  }
}
