import ReactECharts from 'echarts-for-react'
import type { ChartConfig } from '../../types'

interface ChartProps {
  config: ChartConfig
}

/**
 * 安全地將任意值轉換為數字
 * 處理逗號分隔的千分位數字、陣列、字串等各種情境
 * 若無法解析則回傳 0，絕對不會回傳 NaN
 */
function parseValue(val: any): number {
  if (val == null) return 0
  if (typeof val === 'number') return isNaN(val) ? 0 : val
  if (Array.isArray(val)) {
    // 若是陣列，取第一個可解析的數字
    const first = val.find((v) => typeof v === 'number' || (typeof v === 'string' && !isNaN(Number(v.replace(/,/g, '')))))
    return first != null ? parseValue(first) : 0
  }
  if (typeof val === 'string') {
    // 移除千分位逗號後再轉型
    const cleaned = val.replace(/,/g, '').trim()
    const num = Number(cleaned)
    return isNaN(num) ? 0 : num
  }
  return 0
}

/**
 * 安全地取得物件上的屬性值
 */
function getField(obj: any, field: string): any {
  if (obj == null) return undefined
  return obj[field]
}

export function Chart({ config }: ChartProps) {
  const getOption = () => {
    const { type, title, data, xField, yField } = config

    const baseOption = {
      title: {
        text: title,
        textStyle: {
          color: '#e2e8f0',
          fontSize: 14,
        },
        left: 'center',
      },
      tooltip: {
        trigger: type === 'pie' ? 'item' : 'axis',
        backgroundColor: 'rgba(30, 41, 59, 0.9)',
        borderColor: '#475569',
        textStyle: { color: '#e2e8f0' },
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true,
      },
    }

    switch (type) {
      case 'bar':
        return {
          ...baseOption,
          xAxis: {
            type: 'category',
            data: data.map((d) => String(getField(d, xField || 'name') ?? '')),
            axisLine: { lineStyle: { color: '#475569' } },
            axisLabel: { color: '#94a3b8' },
          },
          yAxis: {
            type: 'value',
            axisLine: { lineStyle: { color: '#475569' } },
            axisLabel: { color: '#94a3b8' },
            splitLine: { lineStyle: { color: '#334155' } },
          },
          series: [
            {
              type: 'bar',
              data: data.map((d) => parseValue(getField(d, yField || 'value'))),
              itemStyle: {
                color: {
                  type: 'linear',
                  x: 0, y: 0, x2: 0, y2: 1,
                  colorStops: [
                    { offset: 0, color: '#3b82f6' },
                    { offset: 1, color: '#1d4ed8' },
                  ],
                },
                borderRadius: [4, 4, 0, 0],
              },
            },
          ],
        }

      case 'line':
        return {
          ...baseOption,
          xAxis: {
            type: 'category',
            data: data.map((d) => String(getField(d, xField || 'name') ?? '')),
            axisLine: { lineStyle: { color: '#475569' } },
            axisLabel: { color: '#94a3b8' },
          },
          yAxis: {
            type: 'value',
            axisLine: { lineStyle: { color: '#475569' } },
            axisLabel: { color: '#94a3b8' },
            splitLine: { lineStyle: { color: '#334155' } },
          },
          series: [
            {
              type: 'line',
              data: data.map((d) => parseValue(getField(d, yField || 'value'))),
              smooth: true,
              lineStyle: { color: '#3b82f6', width: 2 },
              areaStyle: {
                color: {
                  type: 'linear',
                  x: 0, y: 0, x2: 0, y2: 1,
                  colorStops: [
                    { offset: 0, color: 'rgba(59, 130, 246, 0.3)' },
                    { offset: 1, color: 'rgba(59, 130, 246, 0.05)' },
                  ],
                },
              },
              itemStyle: { color: '#3b82f6' },
            },
          ],
        }

      case 'pie':
        return {
          ...baseOption,
          series: [
            {
              type: 'pie',
              radius: ['40%', '70%'],
              center: ['50%', '55%'],
              data: data.map((d) => ({
                name: String(getField(d, xField || 'name') ?? ''),
                value: parseValue(getField(d, yField || 'value')),
              })),
              label: {
                color: '#94a3b8',
              },
              itemStyle: {
                borderColor: '#1e293b',
                borderWidth: 2,
              },
            },
          ],
        }

      default:
        return baseOption
    }
  }

  return (
    <ReactECharts
      key={config.type}
      option={getOption()}
      style={{ height: '100%', width: '100%' }}
      theme="dark"
    />
  )
}
