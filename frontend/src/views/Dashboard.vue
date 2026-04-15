<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getStats, getProject } from '../api'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { PieChart, BarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

use([PieChart, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, CanvasRenderer])

const route = useRoute()
const router = useRouter()
const projectId = computed(() => route.params.id)
const project = ref({})
const stats = ref(null)

const RESULT_COLORS = { '符合': '#92D050', '不符合': '#FF0000', '部分符合': '#FF69B4', '不适用': '#4472C4', '未填写': '#C0C0C0' }
const RISK_COLORS = { '高危': '#FF0000', '中危': '#FF8C00', '低危': '#4472C4' }

const resultPieOption = computed(() => {
  if (!stats.value) return {}
  const data = Object.entries(stats.value.result_counts).map(([name, value]) => ({
    name, value, itemStyle: { color: RESULT_COLORS[name] }
  })).filter(d => d.value > 0)
  return {
    title: { text: '检查结果分布', left: 'center' },
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0 },
    series: [{ type: 'pie', radius: ['40%', '70%'], data, label: { formatter: '{b}\n{d}%' } }]
  }
})

const issuePieOption = computed(() => {
  if (!stats.value) return {}
  const data = Object.entries(stats.value.issue_counts).map(([name, value]) => ({
    name, value, itemStyle: { color: RISK_COLORS[name] }
  })).filter(d => d.value > 0)
  return {
    title: { text: '问题风险分布', left: 'center' },
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0 },
    series: [{ type: 'pie', radius: ['40%', '70%'], data, label: { formatter: '{b}\n{d}%' } }]
  }
})

const progressBarOption = computed(() => {
  if (!stats.value) return {}
  const objs = stats.value.eval_objects || []
  return {
    title: { text: '评测对象完成进度', left: 'center' },
    tooltip: { trigger: 'axis' },
    grid: { left: '20%', right: '10%', bottom: '10%' },
    xAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%' } },
    yAxis: { type: 'category', data: objs.map(o => o.name), inverse: true },
    series: [{
      type: 'bar',
      data: objs.map(o => o.total ? Math.round(o.filled / o.total * 100) : 0),
      itemStyle: { color: '#409EFF' },
      label: { show: true, position: 'right', formatter: '{c}%' }
    }]
  }
})

const EXTENSION_COLORS = {
  '基础通用': '#909399',
  '云计算': '#409EFF',
  '移动互联': '#409EFF',
  '物联网': '#409EFF',
  '工业控制': '#409EFF',
  '边缘计算': '#E6A23C',
  '大数据': '#E6A23C',
  'IPv6': '#E6A23C',
  '区块链': '#E6A23C',
  '5G接入': '#9B59B6',
}

const extensionPieOption = computed(() => {
  if (!stats.value?.extension_stats) return {}
  const data = Object.entries(stats.value.extension_stats).map(([name, value]) => ({
    name, value, itemStyle: { color: EXTENSION_COLORS[name] || '#C0C0C0' }
  })).filter(d => d.value > 0)
  return {
    title: { text: '题库扩展类型分布', left: 'center' },
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0 },
    series: [{ type: 'pie', radius: ['40%', '70%'], data, label: { formatter: '{b}\n{d}%' } }]
  }
})

const loadData = async () => {
  const [pRes, sRes] = await Promise.all([getProject(projectId.value), getStats(projectId.value)])
  project.value = pRes.data
  stats.value = sRes.data
}

onMounted(loadData)
</script>

<template>
  <div>
    <el-page-header @back="router.push(`/project/${projectId}`)" style="margin-bottom: 20px;">
      <template #content><span>统计看板 - {{ project.name }}</span></template>
    </el-page-header>

    <el-row :gutter="16" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="评测对象" :value="stats?.eval_object_count || 0" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="检查项总数" :value="stats?.total_records || 0" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="已填写" :value="stats ? (stats.total_records - stats.result_counts['未填写']) : 0" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="问题总数" :value="stats?.total_issues || 0" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-card><v-chart :option="resultPieOption" style="height: 350px;" /></el-card>
      </el-col>
      <el-col :span="12">
        <el-card><v-chart :option="issuePieOption" style="height: 350px;" /></el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top: 16px;" v-if="stats?.extension_stats">
      <el-col :span="24">
        <el-card><v-chart :option="extensionPieOption" style="height: 350px;" /></el-card>
      </el-col>
    </el-row>

    <el-card style="margin-top: 16px;" v-if="stats?.eval_objects?.length">
      <v-chart :option="progressBarOption" :style="{ height: Math.max(300, (stats.eval_objects.length * 40 + 100)) + 'px' }" />
    </el-card>
  </div>
</template>
