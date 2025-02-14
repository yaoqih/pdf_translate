<template>
  <div class="home">
    <!-- 密钥合并卡片 -->
    <el-card class="merge-card">
      <template #header>
        <div class="card-header">
          <h3>密钥合并</h3>
        </div>
      </template>
      
      <el-form :model="mergeForm" label-width="120px">
        <el-form-item label="目标密钥">
          <el-input v-model="mergeForm.target_key" placeholder="请输入要合并到的目标密钥" />
        </el-form-item>
        
        <el-form-item label="源密钥列表">
          <el-input
            type="textarea"
            v-model="mergeForm.source_keys_text"
            :rows="4"
            placeholder="请输入要合并的源密钥列表，每行一个密钥"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleMergeKeys" :loading="merging">
            合并密钥
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 文件上传卡片 -->
    <el-card class="upload-card">
      <template #header>
        <div class="card-header">
          <h2>PDF翻译服务</h2>
        </div>
      </template>
      
      <el-form :model="form" label-width="120px">
        <el-form-item label="翻译密钥" required>
          <el-input v-model="form.key" placeholder="请输入翻译密钥" />
        </el-form-item>

        <el-form-item label="源语言" required>
          <el-select v-model="form.source_language" placeholder="请选择源语言">
            <el-option
              v-for="(name, value) in languageOptions"
              :key="value"
              :label="name"
              :value="value"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="PDF文件" required>
          <el-upload
            class="upload-demo"
            drag
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            accept=".pdf"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或 <em>点击上传</em>
            </div>
          </el-upload>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleUpload" :loading="uploading">
            上传并翻译
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 密钥查询卡片 -->
    <el-card class="key-card">
      <template #header>
        <div class="card-header">
          <h3>密钥查询</h3>
          <el-input
            v-model="queryKey"
            placeholder="输入密钥查看已翻译的文件"
            style="width: 300px"
            clearable
            @change="getFiles"
          >
            <template #append>
              <el-button @click="getFiles">
                <el-icon><search /></el-icon>
              </el-button>
            </template>
          </el-input>
        </div>
      </template>
      
      <!-- 密钥信息 -->
      <el-descriptions v-if="keyInfo" :column="3" class="mt-4">
        <el-descriptions-item label="密钥">{{ keyInfo.key }}</el-descriptions-item>
        <el-descriptions-item label="剩余页数">{{ keyInfo.page_count }}</el-descriptions-item>
        <el-descriptions-item label="已使用页数">{{ keyInfo.used_count || 0 }}</el-descriptions-item>
        <el-descriptions-item label="总页数">{{ (keyInfo.page_count || 0) + (keyInfo.used_count || 0) }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="keyInfo.is_active ? 'success' : 'danger'">
            {{ keyInfo.is_active ? '有效' : '无效' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="过期时间">{{ formatDate(keyInfo.expired_at) }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 文件列表 -->
    <el-card class="file-list" v-if="files.length">
      <template #header>
        <div class="card-header">
          <h3>文件列表</h3>
          <el-button @click="getFiles" :icon="Refresh">刷新</el-button>
        </div>
      </template>
      
      <el-table :data="files" style="width: 100%">
        <el-table-column prop="filename" label="文件名" />
        <el-table-column label="页数">
          <template #default="{ row }">
            {{ row.translated_pages || row.page_count }}/{{ row.page_count }}
          </template>
        </el-table-column>
        <el-table-column prop="source_language" label="源语言">
          <template #default="{ row }">
            {{ languageOptions[row.source_language] }}
          </template>
        </el-table-column>
        <el-table-column prop="file_status" label="处理状态">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.file_status)">
              {{ getStatusText(row.file_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="上传时间">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button-group>
              <el-button size="small" @click="handleDownload(row.id)">
                下载原文
              </el-button>
              <el-button
                size="small"
                type="success"
                @click="handleDownload(row.id, 'translated')"
                :disabled="row.file_status !== 'completed'"
              >
                下载译文
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { pdfAPI, keyAPI } from '@/api'
import { Refresh, Search, UploadFilled } from '@element-plus/icons-vue'

const form = ref({
  key: '',
  file: null,
  source_language: 'en_to_zh'
})

const mergeForm = ref({
  target_key: '',
  source_keys_text: ''
})

const queryKey = ref(localStorage.getItem('translationKey') || '')
const files = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const uploading = ref(false)
const merging = ref(false)
const keyInfo = ref(null)

// 语言选项
const languageOptions = {
  en_to_zh: '英语 → 中文',
  zh_to_en: '中文 → 英语',
  ja_to_zh: '日语 → 中文',
  ko_to_zh: '韩语 → 中文',
  fr_to_zh: '法语 → 中文',
  de_to_zh: '德语 → 中文',
  es_to_zh: '西班牙语 → 中文',
  ru_to_zh: '俄语 → 中文'
}

// 获取文件列表
const getFiles = async () => {
  try {
    const params = {
      page: currentPage.value,
      size: pageSize.value
    }
    
    if (queryKey.value) {
      params.key = queryKey.value
      localStorage.setItem('translationKey', queryKey.value)
    }
    
    const res = await pdfAPI.list(params)
    files.value = res.data.items
    total.value = res.total
    keyInfo.value = res.data.key_info
  } catch (error) {
    console.error('获取文件列表失败:', error)
    ElMessage.error(error.response?.data?.detail || '获取文件列表失败')
  }
}

// 处理文件选择
const handleFileChange = (file) => {
  form.value.file = file.raw
}

// 处理文件上传
const handleUpload = async () => {
  const key = form.value.key.trim()
  if (!key) {
    ElMessage.warning('请输入翻译密钥')
    return
  }

  if (!form.value.file) {
    ElMessage.warning('请选择要上传的PDF文件')
    return
  }
  
  uploading.value = true
  try {
    // 先获取密钥信息
    const keyRes = await keyAPI.getInfo(key)
    if (!keyRes.data.is_active) {
      ElMessage.warning('密钥已失效')
      uploading.value = false
      return
    }

    const remainingPages = keyRes.data.page_count
    
    // 上传文件
    try {
      const res = await pdfAPI.upload(
        form.value.file,
        form.value.source_language,
        key
      )
      
      // 如果上传成功，说明页数符合要求
      ElMessage.success('文件上传成功，开始翻译处理')
      form.value.file = null
      // 保存密钥到本地存储
      localStorage.setItem('translationKey', key)
      queryKey.value = key
      // 刷新文件列表
      getFiles()
    } catch (error) {
      // 如果是页数超出错误，询问是否部分翻译
      if (error.response?.data?.detail?.includes('密钥可用页数不足')) {
        const pdfPageCount = parseInt(error.response.headers['x-pdf-page-count'])
        
        const confirmResult = await ElMessageBox.confirm(
          `PDF文件共${pdfPageCount}页，但密钥仅剩${remainingPages}页可用。是否只翻译前${remainingPages}页？`,
          '页数超出提示',
          {
            confirmButtonText: '是',
            cancelButtonText: '否',
            type: 'warning'
          }
        ).catch(() => false)

        if (!confirmResult) {
          uploading.value = false
          return
        }
        
        // 重新上传，这次带上翻译页数
        const res = await pdfAPI.upload(
          form.value.file,
          form.value.source_language,
          key,
          remainingPages
        )
        
        ElMessage.success('文件上传成功，开始翻译处理')
        form.value.file = null
        // 保存密钥到本地存储
        localStorage.setItem('translationKey', key)
        queryKey.value = key
        // 刷新文件列表
        getFiles()
      } else {
        // 其他错误直接抛出
        throw error
      }
    }
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error(error.response?.data?.detail || '上传失败')
  } finally {
    uploading.value = false
  }
}

// 处理密钥合并
const handleMergeKeys = async () => {
  if (!mergeForm.value.target_key) {
    ElMessage.warning('请输入目标密钥')
    return
  }

  if (!mergeForm.value.source_keys_text.trim()) {
    ElMessage.warning('请输入要合并的源密钥列表')
    return
  }

  const source_keys = mergeForm.value.source_keys_text
    .split('\n')
    .map(key => key.trim())
    .filter(key => key)

  if (source_keys.length === 0) {
    ElMessage.warning('请输入有效的源密钥')
    return
  }

  if (source_keys.includes(mergeForm.value.target_key)) {
    ElMessage.warning('源密钥列表不能包含目标密钥')
    return
  }

  merging.value = true
  try {
    const res = await keyAPI.merge({
      target_key: mergeForm.value.target_key,
      source_keys: source_keys
    })
    ElMessage.success(`密钥合并成功，合并后的总页数: ${res.data.total_pages}`)
    mergeForm.value.source_keys_text = ''
    
    // 如果当前使用的密钥是被合并的密钥之一，刷新文件列表
    if ([...source_keys, mergeForm.value.target_key].includes(form.value.key)) {
      getFiles()
    }
  } catch (error) {
    console.error('合并失败:', error)
  } finally {
    merging.value = false
  }
}

// 处理文件下载
const handleDownload = (fileId, type = 'original') => {
  pdfAPI.download(fileId, type, type === 'translated' ? queryKey.value : null)
}

// 处理页码变化
const handlePageChange = () => {
  getFiles()
}

// 获取状态类型
const getStatusType = (status) => {
  const types = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return types[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const texts = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return texts[status] || status
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString()
}

// 在组件挂载时自动填充上次使用的密钥
onMounted(() => {
  const savedKey = localStorage.getItem('translationKey')
  if (savedKey) {
    form.value.key = savedKey
  }
  getFiles()
})
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.merge-card,
.upload-card,
.key-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upload-demo {
  width: 100%;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-upload-dragger) {
  width: 100%;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style> 