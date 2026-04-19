import { useEffect, useState, useRef, useCallback } from 'react'
import { ChatSidebar } from './components/ChatSidebar'
import { ChatArea } from './components/ChatArea'
import { ChartPanel } from './components/ChartPanel'

function App() {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking')
  const [chartPanelWidth, setChartPanelWidth] = useState(450) // 預設 450px 寬
  const isDragging = useRef(false)

  const handleMouseDown = (e: React.MouseEvent) => {
    isDragging.current = true
    e.preventDefault()
    document.body.style.cursor = 'col-resize'
    // 預防反白文字
    document.body.style.userSelect = 'none'
  }

  const handleMouseUp = useCallback(() => {
    if (isDragging.current) {
      isDragging.current = false
      document.body.style.cursor = 'default'
      document.body.style.userSelect = 'auto'
    }
  }, [])

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isDragging.current) return
    const newWidth = window.innerWidth - e.clientX
    if (newWidth > 200 && newWidth < 800) {
      setChartPanelWidth(newWidth)
    }
  }, [])

  useEffect(() => {
    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [handleMouseMove, handleMouseUp])

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch('http://localhost:8001/health')
        if (response.ok) {
          setBackendStatus('connected')
        } else {
          setBackendStatus('disconnected')
        }
      } catch {
        setBackendStatus('disconnected')
      }
    }

    checkBackend()
    // 每 30 秒检查一次
    const interval = setInterval(checkBackend, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="h-screen flex bg-slate-900 text-white overflow-hidden">
      {/* 左侧 - 会话管理 */}
      <ChatSidebar />

      {/* 中间 - 聊天区域 */}
      <div className="flex-1 flex flex-col h-full min-w-0 min-h-0 overflow-hidden">
        <ChatArea />
      </div>

      {/* 拖拽控制杆 (Resizer) */}
      <div
        className="w-1 bg-transparent hover:bg-blue-500 cursor-col-resize transition-colors z-10 flex-shrink-0"
        onMouseDown={handleMouseDown}
      />

      {/* 右侧 - 图表面板 */}
      <div style={{ width: chartPanelWidth, flexShrink: 0 }}>
        <ChartPanel />
      </div>

      {/* 后端状态指示器 */}
      <div className="fixed bottom-4 right-4 z-50">
        {backendStatus === 'checking' && (
          <div className="px-3 py-1.5 bg-slate-800 rounded-full text-slate-400 text-xs flex items-center gap-2">
            <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse" />
            檢查後端連線...
          </div>
        )}
        {backendStatus === 'connected' && (
          <div className="px-3 py-1.5 bg-green-500/20 rounded-full text-green-400 text-xs flex items-center gap-2">
            <div className="w-2 h-2 bg-green-400 rounded-full" />
            後端已連線
          </div>
        )}
        {backendStatus === 'disconnected' && (
          <div className="px-3 py-1.5 bg-red-500/20 rounded-full text-red-400 text-xs flex items-center gap-2">
            <div className="w-2 h-2 bg-red-400 rounded-full" />
            後端未連線
          </div>
        )}
      </div>
    </div>
  )
}

export default App
