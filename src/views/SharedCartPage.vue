<template>
  <div class="min-h-screen bg-gray-100 p-8 relative">
    <!-- Логотип -->
    <img
      src="/Logo.svg"
      alt="Логотип"
      class="absolute top-0 left-4 h-12 w-auto mt-4 cursor-pointer"
      @click="goToHome"
    />

    <div class="max-w-4xl mx-auto">
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <h1 class="text-2xl font-bold">Общая корзина</h1>
        <p v-if="cart" class="text-gray-600 mt-2">Создал: {{ cart.owner_name }}</p>
      </div>

      <!-- Товары -->
      <div v-if="cart && cart.items.length" class="bg-white rounded-lg shadow p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">Добавленные товары</h2>
        <div class="space-y-4">
          <div
            v-for="item in cart.items"
            :key="item.id"
            class="flex items-center gap-4 border-b pb-4"
          >
            <img :src="item.image_url" alt="product" class="w-16 h-16 object-contain rounded" />
            <div class="flex-1">
              <p class="font-semibold">{{ item.product_name }}</p>
              <p class="text-sm text-gray-600">Добавил: {{ item.added_by_user_name }}</p>
              <p class="text-sm text-gray-600">{{ item.price }} руб. × {{ item.quantity }}</p>
            </div>

            <!-- Кнопки для автора позиции (не владельца) -->
            <div v-if="isAuthorOf(item) && !isOwner" class="flex items-center gap-2">
              <button
                @click="decreaseQuantity(item)"
                class="w-8 h-8 rounded border hover:bg-gray-100 flex items-center justify-center"
              >
                <img src="/Minus_Main.svg" alt="-" class="w-4 h-4" />
              </button>
              <span class="w-8 text-center">{{ item.quantity }}</span>
              <button
                @click="increaseQuantity(item)"
                class="w-8 h-8 rounded border hover:bg-gray-100 flex items-center justify-center"
              >
                <img src="/Plus_Main.svg" alt="+" class="w-4 h-4" />
              </button>
              <!-- Кнопка "Удалить" для автора -->
              <button @click="deleteItem(item.id)" class="ml-2 text-red-500 hover:text-red-700">
                Удалить
              </button>
            </div>

            <!-- Владелец видит только просмотр (управление через его корзину) -->
            <div v-else class="text-gray-500">× {{ item.quantity }}</div>
          </div>
        </div>
      </div>

      <!-- Блок добавления товаров (для всех) -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">Добавить товар</h2>
        <div v-if="products.length" class="grid grid-cols-2 gap-4">
          <div
            v-for="product in products"
            :key="product.product_id"
            class="border rounded-lg p-3 flex items-center gap-3"
          >
            <img :src="product.image_url" alt="product" class="w-12 h-12 object-contain rounded" />
            <div class="flex-1">
              <p class="font-medium">{{ product.name }}</p>
              <p class="text-gray-600">{{ product.price }} руб.</p>
            </div>
            <button
              @click="addProduct(product.product_id)"
              class="bg-[#FFA100] hover:bg-[#e09000] text-white px-3 py-1 rounded transition-colors"
            >
              Добавить
            </button>
          </div>
        </div>
        <div v-else class="text-gray-500">Загрузка товаров...</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const token = route.params.token

const cart = ref(null)
const products = ref([])
const currentUserId = ref(null)

const isOwner = computed(() => {
  if (!cart.value || !currentUserId.value) return false
  return cart.value.owner_id === currentUserId.value
})

// Является ли текущий пользователь автором данного элемента
const isAuthorOf = (item) => {
  return currentUserId.value === item.added_by_user_id
}

const goToHome = () => router.push('/')

const loadCart = async () => {
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/v1/shared-cart/${token}`)
    cart.value = response.data
  } catch (err) {
    alert('Общая корзина не найдена или истекла')
    router.push('/')
  }
}

const loadProducts = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/v1/products/')
    products.value = response.data
  } catch (err) {
    console.error('Ошибка загрузки товаров')
  }
}

const getAuthHeaders = () => {
  const accessToken = localStorage.getItem('access_token')
  if (!accessToken) {
    alert('Необходимо авторизоваться')
    router.push('/login')
    return null
  }
  return { Authorization: `Bearer ${accessToken}` }
}

const addProduct = async (productId) => {
  const headers = getAuthHeaders()
  if (!headers) return
  try {
    await axios.post(
      `http://127.0.0.1:8000/api/v1/shared-cart/${token}/add`,
      { product_id: productId, quantity: 1 },
      { headers },
    )
    await loadCart()
  } catch (err) {
    console.error(err)
    if (err.response?.status === 401) {
      alert('Ошибка авторизации. Попробуйте выйти и заново войти.')
    } else {
      alert('Ошибка при добавлении товара')
    }
  }
}

const increaseQuantity = async (item) => {
  const headers = getAuthHeaders()
  if (!headers) return
  try {
    await axios.put(
      `http://127.0.0.1:8000/api/v1/shared-cart/${token}/item/${item.id}`,
      { quantity: item.quantity + 1 },
      { headers },
    )
    await loadCart()
  } catch (err) {
    alert('Ошибка изменения количества')
  }
}

const decreaseQuantity = async (item) => {
  const headers = getAuthHeaders()
  if (!headers) return
  try {
    if (item.quantity <= 1) {
      await axios.delete(`http://127.0.0.1:8000/api/v1/shared-cart/${token}/item/${item.id}`, {
        headers,
      })
    } else {
      await axios.put(
        `http://127.0.0.1:8000/api/v1/shared-cart/${token}/item/${item.id}`,
        { quantity: item.quantity - 1 },
        { headers },
      )
    }
    await loadCart()
  } catch (err) {
    alert('Ошибка изменения количества')
  }
}

const deleteItem = async (itemId) => {
  const headers = getAuthHeaders()
  if (!headers) return
  try {
    await axios.delete(`http://127.0.0.1:8000/api/v1/shared-cart/${token}/item/${itemId}`, {
      headers,
    })
    await loadCart()
  } catch (err) {
    alert('Ошибка удаления')
  }
}

onMounted(async () => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    const user = JSON.parse(userStr)
    currentUserId.value = user.employee_id
  }
  await loadCart()
  await loadProducts()
})
</script>
