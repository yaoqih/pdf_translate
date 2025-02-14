<template>
  <div class="keys-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>密钥管理</h3>
          <el-button type="primary" @click="dialogVisible = true">
            生成新密钥
          </el-button>
        </div>
      </template>
      
      <!-- 密钥列表 -->
      <el-table :data="keys" style="width: 100%">
        <el-table-column prop="key" label="密钥" width="280" />
        <el-table-column prop="page_count" label="剩余页数" width="100">
          <template #default="{ row }">
            <el-tag :type="row.page_count > 0 ? 'success' : 'danger'">
              {{ row.page_count }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? '有效' : '已停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="expired_at" label="过期时间">
          <template #default="{ row }">
            {{ new Date(row.expired_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button-group>
              <el-button
                size="small"
                type="primary"
                @click="handleCopy(row.key)"
              >
                复制密钥
              </el-button>
              <el-button
                size="small"
                :type="selectedKeys.includes(row.key) ? 'success' : 'default'"
                @click="toggleKeySelection(row.key)"
                :disabled="!row.is_active || row.page_count <= 0"
              >
                {{ selectedKeys.includes(row.key) ? '已选择' : '选择' }}
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          :total="total"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>
    
    <!-- 合并密钥按钮 -->
    <div class="merge-keys" v-if="selectedKeys.length > 1">
      <el-button type="primary" @click="handleMergeKeys">
        合并选中的密钥 ({{ selectedKeys.length }})
      </el-button>
    </div>
    
    <!-- 生成密钥对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="生成新密钥"
      width="500px"
    >
      <el-form :model="form" label-width="120px">
        <el-form-item label="可翻译页数">
          <el-input-number v-model="form.page_count" :min="1" />
        </el-form-item>
        <el-form-item label="有效期">
          <el-date-picker
            v-model="form.expired_at"
            type="datetime"
            placeholder="选择有效期"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleGenerateKey">
            确认生成
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { keyAPI } from '@/api'
import { ElMessage } from 'element-plus'

const keys = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const dialogVisible = ref(false)
const selectedKeys = ref([])

const form = ref({
  page_count: 1,
  max_uses: 1,
  expired_at: null
})

// 生成新密钥
const handleGenerateKey = async () => {
  if (!form.value.page_count || form.value.page_count < 1) {
    ElMessage.warning('请输入有效的可翻译页数')
    return
  }

  try {
    const res = await keyAPI.generate({
      page_count: form.value.page_count,
      max_uses: form.value.max_uses || 1,
      expired_at: form.value.expired_at
    })
    ElMessage.success('密钥生成成功')
    dialogVisible.value = false
    form.value = {
      page_count: 1,
      max_uses: 1,
      expired_at: null
    }
    getKeys()
    
    // 复制密钥到剪贴板
    await navigator.clipboard.writeText(res.data.key)
    ElMessage.success('密钥已复制到剪贴板')
  } catch (error) {
    console.error('生成密钥失败:', error)
    ElMessage.error(error.response?.data?.detail || '生成密钥失败')
  }
}

// 获取密钥列表
const getKeys = async () => {
  try {
    const res = await keyAPI.list({
      page: currentPage.value,
      size: pageSize.value
    })
    
    // 确保数据存在
    if (res?.data) {
      keys.value = res.data.items || []
      total.value = res.data.total || 0
      
      console.log('Processed data:', {
        items: keys.value,
        total: total.value,
        currentPage: currentPage.value,
        pageSize: pageSize.value
      })
    } else {
      keys.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('获取密钥列表失败:', error)
    ElMessage.error(error.response?.data?.detail || '获取密钥列表失败')
    keys.value = []
    total.value = 0
  }
}

// 复制密钥
const handleCopy = async (key) => {
  try {
    await navigator.clipboard.writeText(key)
    ElMessage.success('密钥已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败，请手动复制')
  }
}

// 切换密钥选择状态
const toggleKeySelection = (key) => {
  const index = selectedKeys.value.indexOf(key)
  if (index === -1) {
    selectedKeys.value.push(key)
  } else {
    selectedKeys.value.splice(index, 1)
  }
}

// 合并密钥
const handleMergeKeys = async () => {
  if (selectedKeys.value.length < 2) {
    ElMessage.warning('请至少选择两个密钥')
    return
  }

  try {
    const [target_key, ...source_keys] = selectedKeys.value
    const res = await keyAPI.merge({
      target_key,
      source_keys
    })
    ElMessage.success(`密钥合并成功，合并后的总页数: ${res.data.total_pages}`)
    selectedKeys.value = []
    getKeys()
  } catch (error) {
    console.error('合并密钥失败:', error)
    ElMessage.error(error.response?.data?.detail || '合并密钥失败')
  }
}

// 处理页码变化
const handlePageChange = () => {
  getKeys()
}

// 处理每页条数变化
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  getKeys()
}

onMounted(() => {
  getKeys()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.merge-keys {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style> 