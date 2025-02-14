<template>
  <div class="statistics">
    <el-row :gutter="20">
      <!-- 文件状态统计 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <h3>文件状态统计</h3>
              <el-button type="primary" @click="getStatistics">
                刷新
              </el-button>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="12" v-for="(count, status) in stats.file_status" :key="status">
              <el-card shadow="hover" class="status-card">
                <div class="status-info">
                  <el-tag :type="getFileStatusType(status)" size="large">
                    {{ getFileStatusText(status) }}
                  </el-tag>
                  <div class="count">{{ count }}</div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
      
      <!-- 订单状态统计 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <h3>订单状态统计</h3>
              <el-button type="primary" @click="getStatistics">
                刷新
              </el-button>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="12" v-for="(count, status) in stats.order_status" :key="status">
              <el-card shadow="hover" class="status-card">
                <div class="status-info">
                  <el-tag :type="getOrderStatusType(status)" size="large">
                    {{ getOrderStatusText(status) }}
                  </el-tag>
                  <div class="count">{{ count }}</div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { statusAPI } from '@/api'
import { ElMessage } from 'element-plus'

const stats = ref({
  file_status: {},
  order_status: {}
})

// 获取统计数据
const getStatistics = async () => {
  try {
    const res = await statusAPI.getStatistics()
    if (res.data) {
      stats.value = res.data
    } else {
      console.error('Invalid statistics data:', res)
      ElMessage.error('获取统计数据失败')
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error(error.response?.data?.detail || '获取统计数据失败')
  }
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
  getStatistics()
})
</script>

<style scoped>
.statistics {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-card {
  margin-bottom: 20px;
}

.status-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.count {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}
</style> 