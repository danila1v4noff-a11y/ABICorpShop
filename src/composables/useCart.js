import { ref } from 'vue'
import axios from 'axios'

const API_BASE = 'http://127.0.0.1:8000/api/v1'

// Глобальное реактивное состояние корзины
const cartItems = ref([])
const totalSum = ref(0)
const totalWeight = ref(0)
const loading = ref(false)
const error = ref(null)

// Получить токен из localStorage
const getToken = () => localStorage.getItem('access_token')

// Загрузить корзину с сервера
const fetchCart = async () => {
  const token = getToken()
  if (!token) {
    cartItems.value = []
    totalSum.value = 0
    totalWeight.value = 0
    return
  }

  loading.value = true
  error.value = null
  try {
    const response = await axios.get(`${API_BASE}/cart/`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    cartItems.value = response.data.items
    totalSum.value = response.data.total_sum
    totalWeight.value = response.data.total_weight
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка загрузки корзины'
    console.error('fetchCart error:', err)
  } finally {
    loading.value = false
  }
}

// Добавить товар в корзину (или увеличить количество)
const addToCart = async (productId, quantity = 1) => {
  const token = getToken()
  if (!token) throw new Error('Не авторизован')

  loading.value = true
  error.value = null
  try {
    await axios.post(
      `${API_BASE}/cart/add`,
      { product_id: productId, quantity },
      { headers: { Authorization: `Bearer ${token}` } },
    )
    await fetchCart() // обновляем состояние после добавления
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка добавления в корзину'
    throw err
  } finally {
    loading.value = false
  }
}

// Обновить количество товара в корзине
const updateCartItem = async (cartItemId, quantity) => {
  const token = getToken()
  if (!token) throw new Error('Не авторизован')

  loading.value = true
  error.value = null
  try {
    if (quantity <= 0) {
      await axios.delete(`${API_BASE}/cart/${cartItemId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
    } else {
      await axios.put(
        `${API_BASE}/cart/${cartItemId}`,
        { quantity },
        { headers: { Authorization: `Bearer ${token}` } },
      )
    }
    await fetchCart()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка обновления корзины'
    throw err
  } finally {
    loading.value = false
  }
}

// Удалить товар из корзины
const removeFromCart = async (cartItemId) => {
  const token = getToken()
  if (!token) throw new Error('Не авторизован')

  loading.value = true
  error.value = null
  try {
    await axios.delete(`${API_BASE}/cart/${cartItemId}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    await fetchCart()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка удаления из корзины'
    throw err
  } finally {
    loading.value = false
  }
}

// Очистить состояние корзины (при выходе из аккаунта)
const clearCart = () => {
  cartItems.value = []
  totalSum.value = 0
  totalWeight.value = 0
  error.value = null
}

export function useCart() {
  return {
    cartItems,
    totalSum,
    totalWeight,
    loading,
    error,
    fetchCart,
    addToCart,
    updateCartItem,
    removeFromCart,
    clearCart,
  }
}
