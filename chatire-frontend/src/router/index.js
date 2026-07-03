import Vue from 'vue'
import Router from 'vue-router'
import Chat from '@/components/Chat'
import UserAuth from '@/components/UserAuth'

Vue.use(Router)

const router = new Router({
  routes: [
    // Root redirect — always land on the chat welcome screen
    {
      path: '/',
      redirect: '/chats'
    },
    {
      path: '/chats/:uri?',
      name: 'Chat',
      component: Chat
    },
    {
      path: '/auth',
      name: 'UserAuth',
      component: UserAuth
    },
    // Catch-all — any unknown path goes to chat welcome screen
    {
      path: '*',
      redirect: '/chats'
    }
  ]
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = sessionStorage.getItem('authToken') !== null

  if (isAuthenticated || to.path === '/auth') {
    next()
  } else {
    // Only store the redirect if the destination is a meaningful chat path
    // Avoid storing '/' or '*' which have no mapped component
    const redirect = to.path.startsWith('/chats') ? to.fullPath : null
    if (redirect) {
      next({ path: '/auth', query: { redirect } })
    } else {
      next('/auth')
    }
  }
})

export default router
