import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue')
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/AdminView.vue'),
      children: [
        {
          path: 'keys',
          name: 'admin-keys',
          component: () => import('../views/admin/KeysManagement.vue')
        },
        {
          path: 'files',
          name: 'admin-files',
          component: () => import('../views/admin/FilesManagement.vue')
        },
        {
          path: 'statistics',
          name: 'admin-statistics',
          component: () => import('../views/admin/Statistics.vue')
        }
      ]
    }
  ]
})

export default router 