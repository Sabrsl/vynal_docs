import { createRouter, createWebHistory } from 'vue-router'
import DocumentsView from '@/views/DocumentsView.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue')
  },
  {
    path: '/documents',
    name: 'Documents',
    component: DocumentsView
  },
  {
    path: '/templates',
    name: 'Templates',
    component: () => import('@/views/TemplatesView.vue')
  },
  {
    path: '/categories',
    name: 'Categories',
    component: () => import('@/views/CategoriesView.vue')
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('@/views/UsersView.vue')
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/SettingsView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  linkActiveClass: 'active'
})

export default router 