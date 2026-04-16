import { BarChart3, Table, PieChart, TrendingUp, Code, AlertCircle } from 'lucide-react'
import { useAppStore } from '../../store/useAppStore'
import { Chart } from './Chart'
import { DataTable } from './DataTable'
import type { ChartConfig } from '../../types'

export function ChartPanel() {
  const { chartConfig, tableData, viewMode, setViewMode, setChartConfig, currentSql } = useAppStore()

  // 检查是否有数据
  const hasData = chartConfig || tableData
  const hasChartData = chartConfig && chartConfig.data && chartConfig.data.length > 0
  const hasTableData = tableData && tableData.rows && tableData.rows.length > 0

  const chartTypes: { type: ChartConfig['type']; icon: React.ReactNode; label: string }[] = [
    { type: 'bar', icon: <BarChart3 className="w-4 h-4" />, label: '柱狀圖' },
    { type: 'line', icon: <TrendingUp className="w-4 h-4" />, label: '折線圖' },
    { type: 'pie', icon: <PieChart className="w-4 h-4" />, label: '圓餅圖' },
  ]

  return (
    <div className="w-full h-full bg-slate-900 border-l border-slate-700/50 flex flex-col min-w-0">
      {/* 顶部栏 */}
      <div className="h-14 border-b border-slate-700/50 flex items-center justify-between px-4">
        <h2 className="text-sm font-medium text-slate-300">數據視覺化</h2>

        {/* 视图切换 */}
        <div className="flex gap-1 bg-slate-800 rounded-lg p-1">
          <button
            onClick={() => setViewMode('chart')}
            className={`px-3 py-1.5 text-xs rounded-md transition-colors ${viewMode === 'chart'
              ? 'bg-blue-600 text-white'
              : 'text-slate-400 hover:text-white'
              }`}
          >
            圖表
          </button>
          <button
            onClick={() => setViewMode('table')}
            className={`px-3 py-1.5 text-xs rounded-md transition-colors ${viewMode === 'table'
              ? 'bg-blue-600 text-white'
              : 'text-slate-400 hover:text-white'
              }`}
          >
            表格
          </button>
        </div>
      </div>

      {/* SQL 展示区 */}
      {currentSql && (
        <div className="px-4 py-3 border-b border-slate-700/50">
          <div className="flex items-center gap-2 text-xs text-slate-400 mb-2">
            <Code className="w-3.5 h-3.5" />
            <span>執行的 SQL</span>
          </div>
          <pre className="bg-slate-800 rounded-lg p-3 overflow-x-auto max-h-32">
            <code className="text-xs text-green-400 whitespace-pre-wrap">{currentSql}</code>
          </pre>
        </div>
      )}

      {/* 图表类型选择器 */}
      {viewMode === 'chart' && hasChartData && (
        <div className="px-4 py-3 border-b border-slate-700/50">
          <div className="flex gap-2">
            {chartTypes.map(({ type, icon, label }) => (
              <button
                key={type}
                onClick={() => chartConfig && setChartConfig({ ...chartConfig, type })}
                className={`
                  flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs
                  transition-colors duration-200
                  ${chartConfig?.type === type
                    ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                    : 'bg-slate-800 text-slate-400 hover:text-white border border-transparent'
                  }
                `}
              >
                {icon}
                {label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 图表/表格区域 */}
      <div className="flex-1 p-4 min-h-0">
        {!hasData ? (
          // 无数据状态
          <div className="h-full flex flex-col items-center justify-center text-slate-500">
            <AlertCircle className="w-12 h-12 mb-4 opacity-30" />
            <p className="text-sm">暫無數據</p>
            <p className="text-xs mt-1 text-slate-600">發送查詢後將顯示結果</p>
          </div>
        ) : viewMode === 'chart' ? (
          hasChartData ? (
            <div className="h-full bg-slate-800/50 rounded-xl p-4">
              <Chart config={chartConfig!} />
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-slate-500">
              <BarChart3 className="w-12 h-12 mb-4 opacity-30" />
              <p className="text-sm">無視覺化數據</p>
              <p className="text-xs mt-1 text-slate-600">切換到表格視圖查看數據</p>
            </div>
          )
        ) : (
          hasTableData ? (
            <div className="h-full bg-slate-800/50 rounded-xl overflow-hidden">
              <DataTable data={tableData!} />
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-slate-500">
              <Table className="w-12 h-12 mb-4 opacity-30" />
              <p className="text-sm">無表格數據</p>
            </div>
          )
        )}
      </div>

      {/* 底部信息 */}
      <div className="px-4 py-3 border-t border-slate-700/50">
        <div className="flex items-center justify-between text-xs text-slate-500">
          <span>
            數據行數: {tableData?.rows?.length || chartConfig?.data?.length || 0}
          </span>
          <span>{hasData ? '即時數據' : '等待查詢'}</span>
        </div>
      </div>
    </div>
  )
}
