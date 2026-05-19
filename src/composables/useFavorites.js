import { ref } from 'vue'
import axios from 'axios'

const API_BASE = 'http://127.0.0.1:8000/api/v1'
const favorites = ref([])
const loading = ref(false)
const error = ref(null)

const getToken = () => localStorage.getItem('access_token')

const fetchFavorites = async () => {
  const token = getToken()
  if (!token) {
    favorites.value = []
    return
  }
  loading.value = true
  error.value = null
  try {
    const response = await axios.get(`${API_BASE}/favorites/`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    favorites.value = response.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка загрузки избранного'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const addFavorite = async (productId) => {
  const token = getToken()
  if (!token) throw new Error('Не авторизован')
  loading.value = true
  error.value = null
  try {
    await axios.post(
      `${API_BASE}/favorites/`,
      { product_id: productId },
      { headers: { Authorization: `Bearer ${token}` } },
    )
    await fetchFavorites()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка добавления в избранное'
    throw err
  } finally {
    loading.value = false
  }
}

const removeFavorite = async (productId) => {
  const token = getToken()
  if (!token) throw new Error('Не авторизован')
  loading.value = true
  error.value = null
  try {
    await axios.delete(`${API_BASE}/favorites/${productId}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    await fetchFavorites()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка удаления из избранного'
    throw err
  } finally {
    loading.value = false
  }
}

const clearFavorites = () => {
  favorites.value = []
}

export function useFavorites() {
  return {
    favorites,
    loading,
    error,
    fetchFavorites,
    addFavorite,
    removeFavorite,
    clearFavorites,
  }
}
