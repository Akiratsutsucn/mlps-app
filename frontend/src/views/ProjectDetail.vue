<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProject, updateProject, getEvalObjects, createEvalObject, deleteEvalObject, copyRecords, exportExcel } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const projectId = computed(() => route.params.id)
const project = ref({})
const evalObjects = ref([])
const showObjDialog = ref(false)
const showCopyDialog = ref(false)
const editingProject = ref(false)
const copyTarget = ref(null)
const copySource = ref(null)

const OBJECT_TYPE_GROUPS = [
  {
    label: '通用',
    types: ['物理机房', '网络设备', '安全设备', '服务器/存储', '终端设备',
      '其他系统或设备', '系统管理软件/平台', '业务应用系统/平台',
      '数据资源', '安全相关人员', '安全管理文档', '漏洞扫描', '渗透测试']
  },
  { label: '物联网', types: ['感知节点设备', '网关节点设备'] },
  { label: '工业控制', types: ['工业控制设备', '室外控制设备'] },
  { label: '移动互联', types: ['无线接入设备', '移动终端'] },
  { label: '边缘计算', types: ['MEC节点', '边缘网关'] },
  { label: '大数据', types: ['大数据平台', '数据采集节点'] },
  { label: 'IPv6', types: ['IPv6网络设备', 'IPv6安全设备'] },
  { label: '区块链', types: ['区块链节点', '智能合约系统'] },
  { label: '5G接入', types: ['5G基站', 'UPF设备'] },
]
const OBJECT_TYPES = OBJECT_TYPE_GROUPS.flatMap(g => g.types)

const SUB_TYPES = {
  '系统管理软件/平台': ['云控制台', '数据库', '中间件'],
  '数据资源': ['鉴别数据', '重要业务数据', '主要配置数据', '重要审计数据'],
  '安全相关人员': ['安全管理员', '系统管理员', '审计管理员'],
  '安全管理文档': ['安全管理中心', '安全管理制度', '安全管理机构', '安全管理人员', '安全建设管理', '安全运维管理', '其他安全要求指标'],
  '工业控制设备': ['PLC', 'DCS控制器', 'RTU', 'SCADA系统'],
  'MEC节点': ['通用MEC', '专用MEC'],
  '大数据平台': ['Hadoop集群', 'Spark集群', '数据仓库', '数据湖'],
  '区块链节点': ['共识节点', '普通节点', '轻节点'],
}

const objForm = ref({ object_type: '', name: '', sub_type: '', extra_info: '' })

const loadData = async () => {
  const [pRes, oRes] = await Promise.all([getProject(projectId.value), getEvalObjects(projectId.value)])
  project.value = pRes.data
  evalObjects.value = oRes.data
}

const handleCreateObj = async () => {
  if (!objForm.value.object_type || !objForm.value.name) {
    ElMessage.warning('请填写类型和名称')
    return
  }
  await createEvalObject(projectId.value, objForm.value)
  showObjDialog.value = false
  objForm.value = { object_type: '', name: '', sub_type: '', extra_info: '' }
  ElMessage.success('创建成功')
  loadData()
}

const handleDeleteObj = async (objId) => {
  await ElMessageBox.confirm('确定删除该评测对象？', '确认', { type: 'warning' })
  await deleteEvalObject(projectId.value, objId)
  ElMessage.success('已删除')
  loadData()
}

const openCopyDialog = (obj) => {
  copyTarget.value = obj
  copySource.value = null
  showCopyDialog.value = true
}

const sameTypeObjects = computed(() => {
  if (!copyTarget.value) return []
  return evalObjects.value.filter(o => o.object_type === copyTarget.value.object_type && o.id !== copyTarget.value.id)
})

const handleCopy = async () => {
  if (!copySource.value) { ElMessage.warning('请选择源对象'); return }
  await copyRecords(projectId.value, copyTarget.value.id, copySource.value)
  showCopyDialog.value = false
  ElMessage.success('复制完成')
  loadData()
}

const handleSaveProject = async () => {
  await updateProject(projectId.value, project.value)
  editingProject.value = false
  ElMessage.success('已保存')
}

const handleExport = async () => {
  const { data } = await exportExcel(projectId.value)
  const url = window.URL.createObjectURL(data)
  const a = document.createElement('a')
  a.href = url
  a.download = `${project.value.organization}_${project.value.name}_评测记录.xlsx`
  a.click()
  window.URL.revokeObjectURL(url)
}

const progressPercent = (obj) => {
  if (!obj.progress || !obj.progress.total) return 0
  return Math.round((obj.progress.filled / obj.progress.total) * 100)
}

onMounted(loadData)
</script>

