<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getProjects, createProject, deleteProject } from '../api'
import { ElMessageBox, ElMessage } from 'element-plus'

const router = useRouter()
const projects = ref([])
const showDialog = ref(false)
const form = ref({ name: '', security_level: '三级', organization: '', eval_date: '', reviewer: '' })

const loadProjects = async () => {
  const { data } = await getProjects()
  projects.value = data
}

const handleCreate = async () => {
  if (!form.value.name || !form.value.organization) {
    ElMessage.warning('请填写系统名称和被测单位')
    return
  }
  await createProject(form.value)
  showDialog.value = false
  form.value = { name: '', security_level: '三级', organization: '', eval_date: '', reviewer: '' }
  ElMessage.success('创建成功')
  loadProjects()
}

const handleDelete = async (id) => {
  await ElMessageBox.confirm('确定删除该项目？所有相关数据将被清除。', '确认删除', { type: 'warning' })
  await deleteProject(id)
  ElMessage.success('已删除')
  loadProjects()
}

onMounted(loadProjects)
</script>

<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <h2 style="margin: 0;">评测项目</h2>
      <el-button type="primary" @click="showDialog = true">
        <el-icon style="margin-right: 5px;"><Plus /></el-icon>新建项目
      </el-button>
    </div>

    <el-row :gutter="16">
      <el-col :xs="24" :sm="12" :lg="8" v-for="p in projects" :key="p.id" style="margin-bottom: 16px;">
        <el-card shadow="hover" style="cursor: pointer;" @click="router.push(`/project/${p.id}`)">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span style="font-weight: bold; font-size: 16px;">{{ p.name }}</span>
              <el-tag :type="p.security_level === '三级' ? 'danger' : 'warning'" size="small">{{ p.security_level }}</el-tag>
            </div>
          </template>
          <p style="color: #666; margin-bottom: 8px;">{{ p.organization }}</p>
          <div style="display: flex; gap: 16px; color: #999; font-size: 13px;">
            <span>评测对象: {{ p.eval_object_count || 0 }}</span>
            <span>问题: {{ p.issue_count || 0 }}</span>
          </div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px;">
            <span style="color: #999; font-size: 12px;">{{ p.eval_date || '未设置日期' }}</span>
            <el-button type="danger" size="small" text @click.stop="handleDelete(p.id)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-empty v-if="projects.length === 0" description="暂无项目，点击右上角新建" />

    <el-dialog v-model="showDialog" title="新建评测项目" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="系统名称" required>
          <el-input v-model="form.name" placeholder="被测系统名称" />
        </el-form-item>
        <el-form-item label="等保级别" required>
          <el-radio-group v-model="form.security_level">
            <el-radio value="二级">二级</el-radio>
            <el-radio value="三级">三级</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="被测单位" required>
          <el-input v-model="form.organization" placeholder="被测单位名称缩写" />
        </el-form-item>
        <el-form-item label="评测日期">
          <el-date-picker v-model="form.eval_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="评测复核员">
          <el-input v-model="form.reviewer" placeholder="复核员姓名" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>
