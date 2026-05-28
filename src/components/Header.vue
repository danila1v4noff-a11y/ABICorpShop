<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCart } from '../composables/useCart'
import axios from 'axios'

const emit = defineEmits(['toggleDrawer'])
const router = useRouter()

const addresses = ['Дворянская 27АК17', 'Ленина 15АК17', 'Пушкина 10АК17', 'Гагарина 5АК17']
const selectedAddress = ref(addresses[0])
const isDropdownOpen = ref(false)

const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
}
const selectAddress = (address) => {
  selectedAddress.value = address
  isDropdownOpen.value = false
}

const { cartItems, fetchCart, clearCart } = useCart()
const cartCount = computed(() => cartItems.value.reduce((sum, item) => sum + item.quantity, 0))

const user = ref(null)
const isManager = computed(() => user.value?.is_manager === true)
const pendingCount = ref(0)

const loadUser = () => {
  const userStr = localStorage.getItem('user')
  if (userStr) user.value = JSON.parse(userStr)
}

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('user')
  clearCart()
  user.value = null
  router.push('/login')
}

const goToProfile = () => router.push('/profile')
const goToCart = () => router.push('/cart')

// Поиск
const searchQuery = ref('')
let debounceTimer = null
const emitSearch = () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    emit('update:searchQuery', searchQuery.value)
  }, 1000)
}

// Загрузка количества pending заказов для менеджера
const fetchPendingCount = async () => {
  if (!isManager.value) return
  try {
    const token = localStorage.getItem('access_token')
    const resp = await axios.get('http://127.0.0.1:8000/api/v1/admin/orders/pending-count', {
      headers: { Authorization: `Bearer ${token}` },
    })
    pendingCount.value = resp.data.pending_count
  } catch (e) {
    console.error('Ошибка загрузки количества pending заказов')
  }
}

onMounted(() => {
  loadUser()
  fetchCart()
  fetchPendingCount()
})
</script>

<template>
  <header class="bg-[#FF4E4E] px-12 pb-4">
    <div class="flex justify-between items-center">
      <div>
        <img src="/Logo.svg" alt="Logo" class="w-40" />
      </div>
      <div class="flex items-center gap-3">
        <!-- Корзина -->
        <div class="relative mr-5 cursor-pointer" @click="goToCart">
          <img src="/Order.png" alt="Order" class="w-10" />
          <span
            v-if="cartCount > 0"
            class="absolute -top-1 -right-1 bg-white text-[#FF4E4E] text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center"
            >{{ cartCount }}</span
          >
        </div>

        <!-- Колокольчик для менеджера (меняется иконка) -->
        <router-link v-if="isManager" to="/admin/orders" class="relative mr-3 cursor-pointer">
          <img
            :src="pendingCount > 0 ? '/Bell_on.svg' : '/Bell_off.svg'"
            alt="Уведомления"
            class="w-10"
          />
          <span
            v-if="pendingCount > 0"
            class="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center"
            >{{ pendingCount }}</span
          >
        </router-link>
        <router-link to="/rules" class="relative mr-3 cursor-pointer">
          <img src="/Rule.svg" alt="Правила" class="w-10" />
        </router-link>
        <!-- Авторизация -->
        <div v-if="user" class="flex items-center gap-3">
          <span class="text-white font-medium">{{ user.fio }}</span>
          <button @click="logout" class="text-sm text-white/80 hover:text-white">Выйти</button>
        </div>
        <router-link v-else to="/login" class="text-white hover:underline">Войти</router-link>

        <!-- Профиль и адрес -->
        <div class="relative flex items-center gap-2">
          <img src="/Employee.svg" alt="Profile" class="w-10 cursor-pointer" @click="goToProfile" />
          <b
            class="font-medium text-white transition-colors duration-200 cursor-pointer hover:text-gray-300"
            @click="toggleDropdown"
            >{{ selectedAddress }}</b
          >
          <div
            v-if="isDropdownOpen"
            class="absolute left-0 top-full mt-2 w-56 bg-white rounded-lg shadow-lg z-10"
          >
            <ul class="py-1">
              <li
                v-for="address in addresses"
                :key="address"
                @click="selectAddress(address)"
                class="px-4 py-2 hover:bg-gray-100 cursor-pointer text-gray-800"
                :class="{ 'bg-gray-50 font-semibold': address === selectedAddress }"
              >
                {{ address }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <div class="flex justify-center mt-4">
      <div class="flex items-center gap-4">
        <div class="relative w-96 flex-shrink-0">
          <img
            src="/Glass.svg"
            alt="Search"
            class="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 pointer-events-none"
          />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Поиск..."
            @input="emitSearch"
            class="w-full py-2 pl-12 pr-4 bg-white border border-gray-400 rounded-full focus:outline-none focus:ring-1 focus:ring-gray-400"
          />
        </div>
        <button
          @click="emit('toggleDrawer')"
          class="transition-transform duration-100 active:scale-95"
        >
          <img src="/Filters.svg" alt="Filter" class="w-6 h-6" />
        </button>
      </div>
    </div>
  </header>
</template>
