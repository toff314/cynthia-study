import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/schedule',
    name: 'Schedule',
    component: () => import('@/views/Schedule.vue')
  },
  {
    path: '/study',
    name: 'Study',
    component: () => import('@/views/Study.vue')
  },
  {
    path: '/quiz',
    name: 'Quiz',
    component: () => import('@/views/QuizGenerator.vue')
  },
  {
    path: '/achievement',
    name: 'Achievement',
    component: () => import('@/views/AchievementWall.vue')
  },
  {
    path: '/games',
    name: 'Games',
    component: () => import('@/views/PuzzleGames.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
