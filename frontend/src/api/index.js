import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 50000
})

// 响应拦截器
api.interceptors.response.use(
  response => {
    const { data } = response
    if (data.code === 200) {
      return data
    }
    ElMessage.error(data.message || '请求失败')
    return Promise.reject(new Error(data.message || '请求失败'))
  },
  error => {
    console.error('API Error:', error.response?.data || error)
    ElMessage.error(error.response?.data?.detail || '网络错误')
    return Promise.reject(error)
  }
)

// PDF相关接口
export const pdfAPI = {
  upload: (file, source_language, key, translate_pages) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('source_language', source_language)
    formData.append('key', key)
    if (translate_pages) {
      formData.append('translate_pages', translate_pages)
    }
    return api.post('/pdf/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  getPageCount: (formData) => {
    return api.post('/pdf/page-count', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  download: (fileId, type = 'original', key = null) => {
    const url = new URL(`/api/pdf/download/${fileId}`, window.location.origin)
    url.searchParams.append('type', type)
    if (key) {
      url.searchParams.append('key', key)
    }
    window.open(url.toString(), '_blank')
  },
  list: (params) => api.get('/pdf/list', { params }),
  delete: (fileId, key = null) => {
    const url = `/pdf/${fileId}`
    return api.delete(key ? `${url}?key=${key}` : url)
  }
}

// 密钥相关接口
export const keyAPI = {
  generate: (data) => api.post('/key/generate', data),
  getInfo: (key) => api.get(`/key/info/${key}`),
  list: (params) => api.get('/key/list', { params }),
  merge: (data) => api.post('/key/merge', data)
}

// 状态相关接口
export const statusAPI = {
  getStatistics: () => api.get('/status/statistics')
} 