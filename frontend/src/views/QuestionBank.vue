<script setup>
import { ref, onMounted } from 'vue'
import { getCheckItems, createCheckItem, updateCheckItem, deleteCheckItem, getCheckItemCount } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const items = ref([])
const total = ref(0)
const loading = ref(false)
const showDialog = ref(false)
const editingId = ref(null)
const filters = ref({
  object_type: '', security_level: '', keyword: '',
  extension_type: '', standard_ref: '',
  page: 1, page_size: 20
})

const OBJECT_TYPES = [
  '物理机房', '网络设备', '安全设备', '服务器/存储', '终端设备',
  '其他系统或设备', '系统管理软件/平台', '业务应用系统/平台',
  '数据资源', '安全相关人员', '安全管理文档', '漏洞扫描', '渗透测试',
  '感知节点设备', '网关节点设备', '工业控制设备', '室外控制设备',
  '无线接入设备', '移动终端', 'MEC节点', '边缘网关',
  '大数据平台', '数据采集节点', 'IPv6网络设备', 'IPv6安全设备',
  '区块链节点', '智能合约系统', '5G基站', 'UPF设备'
]

const EXTENSION_TYPES = [
  { label: '全部', value: '' },
  { label: '基础通用', value: 'base' },
  { label: '云计算', value: '云计算' },
  { label: '移动互联', value: '移动互联' },
  { label: '物联网', value: '物联网' },
  { label: '工业控制', value: '工业控制' },
  { label: '边缘计算', value: '边缘计算' },
  { label: '大数据', value: '大数据' },
  { label: 'IPv6', value: 'IPv6' },
  { label: '区块链', value: '区块链' },
  { label: '5G接入', value: '5G接入' },
]

const STANDARD_REFS = [
  { label: '全部', value: '' },
  { label: 'GB/T 22239-2019', value: 'GB/T 22239-2019' },
  { label: 'GA/T 1390.6-2025', value: 'GA/T 1390.6-2025' },
  { label: 'GA/T 1390.7-2025', value: 'GA/T 1390.7-2025' },
  { label: 'GA/T 1390.8-2025', value: 'GA/T 1390.8-2025' },
  { label: 'GA/T 1390.9-2025', value: 'GA/T 1390.9-2025' },
  { label: 'GA/T 2348-2025', value: 'GA/T 2348-2025' },
]

const EXTENSION_STANDARD_MAP = {
  '云计算': 'GB/T 22239-2019',
  '移动互联': 'GB/T 22239-2019',
  '物联网': 'GB/T 22239-2019',
  '工业控制': 'GB/T 22239-2019',
  '边缘计算': 'GA/T 1390.6-2025',
  '大数据': 'GA/T 1390.7-2025',
  'IPv6': 'GA/T 1390.8-2025',
  '区块链': 'GA/T 1390.9-2025',
  '5G接入': 'GA/T 2348-2025',
}

const getExtensionTagType = (extType) => {
  if (!extType) return 'info'
  const national = ['云计算', '移动互联', '物联网', '工业控制']
  if (national.includes(extType)) return ''
  if (extType === '5G接入') return 'warning'
  return 'warning'
}

const getExtensionLabel = (extType) => extType || '基础通用'

const form = ref({
  object_type: '', security_level: '三级', category: '', sub_category: '',
  item_code: '', content: '', is_cloud_extension: false,
  extension_type: '', standard_ref: ''
})

const loadData = async () => {
  loading.value = true
  try {
    const params = { ...filters.value }
    Object.keys(params).forEach(k => { if (!params[k] && k !== 'page' && k !== 'page_size') delete params[k] })
    const { data } = await getCheckItems(params)
    items.value = data
    const countRes = await getCheckItemCount()
    total.value = countRes.data.total
  } finally {
    loading.value = false
  }
}

const openCreate = () => {
  editingId.value = null
  form.value = { object_type: '', security_level: '三级', category: '', sub_category: '', item_code: '', content: '', is_cloud_extension: false, extension_type: '', standard_ref: '' }
  showDialog.value = true
}

const openEdit = (item) => {
  editingId.value = item.id
  form.value = {
    object_type: item.object_type, security_level: item.security_level,
    category: item.category, sub_category: item.sub_category || '',
    item_code: item.item_code || '', content: item.content,
    is_cloud_extension: item.is_cloud_extension,
    extension_type: item.extension_type || '',
    standard_ref: item.standard_ref || ''
  }
  showDialog.value = true
}

const handleSave = async () => {
  if (!form.value.object_type || !form.value.category || !form.value.content) {
    ElMessage.warning('请填写必填项')
    return
  }
  if (editingId.value) {
    await updateCheckItem(editingId.value, form.value)
  } else {
    await createCheckItem(form.value)
  }
  showDialog.value = false
  ElMessage.success('保存成功')
  loadData()
}

