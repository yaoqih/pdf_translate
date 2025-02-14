<template>
  <div class="files-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>文件管理</h3>
          <div class="header-actions">
            <el-input
              v-model="searchKey"
              placeholder="输入密钥搜索"
              clearable
              @clear="handleSearch"
              style="width: 200px; margin-right: 10px;"
            >
              <template #append>
                <el-button @click="handleSearch">
                  <el-icon><search /></el-icon>
                </el-button>
              </template>
            </el-input>
            
            <el-select
              v-model="fileStatus"
              placeholder="文件状态"
              clearable
              @change="handleSearch"
              style="width: 120px; margin-right: 10px;"
            >
              <el-option label="待处理" value="pending" />
              <el-option label="处理中" value="processing" />
              <el-option label="已完成" value="completed" />
              <el-option label="失败" value="failed" />
            </el-select>
            
            <el-select
              v-model="orderStatus"
              placeholder="订单状态"
              clearable
              @change="handleSearch"
              style="width: 120px;"
            >
              <el-option label="未支付" value="unpaid" />
              <el-option label="已支付" value="paid" />
              <el-option label="已取消" value="cancelled" />
              <el-option label="已退款" value="refunded" />
            </el-select>
          </div>
        </div>
      </template>
      
      <!-- 文件列表 -->
      <el-table :data="files" style="width: 100%">
        <el-table-column prop="filename" label="文件名" />
        <el-table-column prop="page_count" label="页数" width="80" />
        <el-table-column prop="file_status" label="文件状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getFileStatusType(row.file_status)">
              {{ getFileStatusText(row.file_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="order_status" label="订单状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getOrderStatusType(row.order_status)">
              {{ getOrderStatusText(row.order_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300">
          <template #default="{ row }">
            <el-button-group>
              <el-button
                size="small"
                @click="handleDownload(row.id)"
              >
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
              <el-button
                size="small"
                type="danger"
                @click="handleDelete(row.id)"
              >
                删除
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { pdfAPI } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const files = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const searchKey = ref('')
const fileStatus = ref('')
const orderStatus = ref('')

// 获取文件列表
const getFiles = async () => {
  try {
    const res = await pdfAPI.list({
      page: currentPage.value,
      size: pageSize.value,
      key: searchKey.value || undefined,
      file_status: fileStatus.value || undefined,
      order_status: orderStatus.value || undefined,
      is_admin: true
    })
    
    // 确保数据存在
    if (res?.data) {
      files.value = res.data.items || []
      total.value = res.data.total || 0
      
      console.log('Processed data:', {
        items: files.value,
        total: total.value,
        currentPage: currentPage.value,
        pageSize: pageSize.value
      })
    } else {
      files.value = []
      total.value = 0
    }
  } catch (error) {
    console.error('获取文件列表失败:', error)
    ElMessage.error('获取文件列表失败')
    files.value = []
    total.value = 0
  }
}

// 处理搜索
const handleSearch = () => {
  currentPage.value = 1
  getFiles()
}

// 处理文件下载
const handleDownload = (fileId, type = 'original') => {
  pdfAPI.download(fileId, type)
}

// 处理文件删除
const handleDelete = async (fileId) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个文件吗？此操作不可恢复。',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await pdfAPI.delete(fileId)
    ElMessage.success('文件删除成功')
    getFiles()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除文件失败:', error)
    }
  }
}

// 处理页码变化
const handlePageChange = () => {
  getFiles()
}

// 处理每页条数变化
const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  getFiles()
}

// 获取文件状态类型
const getFileStatusType = (status) => {
  const types = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return types[status] || 'info'
}

// 获取文件状态文本
const getFileStatusText = (status) => {
  const texts = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    failed: '失败'
  }
  return texts[status] || status
}

// 获取订单状态类型
const getOrderStatusType = (status) => {
  const types = {
    unpaid: 'info',
    paid: 'success',
    cancelled: 'danger',
    refunded: 'warning'
  }
  return types[status] || 'info'
}

// 获取订单状态文本
const getOrderStatusText = (status) => {
  const texts = {
    unpaid: '未支付',
    paid: '已支付',
    cancelled: '已取消',
    refunded: '已退款'
  }
  return texts[status] || status
}

onMounted(() => {
  getFiles()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style> 