<template>
  <div>
    <el-page-header @back="router.push('/')" style="margin-bottom: 20px;">
      <template #content>
        <span style="font-size: 18px; font-weight: bold;">{{ project.name }}</span>
        <el-tag :type="project.security_level === '三级' ? 'danger' : 'warning'" size="small" style="margin-left: 10px;">{{ project.security_level }}</el-tag>
      </template>
      <template #extra>
        <el-button-group>
          <el-button @click="router.push(`/project/${projectId}/issues`)">
            <el-icon style="margin-right: 4px;"><Warning /></el-icon>问题记录
          </el-button>
          <el-button @click="router.push(`/project/${projectId}/dashboard`)">
            <el-icon style="margin-right: 4px;"><DataAnalysis /></el-icon>统计看板
          </el-button>
          <el-button type="success" @click="handleExport">
            <el-icon style="margin-right: 4px;"><Download /></el-icon>导出Excel
          </el-button>
        </el-button-group>
      </template>
    </el-page-header>

    <!-- 被测系统信息 -->
    <el-card style="margin-bottom: 20px;">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>被测系统信息</span>
          <el-button v-if="!editingProject" text type="primary" @click="editingProject = true">编辑</el-button>
          <el-button v-else type="primary" size="small" @click="handleSaveProject">保存</el-button>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="系统名称">
          <el-input v-if="editingProject" v-model="project.name" size="small" />
          <span v-else>{{ project.name }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="等保级别">
          <el-radio-group v-if="editingProject" v-model="project.security_level" size="small">
            <el-radio value="二级">二级</el-radio>
            <el-radio value="三级">三级</el-radio>
          </el-radio-group>
          <span v-else>{{ project.security_level }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="被测单位">
          <el-input v-if="editingProject" v-model="project.organization" size="small" />
          <span v-else>{{ project.organization }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="评测日期">
          <el-date-picker v-if="editingProject" v-model="project.eval_date" type="date" value-format="YYYY-MM-DD" size="small" />
          <span v-else>{{ project.eval_date || '-' }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="评测复核员">
          <el-input v-if="editingProject" v-model="project.reviewer" size="small" />
          <span v-else>{{ project.reviewer || '-' }}</span>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 评测对象 -->
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>评测对象 ({{ evalObjects.length }})</span>
          <el-button type="primary" size="small" @click="showObjDialog = true">
            <el-icon style="margin-right: 4px;"><Plus /></el-icon>添加评测对象
          </el-button>
        </div>
      </template>
      <el-table :data="evalObjects" stripe>
        <el-table-column prop="object_type" label="类型" width="160" />
        <el-table-column prop="name" label="名称" width="200" />
        <el-table-column prop="sub_type" label="子类型" width="120" />
        <el-table-column label="进度" width="200">
          <template #default="{ row }">
            <el-progress :percentage="progressPercent(row)" :format="() => `${row.progress?.filled || 0}/${row.progress?.total || 0}`" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="260">
          <template #default="{ row }">
            <el-button type="primary" size="small" text @click="router.push(`/project/${projectId}/eval/${row.id}`)">填写检查</el-button>
            <el-button type="warning" size="small" text @click="openCopyDialog(row)">复制结果</el-button>
            <el-button type="danger" size="small" text @click="handleDeleteObj(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新建评测对象 -->
    <el-dialog v-model="showObjDialog" title="添加评测对象" width="500px">
      <el-form :model="objForm" label-width="100px">
        <el-form-item label="对象类型" required>
          <el-select v-model="objForm.object_type" placeholder="选择类型" style="width: 100%;" filterable>
            <el-option-group v-for="group in OBJECT_TYPE_GROUPS" :key="group.label" :label="group.label">
              <el-option v-for="t in group.types" :key="t" :label="t" :value="t" />
            </el-option-group>
          </el-select>
        </el-form-item>
        <el-form-item label="子类型" v-if="SUB_TYPES[objForm.object_type]">
          <el-select v-model="objForm.sub_type" placeholder="选择子类型" style="width: 100%;">
            <el-option v-for="s in SUB_TYPES[objForm.object_type]" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="名称" required>
          <el-input v-model="objForm.name" placeholder="如：核心交换机、Web服务器01" />
        </el-form-item>
        <el-form-item label="备注" v-if="objForm.object_type === '物理机房'">
          <el-input v-model="objForm.extra_info" placeholder="物理位置/地址" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showObjDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreateObj">添加</el-button>
      </template>
    </el-dialog>

    <!-- 复制结果 -->
    <el-dialog v-model="showCopyDialog" title="复制检查结果" width="400px">
      <p style="margin-bottom: 12px;">将其他同类对象的检查结果复制到: <strong>{{ copyTarget?.name }}</strong></p>
      <el-select v-model="copySource" placeholder="选择源对象" style="width: 100%;">
        <el-option v-for="o in sameTypeObjects" :key="o.id" :label="o.name" :value="o.id" />
      </el-select>
      <p v-if="sameTypeObjects.length === 0" style="color: #999; margin-top: 8px;">没有同类型的其他评测对象</p>
      <template #footer>
        <el-button @click="showCopyDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCopy" :disabled="!copySource">复制</el-button>
      </template>
    </el-dialog>
  </div>
</template>
