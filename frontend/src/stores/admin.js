import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAdminStore = defineStore('admin', () => {
  const isAuthenticated = ref(false)
  const token = ref(localStorage.getItem('admin_token') || '')

  const login = async (credentials) => {
    // 这里应该调用后端API进行验证
    // 目前使用模拟数据，实际使用时请替换为真实的API调用
    if (credentials.username === 'admin' && credentials.password === 'admin123') {
      const mockToken = 'mock_admin_token'
      token.value = mockToken
      localStorage.setItem('admin_token', mockToken)
      isAuthenticated.value = true
    } else {
      throw new Error('用户名或密码错误')
    }
  }

  const logout = () => {
    token.value = ''
    isAuthenticated.value = false
    localStorage.removeItem('admin_token')
  }

  const checkAuth = () => {
    const storedToken = localStorage.getItem('admin_token')
    if (storedToken) {
      token.value = storedToken
      isAuthenticated.value = true
    }
  }

  return {
    isAuthenticated,
    token,
    login,
    logout,
    checkAuth
  }
}) 