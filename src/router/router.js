import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '../views/HomePage.vue'
import ProfilePage from '../views/ProfilePage.vue'
import CartPage from '../views/CartPage.vue'
import LoginPage from '../views/LoginPage.vue'
import SharedCartPage from '../views/SharedCartPage.vue'
import AdminOrdersPage from '../views/AdminOrdersPage.vue'
import ProductPage from '../views/ProductPage.vue'
import BlacklistPage from '../views/BlacklistPage.vue'
import RulesPage from '../views/RulesPage.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfilePage,
    meta: { requiresAuth: true },
  },
  {
    path: '/cart',
    name: 'Cart',
    component: CartPage,
    meta: { requiresAuth: true },
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
  },
  {
    path: '/shared/:token',
    name: 'SharedCart',
    component: SharedCartPage,
    meta: { requiresAuth: false },
  },
  {
    path: '/admin/orders',
    name: 'AdminOrders',
    component: AdminOrdersPage,
    meta: { requiresAuth: true, requiresManager: true },
  },
  {
    path: '/product/:id',
    name: 'Product',
    component: ProductPage,
    meta: { requiresAuth: false }, // можно без авторизации, но корзина/избранное требуют токен
  },
  {
    path: '/admin/blacklist',
    name: 'Blacklist',
    component: BlacklistPage,
    meta: { requiresAuth: true, requiresManager: true },
  },
  {
    path: '/rules',
    name: 'Rules',
    component: RulesPage,
    meta: { requiresAuth: false },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Глобальный guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }

  if (to.meta.requiresManager) {
    const userStr = localStorage.getItem('user')
    if (!userStr) {
      next('/login')
      return
    }
    const user = JSON.parse(userStr)
    if (!user.is_manager) {
      next('/') // не менеджер – на главную
      return
    }
  }

  if (to.path === '/login' && token) {
    next('/')
    return
  }

  next()
})

export default router
