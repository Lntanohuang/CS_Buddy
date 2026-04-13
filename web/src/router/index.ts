import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { guest: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/auth/RegisterView.vue'),
      meta: { guest: true },
    },
    {
      path: '/app',
      component: () => import('@/components/layout/AppLayout.vue'),
      children: [
        { path: '', redirect: '/app/chat' },
        {
          path: 'chat',
          name: 'chat',
          component: () => import('@/views/chat/ChatView.vue'),
        },
        {
          path: 'path',
          name: 'path',
          component: () => import('@/views/path/PathView.vue'),
        },
        {
          path: 'evaluate',
          name: 'evaluate',
          component: () => import('@/views/evaluate/EvalView.vue'),
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('@/views/profile/ProfileView.vue'),
        },
      ],
    },
    { path: '/', redirect: '/app/chat' },
    { path: '/:pathMatch(.*)*', redirect: '/app/chat' },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.guest && !auth.isLoggedIn) {
    return { name: 'login' }
  }
  if (to.meta.guest && auth.isLoggedIn) {
    return { path: '/app/chat' }
  }
})

export default router
