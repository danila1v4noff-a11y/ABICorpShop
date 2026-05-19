<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 relative">
    <!-- Логотип слева сверху -->
    <img src="/Logo.svg" alt="Логотип" class="absolute top-0 left-4 h-12 w-auto mt-4" />

    <div class="bg-white p-8 rounded-lg shadow-md w-full max-w-sm">
      <h2 class="text-2xl font-bold mb-6 text-center text-gray-800">Авторизация</h2>
      <form @submit.prevent="handleLogin">
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2" for="login"> Логин </label>
          <input
            v-model="login"
            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            id="login"
            type="text"
            placeholder="Введите логин"
            required
          />
        </div>
        <div class="mb-6">
          <label class="block text-gray-700 text-sm font-bold mb-2" for="password"> Пароль </label>
          <input
            v-model="password"
            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
            id="password"
            type="password"
            placeholder="••••••••"
            required
          />
        </div>
        <div class="flex items-center justify-between">
          <button
            class="bg-[#FFA100] hover:bg-[#e09000] text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline w-full transition-colors"
            type="submit"
            :disabled="loading"
          >
            {{ loading ? 'Вход...' : 'Войти' }}
          </button>
        </div>
        <div v-if="error" class="mt-4 text-red-500 text-sm text-center">
          {{ error }}
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const login = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const router = useRouter()

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/v1/auth/login', {
      login: login.value,
      password: password.value,
    })
    const token = response.data.access_token
    localStorage.setItem('access_token', token)
    await fetchUserData(token)
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Ошибка входа'
  } finally {
    loading.value = false
  }
}

const fetchUserData = async (token) => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/v1/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    })
    localStorage.setItem('user', JSON.stringify(response.data))
  } catch (err) {
    console.error('Не удалось получить данные пользователя')
  }
}
</script>