const handleDelete = async (id) => {
  await ElMessageBox.confirm('确定删除该检查项？', '确认', { type: 'warning' })
  await deleteCheckItem(id)
  ElMessage.success('已删除')
  loadData()
}

const handlePageChange = (page) => {
  filters.value.page = page
  loadData()
}

onMounted(loadData)
</script>

<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <h2 style="margin: 0;">题库管理 <el-tag type="info" size="small">共 {{ total }} 条</el-tag></h2>
      <el-button type="primary" @click="openCreate">
        <el-icon style="margin-right: 4px;"><Plus /></el-icon>新增检查项
      </el-button>
    </div>

    <el-card style="margin-bottom: 16px;">
      <el-form :inline="true" :model="filters">
        <el-form-item label="评测对象">
          <el-select v-model="filters.object_type" clearable placeholder="全部" @change="loadData" style="width: 180px;">
            <el-option v-for="t in OBJECT_TYPES" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="等保级别">
          <el-select v-model="filters.security_level" clearable placeholder="全部" @change="loadData" style="width: 100px;">
            <el-option label="二级" value="二级" />
            <el-option label="三级" value="三级" />
          </el-select>
        </el-form-item>
        <el-form-item label="扩展类型">
          <el-select v-model="filters.extension_type" clearable placeholder="全部" @change="loadData" style="width: 130px;">
            <el-option v-for="t in EXTENSION_TYPES" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="标准来源">
          <el-select v-model="filters.standard_ref" clearable placeholder="全部" @change="loadData" style="width: 170px;">
            <el-option v-for="t in STANDARD_REFS" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="搜索内容" clearable @clear="loadData" @keyup.enter="loadData" style="width: 200px;" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="filters.page = 1; loadData()">搜索</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card>
      <el-table :data="items" v-loading="loading" stripe>
        <el-table-column prop="item_code" label="编码" width="140" />
        <el-table-column prop="object_type" label="评测对象类型" width="150" />
        <el-table-column prop="security_level" label="级别" width="70" align="center" />
        <el-table-column prop="category" label="分类" width="130" />
        <el-table-column prop="sub_category" label="子分类" width="120" />
        <el-table-column prop="content" label="检查内容" min-width="300" show-overflow-tooltip />
        <el-table-column label="扩展类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getExtensionTagType(row.extension_type)" size="small">
              {{ getExtensionLabel(row.extension_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="standard_ref" label="标准来源" width="160" />
        <el-table-column label="操作" width="130" align="center">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="openEdit(row)">编辑</el-button>
            <el-button text type="danger" size="small" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div style="margin-top: 16px; display: flex; justify-content: center;">
        <el-pagination :current-page="filters.page" :page-size="filters.page_size" :total="total"
          layout="prev, pager, next" @current-change="handlePageChange" />
      </div>
    </el-card>

    <el-dialog v-model="showDialog" :title="editingId ? '编辑检查项' : '新增检查项'" width="650px">
      <el-form :model="form" label-width="110px">
        <el-form-item label="评测对象类型" required>
          <el-select v-model="form.object_type" placeholder="选择类型" style="width: 100%;">
            <el-option v-for="t in OBJECT_TYPES" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="等保级别" required>
          <el-radio-group v-model="form.security_level">
            <el-radio value="二级">二级</el-radio>
            <el-radio value="三级">三级</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="分类" required>
          <el-input v-model="form.category" placeholder="如：安全计算环境" />
        </el-form-item>
        <el-form-item label="子分类">
          <el-input v-model="form.sub_category" placeholder="如：身份鉴别" />
        </el-form-item>
        <el-form-item label="测评单元编码">
          <el-input v-model="form.item_code" placeholder="如：L3-CES-01-01" />
        </el-form-item>
        <el-form-item label="检查内容" required>
          <el-input v-model="form.content" type="textarea" :rows="4" placeholder="检查项内容" />
        </el-form-item>
        <el-form-item label="扩展类型">
          <el-select v-model="form.extension_type" clearable placeholder="基础通用（不选）" style="width: 100%;"
            @change="(val) => { form.standard_ref = EXTENSION_STANDARD_MAP[val] || '' }">
            <el-option v-for="(std, ext) in EXTENSION_STANDARD_MAP" :key="ext" :label="ext" :value="ext" />
          </el-select>
        </el-form-item>
        <el-form-item label="标准来源">
          <el-select v-model="form.standard_ref" clearable placeholder="自动填充" style="width: 100%;">
            <el-option v-for="t in STANDARD_REFS.slice(1)" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
