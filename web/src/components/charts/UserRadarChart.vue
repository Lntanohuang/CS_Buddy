<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue'
import * as echarts from 'echarts'
import type { LearningRadarMetric } from '@/types'

const props = defineProps<{
  metrics: LearningRadarMetric[]
  values: number[]
}>()

const chartRoot = ref<HTMLElement | null>(null)
const chartInstance = shallowRef<echarts.ECharts | null>(null)

let resizeObserver: ResizeObserver | null = null

function getThemeValue(name: string, fallback: string) {
  if (typeof window === 'undefined') return fallback
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback
}

function renderChart() {
  if (!chartRoot.value) return

  if (!chartInstance.value) {
    chartInstance.value = echarts.init(chartRoot.value)
  }

  const accentPrimary = getThemeValue('--accent-primary', '#4A7C6F')
  const accentSecondary = getThemeValue('--accent-secondary', '#E8C07A')
  const borderColor = getThemeValue('--border', '#EBEBEA')
  const textColor = getThemeValue('--text-primary', '#37352F')
  const mutedTextColor = getThemeValue('--text-secondary', '#9B9A97')
  const panelColor = getThemeValue('--bg-card', '#FFFFFF')

  chartInstance.value.setOption(
    {
      animationDuration: 500,
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(55, 53, 47, 0.92)',
        borderWidth: 0,
        textStyle: {
          color: '#FFFFFF',
        },
      },
      radar: {
        radius: '65%',
        center: ['50%', '54%'],
        splitNumber: 4,
        axisName: {
          color: textColor,
          fontSize: 13,
          fontWeight: 600,
        },
        splitLine: {
          lineStyle: {
            color: borderColor,
          },
        },
        splitArea: {
          areaStyle: {
            color: [
              'rgba(255,255,255,0.92)',
              'rgba(247, 246, 243, 0.9)',
              'rgba(255,255,255,0.82)',
              'rgba(247, 246, 243, 0.72)',
            ],
          },
        },
        axisLine: {
          lineStyle: {
            color: borderColor,
          },
        },
        indicator: props.metrics.map((metric) => ({
          name: metric.label,
          max: metric.max,
        })),
      },
      series: [
        {
          type: 'radar',
          symbol: 'circle',
          symbolSize: 7,
          lineStyle: {
            width: 3,
            color: accentPrimary,
          },
          itemStyle: {
            color: accentSecondary,
            borderColor: panelColor,
            borderWidth: 2,
          },
          areaStyle: {
            color: 'rgba(74, 124, 111, 0.22)',
          },
          label: {
            show: true,
            color: mutedTextColor,
            fontSize: 11,
            formatter(params: { value: number[] }) {
              const value = Array.isArray(params.value) ? params.value.join(', ') : params.value
              return `${value}`
            },
          },
          data: [
            {
              value: props.values,
              name: '学习能力画像',
            },
          ],
        },
      ],
    },
    true,
  )

  chartInstance.value.resize()
}

onMounted(async () => {
  await nextTick()
  renderChart()

  if (chartRoot.value && typeof ResizeObserver !== 'undefined') {
    resizeObserver = new ResizeObserver(() => {
      chartInstance.value?.resize()
    })
    resizeObserver.observe(chartRoot.value)
  }
})

watch(
  [() => props.metrics, () => props.values],
  () => {
    renderChart()
  },
  { deep: true },
)

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  resizeObserver = null
  chartInstance.value?.dispose()
  chartInstance.value = null
})
</script>

<template>
  <div ref="chartRoot" class="user-radar-chart" />
</template>

<style scoped>
.user-radar-chart {
  width: 100%;
  min-height: 320px;
  height: 100%;
}
</style>
