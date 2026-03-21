import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Projects',
    component: () => import('../views/ProjectList.vue'),
  },
  {
    path: '/project/:id',
    name: 'ProjectDetail',
    component: () => import('../views/ProjectDetail.vue'),
  },
  {
    path: '/project/:id/eval/:objId',
    name: 'CheckRecords',
    component: () => import('../views/CheckRecords.vue'),
  },
  {
    path: '/project/:id/issues',
    name: 'Issues',
    component: () => import('../views/IssueList.vue'),
  },
  {
    path: '/project/:id/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
  },
  {
    path: '/question-bank',
    name: 'QuestionBank',
    component: () => import('../views/QuestionBank.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
