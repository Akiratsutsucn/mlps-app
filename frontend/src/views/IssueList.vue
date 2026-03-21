<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getIssues, createIssue, updateIssue, deleteIssue, getProject } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const projectId = computed(() => route.params.id)
const project = ref({})
const issues = ref([])
const showDialog = ref(false)
const editingId = ref(null)
const form = ref({ description: '', risk_level: '中危', suggestion: '', check_record_id: null })

const RISK_COLORS = { '高危': '#FF0000', '中危': '#FF8C00', '低危': '#4472C4' }

const loadData = async () => {
  const [pRes, iRes] = await Promise.all([getProject(projectId.value), getIssues(projectId.value)])
  project.value = pRes.data
  issues.value = iRes.data
}

const openCreate = () => {
  editingId.value = null
  form.value = { description: '', risk_level: '中危', suggestion: '', check_record_id: null }
  showDialog.value = true
}

const openEdit = (issue) => {
  editingId.value = issue.id
  form.value = { description: issue.description, risk_level: issue.risk_level, suggestion: issue.suggestion || '' }
  showDialog.value = true
}

const handleSave = async () => {
  if (!form.value.description) { ElMessage.warning('请填写问题描述'); return }
  if (editingId.value) {
    await updateIssue(projectId.value, editingId.value, form.value)
  } else {
    await createIssue(projectId.value, form.value)
  }
  showDialog.value = false
  ElMessage.success('保存成功')
  loadData()
}

const handleDelete = async (id) => {
  await ElMessageBox.confirm('确定删除该问题？', '确认', { type: 'warning' })
  await deleteIssue(projectId.value, id)
  ElMessage.success('已删除')
  loadData()
}

onMounted(loadData)
</script>

<template>
  <div>
    <el-page-header @back="router.push(`/project/${projectId}`)" style="margin-bottom: 20px;">
      <template #content><span>问题记录 - {{ project.name }}</span></template>
      <template #extra>
        <el-button type="primary" @click="openCreate">
          <el-icon style="margin-right: 4px;"><Plus /></el-icon>新增问题
        </el-button>
      </template>
    </el-page-header>

    <el-card>
      <el-table :data="issues" stripe>
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="description" label="问题描述" min-width="250" show-overflow-tooltip />
        <el-table-column prop="risk_level" label="风险等级" width="100" align="center">
          <template #default="{ row }">
            <el-tag :color="RISK_COLORS[row.risk_level]" style="color: #fff; border: none;">{{ row.risk_level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="suggestion" label="整改建议" min-width="200" show-overflow-tooltip />
        <el-table-column prop="client_opinion" label="甲方确认意见" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="150" align="center">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="openEdit(row)">编辑</el-button>
            <el-button text type="danger" size="small" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="issues.length === 0" description="暂无问题记录" />
    </el-card>

    <el-dialog v-model="showDialog" :title="editingId ? '编辑问题' : '新增问题'" width="600px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="问题描述" required>
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="描述发现的问题" />
        </el-form-item>
        <el-form-item label="风险等级" required>
          <el-radio-group v-model="form.risk_level">
            <el-radio value="高危">高危</el-radio>
            <el-radio value="中危">中危</el-radio>
            <el-radio value="低危">低危</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="整改建议">
          <el-input v-model="form.suggestion" type="textarea" :rows="3" placeholder="整改建议" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
