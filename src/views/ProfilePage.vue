<template>
  <div class="relative min-h-screen bg-gray-100 p-8">
    <div class="absolute top-8 left-8 z-10">
      <img
        src="/ArrowLeft.svg"
        alt="Назад"
        class="w-8 h-8 cursor-pointer opacity-50 hover:opacity-100 transition-opacity duration-200"
        @click="goToHome"
      />
    </div>

    <div class="max-w-4xl mx-auto bg-white rounded-xl shadow-lg overflow-hidden">
      <div class="p-6 border-b border-gray-200">
        <div class="flex items-center gap-4">
          <img src="/Employee.svg" alt="Avatar" class="w-16 h-16 bg-gray-100 rounded-full p-2" />
          <h1 class="text-2xl font-bold text-gray-800">{{ userName }}</h1>
        </div>
      </div>
      <div class="p-6">
        <!-- Избранное -->
        <div class="mb-8">
          <h2 class="text-xl font-semibold mb-3 text-gray-800">Избранное (В рассылке)</h2>
          <div v-if="favorites.length === 0" class="text-gray-500 italic">Пусто</div>
          <div v-else class="grid grid-cols-2 gap-4">
            <div
              v-for="fav in favorites"
              :key="fav.favorite_id"
              class="flex items-center gap-4 border rounded-lg p-3"
            >
              <img :src="fav.image_url" alt="product" class="w-16 h-16 object-contain rounded" />
              <div class="flex-1">
                <p class="font-semibold">{{ fav.product_name }}</p>
                <p class="text-gray-600">{{ fav.price }} руб.</p>
              </div>
              <button
                @click="removeFromFavorites(fav.product_id)"
                class="text-red-500 hover:text-red-700"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-5 w-5"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fill-rule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clip-rule="evenodd"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Последние заказы -->
        <div>
          <h2 class="text-xl font-semibold mb-3 text-gray-800">Последние заказы</h2>
          <div v-if="orders.length === 0" class="text-gray-500 italic">Пусто</div>
          <div v-else class="space-y-4">
            <!-- Показываем первые 2 или все, в зависимости от showAll -->
            <div
              v-for="order in displayedOrders"
              :key="order.order_id"
              class="border rounded-lg p-3"
            >
              <div class="flex justify-between">
                <span class="font-semibold">Заказ №{{ order.order_id }}</span>
                <span class="text-sm text-gray-600">{{ formatDate(order.created_at) }}</span>
              </div>
              <p class="text-sm">Статус: {{ statusText(order.status) }}</p>
              <p class="text-sm">Сумма: {{ order.total_amount }} руб.</p>
              <div v-if="order.items.length" class="mt-2">
                <p class="text-xs text-gray-500">Товары:</p>
                <div v-for="item in order.items" :key="item.product_id" class="flex gap-2 text-sm">
                  <span>{{ item.product_name }} × {{ item.quantity }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Кнопка "Больше" / "Скрыть" -->
          <div v-if="orders.length > 2" class="flex justify-center mt-4">
            <button
              @click="toggleShowAll"
              class="focus:outline-none transition-transform duration-200 hover:scale-110"
            >
              <img
                :src="showAll ? '/More_on.svg' : '/More_off.svg'"
                alt="Показать все заказы"
                class="w-30 h-30"
              />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useFavorites } from '../composables/useFavorites'

const router = useRouter()
const userName = ref('Сотрудник')
const { favorites, fetchFavorites, removeFavorite } = useFavorites()

// Заказы
const orders = ref([])
const showAll = ref(false) // показать все или только 2

// Вычисляем, какие заказы показывать
const displayedOrders = computed(() => {
  if (showAll.value) return orders.value
  return orders.value.slice(0, 2)
})

const statusText = (status) => {
  const map = {
    pending: 'Ожидает',
    accepted: 'Принят',
    rejected: 'Отклонён',
    in_progress: 'В работе',
    ready: 'Готово',
    completed: 'Завершён',
    cancelled: 'Отменён',
  }
  return map[status] || status
}

const formatDate = (iso) => new Date(iso).toLocaleDateString('ru-RU')

const goToHome = () => router.push('/')

const removeFromFavorites = async (productId) => {
  try {
    await removeFavorite(productId)
  } catch (err) {
    alert('Не удалось удалить из избранного')
  }
}

// Переключение режима показа заказов
const toggleShowAll = () => {
  showAll.value = !showAll.value
}

onMounted(async () => {
  // Загрузка данных пользователя
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      const user = JSON.parse(userStr)
      userName.value = user.fio || 'Сотрудник'
    } catch (e) {
      console.error('Ошибка чтения пользователя')
    }
  } else {
    const token = localStorage.getItem('access_token')
    if (token) {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/v1/auth/me', {
          headers: { Authorization: `Bearer ${token}` },
        })
        localStorage.setItem('user', JSON.stringify(response.data))
        userName.value = response.data.fio
      } catch (err) {
        router.push('/login')
      }
    } else {
      router.push('/login')
    }
  }

  // Загрузка избранного
  await fetchFavorites()

  // Загрузка заказов
  const token = localStorage.getItem('access_token')
  if (token) {
    try {
      const resp = await axios.get('http://127.0.0.1:8000/api/v1/orders/', {
        headers: { Authorization: `Bearer ${token}` },
      })
      orders.value = resp.data
    } catch (e) {
      console.error('Ошибка загрузки заказов')
    }
  }
})
</script>
