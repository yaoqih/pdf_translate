<template>
  <div>
    <!-- 密钥信息卡片 -->
    <el-card v-if="keyInfo" class="mb-4">
      <template #header>
        <div class="card-header">
          <span>密钥信息</span>
        </div>
      </template>
      <el-descriptions :column="3">
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

    <!-- 文件列表卡片 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>文件列表</h3>
          <el-input
            v-model="queryKey"
            placeholder="输入密钥查看已翻译的文件"
            style="width: 300px"
            clearable
            @change="getList"
          >
            <template #append>
              <el-button @click="getList">
                <el-icon><search /></el-icon>
              </el-button>
            </template>
          </el-input>
        </div>
      </template>
      # ... existing code ...
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getFileList, uploadFile, downloadFile } from '@/api/pdf'
import { formatDate } from '@/utils/format'
import { Search } from '@element-plus/icons-vue'

const files = ref([])
const total = ref(0)
const loading = ref(false)
const keyInfo = ref(null)
const queryKey = ref(localStorage.getItem('translationKey') || '')

const currentPage = ref(1)
const pageSize = ref(10)

const getList = async () => {
  try {
    loading.value = true
    const key = queryKey.value
    if (key) {
      localStorage.setItem('translationKey', key)
    }
    const res = await getFileList({
      page: currentPage.value,
      size: pageSize.value,
      key: key
    })
    files.value = res.data.items
    total.value = res.total
    keyInfo.value = res.data.key_info
  } catch (error) {
    console.error('获取文件列表失败:', error)
    ElMessage.error('获取文件列表失败')
  } finally {
    loading.value = false
  }
}

# ... existing code ...
</script> 