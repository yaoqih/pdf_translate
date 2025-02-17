import { createRouter, createWebHistory } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import AdminView from '../views/AdminView.vue'
import Statistics from '../views/admin/Statistics.vue'
import KeysManagement from '../views/admin/KeysManagement.vue'
import FilesManagement from '../views/admin/FilesManagement.vue'
import SystemConfig from '../views/admin/SystemConfig.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue')
    },
    {
      path: '/admin/login',
      name: 'admin-login',
      component: () => import('../views/admin/Login.vue')
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView,
      redirect: '/admin/keys',
      meta: { requiresAuth: true },
      children: [
        {
          path: 'keys',
          name: 'admin-keys',
          component: KeysManagement,
          meta: { requiresAuth: true }
        },
        {
          path: 'files',
          name: 'admin-files',
          component: FilesManagement,
          meta: { requiresAuth: true }
        },
        {
          path: 'statistics',
          name: 'admin-statistics',
          component: Statistics,
          meta: { requiresAuth: true }
        },
        {
          path: 'config',
          name: 'config',
          component: SystemConfig
        }
      ]
    }
  ]
})

// 全局路由守卫
router.beforeEach((to, from, next) => {
  const adminStore = useAdminStore()
  
  // 检查是否需要认证
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 检查是否已登录
    if (!adminStore.isAuthenticated) {
      // 如果没有登录，重定向到登录页面
      next({
        path: '/admin/login',
        query: { redirect: to.fullPath }
      })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router 