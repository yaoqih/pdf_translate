<template>
  <div class="system-config">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>系统配置</span>
          <el-button type="primary" @click="saveConfigs">保存配置</el-button>
        </div>
      </template>
      
      <el-form :model="configs" label-width="180px">
        <el-form-item 
          v-for="config in configList" 
          :key="config.key" 
          :label="config.description"
        >
          <el-input 
            v-model="configs[config.key]" 
            :placeholder="'请输入' + config.description"
            :type="config.key.includes('KEY') ? 'password' : 'text'"
            :show-password="config.key.includes('KEY')"
          />
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const configs = ref({})
const configList = ref([])

const getConfigs = async () => {
  try {
    const response = await axios.get('/api/status/config')
    if (response.data.code === 200) {
      configList.value = response.data.data.configs
      configs.value = configList.value.reduce((acc, curr) => {
        acc[curr.key] = curr.value
        return acc
      }, {})
    }
  } catch (error) {
    ElMessage.error('获取配置失败')
    console.error('Error fetching configs:', error)
  }
}

const saveConfigs = async () => {
  try {
    const response = await axios.post('/api/status/config', configs.value)
    if (response.data.code === 200) {
      ElMessage.success('保存成功')
    }
  } catch (error) {
    ElMessage.error('保存失败')
    console.error('Error saving configs:', error)
  }
}

const initConfigs = async () => {
  try {
    await axios.get('/api/status/config/init')
    await getConfigs()
  } catch (error) {
    console.error('Error initializing configs:', error)
  }
}

onMounted(async () => {
  await initConfigs()
})
</script>

<style scoped>
.system-config {
  padding: 20px;
}

.config-card {
  max-width: 800px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style> 