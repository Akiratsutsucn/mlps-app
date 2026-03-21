<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getCheckRecords, updateCheckRecord, uploadAttachment, getAttachments, deleteAttachment, getProject, getEvalObjects } from '../api'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const projectId = computed(() => route.params.id)
const objId = computed(() => route.params.objId)
const records = ref([])
const evalObject = ref({})
const project = ref({})
const categories = ref([])
const activeCategory = ref('')
const saving = ref(false)
const showAttachments = ref(false)
const currentRecord = ref(null)
const attachments = ref([])

const RESULT_OPTIONS = [
  { label: '符合', value: '符合', color: '#92D050' },
  { label: '不符合', value: '不符合', color: '#FF0000' },
  { label: '部分符合', value: '部分符合', color: '#FF69B4' },
  { label: '不适用', value: '不适用', color: '#4472C4' },
]

const resultColor = (val) => {
  const opt = RESULT_OPTIONS.find(o => o.value === val)
  return opt ? opt.color : '#999'
}

const loadData = async () => {
  const [pRes, oRes] = await Promise.all([
    getProject(projectId.value),
    getEvalObjects(projectId.value)
  ])
  project.value = pRes.data
  const obj = oRes.data.find(o => o.id === parseInt(objId.value))
  if (obj) evalObject.value = obj

  const { data } = await getCheckRecords(objId.value)
  records.value = data
  const cats = [...new Set(data.map(r => r.check_item?.category).filter(Boolean))]
  categories.value = cats
  if (cats.length > 0 && !activeCategory.value) activeCategory.value = cats[0]
}

const filteredRecords = computed(() => {
  if (!activeCategory.value) return records.value
  return records.value.filter(r => r.check_item?.category === activeCategory.value)
})

const filledCount = computed(() => {
  return records.value.filter(r => r.result).length
})

const handleSave = async (record) => {
  saving.value = true
  try {
    await updateCheckRecord(objId.value, record.id, {
      result: record.result,
      description: record.description,
    })
  } finally {
    saving.value = false
  }
}

const openAttachments = async (record) => {
  currentRecord.value = record
  showAttachments.value = true
  const { data } = await getAttachments(objId.value, record.id)
  attachments.value = data
}

const handleUpload = async (options) => {
  const formData = new FormData()
  formData.append('file', options.file)
  await uploadAttachment(objId.value, currentRecord.value.id, formData)
  ElMessage.success('上传成功')
  const { data } = await getAttachments(objId.value, currentRecord.value.id)
  attachments.value = data
}

const handleDeleteAtt = async (att) => {
  await deleteAttachment(objId.value, currentRecord.value.id, att.id)
  attachments.value = attachments.value.filter(a => a.id !== att.id)
}

onMounted(loadData)
</script>

<template>
  <div>
    <el-page-header @back="router.push(`/project/${projectId}`)" style="margin-bottom: 20px;">
      <template #content>
        <span>{{ evalObject.name }}</span>
        <el-tag size="small" style="margin-left: 8px;">{{ evalObject.object_type }}</el-tag>
        <el-tag type="info" size="small" style="margin-left: 8px;">{{ filledCount }}/{{ records.length }} 已填写</el-tag>
      </template>
    </el-page-header>

    <el-card>
      <el-tabs v-model="activeCategory" type="border-card">
        <el-tab-pane v-for="cat in categories" :key="cat" :label="cat" :name="cat">
          <div v-for="(record, idx) in filteredRecords" :key="record.id"
               style="border: 1px solid #eee; border-radius: 8px; padding: 16px; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
              <div style="flex: 1;">
                <span style="color: #999; font-size: 12px; margin-right: 8px;">{{ record.check_item?.item_code || `#${idx + 1}` }}</span>
                <span v-if="record.check_item?.is_cloud_extension">
                  <el-tag size="small" type="info">云扩展</el-tag>
                </span>
                <p style="margin-top: 6px; line-height: 1.6;">{{ record.check_item?.content }}</p>
              </div>
            </div>
            <div style="display: flex; gap: 12px; align-items: flex-start; flex-wrap: wrap;">
              <div style="min-width: 280px;">
                <span style="font-size: 13px; color: #666; margin-bottom: 4px; display: block;">检查结果</span>
                <el-radio-group v-model="record.result" @change="handleSave(record)" size="small">
                  <el-radio-button v-for="opt in RESULT_OPTIONS" :key="opt.value" :value="opt.value"
                    :style="record.result === opt.value ? { '--el-radio-button-checked-bg-color': opt.color, '--el-radio-button-checked-border-color': opt.color } : {}">
                    {{ opt.label }}
                  </el-radio-button>
                </el-radio-group>
              </div>
              <div style="flex: 1; min-width: 300px;">
                <span style="font-size: 13px; color: #666; margin-bottom: 4px; display: block;">描述</span>
                <el-input v-model="record.description" type="textarea" :rows="2" placeholder="选填描述..."
                  @blur="handleSave(record)" />
              </div>
              <div style="padding-top: 18px;">
                <el-button text type="primary" size="small" @click="openAttachments(record)">
                  <el-icon style="margin-right: 4px;"><Paperclip /></el-icon>附件
                </el-button>
              </div>
            </div>
          </div>
          <el-empty v-if="filteredRecords.length === 0" description="该分类下暂无检查项" />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 附件弹窗 -->
    <el-dialog v-model="showAttachments" title="附件管理" width="500px">
      <el-upload :http-request="handleUpload" :show-file-list="false" accept="image/*,.pdf,.doc,.docx">
        <el-button type="primary" size="small">上传文件</el-button>
      </el-upload>
      <div style="margin-top: 12px;">
        <div v-for="att in attachments" :key="att.id" style="display: flex; align-items: center; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee;">
          <a :href="`/uploads/${att.file_path}`" target="_blank" style="color: #409eff;">{{ att.file_name }}</a>
          <el-button type="danger" text size="small" @click="handleDeleteAtt(att)">删除</el-button>
        </div>
        <el-empty v-if="attachments.length === 0" description="暂无附件" :image-size="60" />
      </div>
    </el-dialog>
  </div>
</template>
