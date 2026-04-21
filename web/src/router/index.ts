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
      path: '/welcome',
      name: 'welcome',
      component: () => import('@/views/auth/WelcomeView.vue'),
    },
    {
      path: '/app',
      component: () => import('@/layouts/BasicLayout.vue'),
      children: [
        { path: '', redirect: '/app/chat' },
        { path: 'chat', name: 'chat', component: () => import('@/views/chat/ChatView.vue') },
        { path: 'path', name: 'path', component: () => import('@/views/path/PathView.vue') },
        { path: 'evaluate', name: 'evaluate', component: () => import('@/views/evaluate/EvalView.vue') },
        { path: 'profile', name: 'profile', component: () => import('@/views/profile/ProfileView.vue') },
        { path: 'notifications', name: 'notifications', component: () => import('@/views/notification/NotificationView.vue') },
      ],
    },
    { path: '/', redirect: '/login' },
    { path: '/:pathMatch(.*)*', redirect: '/login' },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  const currentUser = auth.user
  const isLoggedIn = !!currentUser
  const hasProfile = currentUser?.has_profile === true
  const isGuestPage = to.meta.guest === true
  const isWelcomePage = to.name === 'welcome'
  const isProfileRefreshFlow = isWelcomePage && to.query.mode === 'refresh-profile'

  // Unauthenticated users can only access guest routes.
  if (!isLoggedIn) {
    return isGuestPage ? true : { path: '/login' }
  }

  // Authenticated users without a profile must stay in the welcome flow.
  if (!hasProfile) {
    return isWelcomePage ? true : { path: '/welcome' }
  }

  // Authenticated users with a complete profile should be in app routes.
  if (isGuestPage || (isWelcomePage && !isProfileRefreshFlow)) {
    return { path: '/app/chat' }
  }

  return true
})

export default router
