<template>
  <div class="min-h-screen bg-gray-100 p-8 relative">
    <img
      src="/Logo.svg"
      alt="Логотип"
      class="absolute top-0 left-4 h-12 w-auto mt-4 cursor-pointer"
      @click="goToHome"
    />
    <div class="max-w-6xl mx-auto">
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <h1 class="text-2xl font-bold">Общая корзина</h1>
        <p v-if="cart" class="text-gray-600 mt-2">Создал: {{ cart.owner_name }}</p>
      </div>

      <div class="flex items-center gap-4 mb-6">
        <div class="relative flex-1">
          <img
            src="/Glass.svg"
            class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 pointer-events-none"
          />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Поиск..."
            class="w-full py-2 pl-12 pr-4 bg-white border border-gray-400 rounded-full focus:outline-none focus:ring-1 focus:ring-gray-400"
            @input="debouncedSearch"
          />
        </div>
        <button
          @click="isDrawerOpen = true"
          class="transition-transform duration-100 active:scale-95"
        >
          <img src="/Filters.svg" alt="Filter" class="w-6 h-6" />
        </button>
      </div>

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
              <p class="text-sm text-gray-600">
                <template v-if="item.discount_price">
                  <span class="line-through text-red-400 mr-2">{{ item.price }} руб.</span>
                  <span class="font-semibold text-gray-800">{{ item.discount_price }} руб.</span>
                </template>
                <template v-else> {{ item.price }} руб. </template>
                × {{ item.quantity }}
              </p>
            </div>

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
              <button @click="deleteItem(item.id)" class="ml-2 text-red-500 hover:text-red-700">
                Удалить
              </button>
            </div>
            <div v-else class="text-gray-500">× {{ item.quantity }}</div>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">Добавить товар</h2>
        <div v-if="filteredProducts.length" class="grid grid-cols-4 gap-4">
          <div
            v-for="product in filteredProducts"
            :key="product.batch_id"
            class="border rounded-lg p-3 flex flex-col items-center cursor-pointer hover:shadow transition"
            @click="addProduct(product.product_id, product.batch_id)"
          >
            <img :src="product.image_url" alt="product" class="w-full h-32 object-contain mb-2" />
            <p class="font-medium text-center text-sm">{{ product.product_name }}</p>
            <p class="text-gray-600 text-sm">
              <template v-if="product.has_expiring">
                <span class="line-through text-red-400 mr-1">{{ product.price }} руб.</span>
                <span class="font-semibold text-gray-800"
                  >{{ Math.round(product.price * 0.6) }} руб.</span
                >
              </template>
              <template v-else> {{ product.price }} руб. </template>
            </p>
            <p class="text-xs text-gray-500">В наличии: {{ product.quantity }} шт.</p>
            <p v-if="product.quantity === 0" class="text-red-500 text-xs mt-1">
              Товара больше добавить нельзя
            </p>
          </div>
        </div>
        <div v-else class="text-gray-500">Нет товаров для добавления</div>
      </div>
    </div>

    <div v-if="isDrawerOpen" class="fixed inset-0 z-50 flex">
      <div class="bg-black/50 w-full h-full" @click="isDrawerOpen = false"></div>
      <div class="bg-white w-80 h-full shadow-lg p-6 overflow-y-auto absolute right-0">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-lg font-semibold">Категории</h3>
          <button @click="isDrawerOpen = false" class="text-gray-500 hover:text-gray-700">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
        <ul class="space-y-2">
          <li
            @click="selectCategory(null)"
            class="px-3 py-2 rounded cursor-pointer hover:bg-gray-100"
            :class="{ 'bg-orange-100 font-medium': selectedCategory === null }"
          >
            Все категории
          </li>
          <li
            v-for="cat in categories"
            :key="cat.category_id"
            @click="selectCategory(cat.name)"
            class="px-3 py-2 rounded cursor-pointer hover:bg-gray-100"
            :class="{ 'bg-orange-100 font-medium': selectedCategory === cat.name }"
          >
            {{ cat.name }}
          </li>
        </ul>
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
const categories = ref([])
const currentUserId = ref(null)
const searchQuery = ref('')
const selectedCategory = ref(null)
const isDrawerOpen = ref(false)
let debounceTimer = null

const debouncedSearch = () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {}, 300)
}
const selectCategory = (cat) => {
  selectedCategory.value = cat
  isDrawerOpen.value = false
}
const isOwner = computed(() =>
  cart.value && currentUserId.value ? cart.value.owner_id === currentUserId.value : false,
)
const isAuthorOf = (item) => currentUserId.value === item.added_by_user_id
const goToHome = () => router.push('/')

const loadCart = async () => {
  try {
    const resp = await axios.get(`http://127.0.0.1:8000/api/v1/shared-cart/${token}`)
    cart.value = resp.data
  } catch {
    alert('Общая корзина не найдена или истекла')
    router.push('/')
  }
}
const loadProducts = async () => {
  try {
    const resp = await axios.get('http://127.0.0.1:8000/api/v1/products/')
    products.value = resp.data
  } catch {}
}
const loadCategories = async () => {
  try {
    const resp = await axios.get('http://127.0.0.1:8000/api/v1/categories/')
    categories.value = resp.data
  } catch {}
}

const filteredProducts = computed(() =>
  products.value.filter((p) => {
    const matchSearch = searchQuery.value
      ? p.product_name.toLowerCase().includes(searchQuery.value.toLowerCase())
      : true
    const matchCat = selectedCategory.value ? p.category_name === selectedCategory.value : true
    return matchSearch && matchCat
  }),
)

const getAuthHeaders = () => {
  const accessToken = localStorage.getItem('access_token')
  if (!accessToken) {
    alert('Необходимо авторизоваться')
    router.push('/login')
    return null
  }
  return { Authorization: `Bearer ${accessToken}` }
}

const addProduct = async (productId, batchId) => {
  const headers = getAuthHeaders()
  if (!headers) return
  try {
    await axios.post(
      `http://127.0.0.1:8000/api/v1/shared-cart/${token}/add`,
      { product_id: productId, batch_id: batchId, quantity: 1 },
      { headers },
    )
    await loadCart()
  } catch (err) {
    alert(err.response?.data?.detail || 'Ошибка при добавлении товара')
  }
}

// НОВЫЕ МЕТОДЫ
const increaseQuantity = async (item) => {
  const headers = getAuthHeaders()
  if (!headers) return
  try {
    // Проверим, не превысит ли новое количество лимиты
    if (item.quantity >= 15) {
      alert('Максимальное количество товара — 15 шт.')
      return
    }
    // Можно было бы проверить остаток партии, но в общей корзине нет batch_id у элемента
    await axios.put(
      `http://127.0.0.1:8000/api/v1/shared-cart/${token}/item/${item.id}`,
      { quantity: item.quantity + 1 },
      { headers },
    )
    await loadCart()
  } catch (err) {
    alert(err.response?.data?.detail || 'Ошибка изменения количества')
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
    alert(err.response?.data?.detail || 'Ошибка изменения количества')
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
    alert(err.response?.data?.detail || 'Ошибка удаления')
  }
}

onMounted(async () => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    const user = JSON.parse(userStr)
    currentUserId.value = user.employee_id
  }
  await Promise.all([loadCart(), loadProducts(), loadCategories()])
})
</script>
