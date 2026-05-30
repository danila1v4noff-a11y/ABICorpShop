<template>
  <div class="min-h-screen bg-gray-100">
    <transition name="fade" appear>
      <img
        src="/COLLAGEICON.svg"
        alt="коллаж слева"
        class="fixed top-0 left-0 h-full w-auto min-w-[120px] object-cover opacity-80 pointer-events-none z-0"
        style="filter: drop-shadow(4px 4px 12px rgba(0, 0, 0, 0.25))"
      />
    </transition>
    <transition name="fade" appear>
      <img
        src="/COLLAGEICON.svg"
        alt="коллаж справа"
        class="fixed top-0 right-0 h-full w-auto min-w-[120px] object-cover opacity-80 pointer-events-none z-0"
        style="transform: scaleX(-1); filter: drop-shadow(-4px 4px 12px rgba(0, 0, 0, 0.25))"
      />
    </transition>

    <div class="max-w-6xl mx-auto relative z-10 p-8">
      <transition name="fade" appear>
        <div>
          <div class="mb-4">
            <img
              src="/ArrowLeft.svg"
              alt="Назад"
              class="w-8 h-8 cursor-pointer opacity-50 hover:opacity-100 transition-opacity"
              @click="$router.push('/')"
            />
          </div>

          <h1 class="text-3xl font-bold mb-6">Управление заказами</h1>
          <div class="flex justify-between items-center mb-6">
            <router-link
              to="/admin/blacklist"
              class="bg-gray-700 hover:bg-gray-800 text-white px-4 py-2 rounded"
              >Чёрный список</router-link
            >
          </div>
          <div v-if="loading" class="text-center">Загрузка...</div>
          <div v-else class="space-y-6">
            <div
              v-for="order in orders"
              :key="order.order_id"
              class="bg-white rounded-lg shadow p-6"
            >
              <div class="flex justify-between items-start">
                <div>
                  <p class="font-semibold">Заказ №{{ order.order_id }}</p>
                  <p class="text-sm text-gray-600">Сотрудник: {{ order.user_name }}</p>
                  <p class="text-sm">Статус: {{ statusText(order.status) }}</p>
                  <div
                    v-if="order.status === 'cancelled' && order.cancelled_by_user"
                    class="mt-2 text-red-600 font-bold text-lg border-2 border-red-500 rounded p-2 bg-red-50"
                  >
                    ⚠ Заказ отменён сотрудником
                  </div>
                  <p class="text-sm">
                    Способ получения:
                    {{ order.delivery_method === 'delivery' ? 'Доставка' : 'Самовывоз' }}
                  </p>
                  <p v-if="order.office_address">
                    Адрес: {{ order.office_address }}, каб. {{ order.cabinet }}
                  </p>
                  <p v-if="order.delivery_date">
                    Дата: {{ order.delivery_date }}, слот: {{ order.delivery_time_slot }}
                  </p>
                  <p class="text-sm">Оплата: {{ order.payment_method }}</p>
                  <p class="font-semibold mt-2">Сумма: {{ order.total_amount }} руб.</p>
                  <div class="mt-2">
                    <p class="text-sm font-medium">Товары:</p>
                    <ul class="list-disc list-inside text-sm">
                      <li v-for="item in order.items" :key="item.product_id">
                        {{ item.product_name }} × {{ item.quantity }} ({{ item.total_price }} руб.)
                        <span v-if="item.batch_id"> — Партия №{{ item.batch_id }}</span>
                        <span v-if="item.expiration_date"
                          >, годен до {{ item.expiration_date }}</span
                        >
                      </li>
                    </ul>
                  </div>
                </div>
                <div class="flex flex-col gap-2">
                  <button
                    v-if="order.status === 'pending'"
                    @click="updateStatus(order.order_id, 'accepted')"
                    class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded"
                  >
                    Принять
                  </button>
                  <button
                    v-if="order.status === 'pending'"
                    @click="updateStatus(order.order_id, 'rejected')"
                    class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded"
                  >
                    Отклонить
                  </button>
                  <button
                    v-if="order.status === 'accepted'"
                    @click="updateStatus(order.order_id, 'in_progress')"
                    class="bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded"
                  >
                    В работе
                  </button>
                  <button
                    v-if="order.status === 'in_progress'"
                    @click="updateStatus(order.order_id, 'ready')"
                    class="bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded"
                  >
                    Готово
                  </button>
                  <button
                    v-if="order.status === 'ready'"
                    @click="updateStatus(order.order_id, 'completed')"
                    class="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded"
                  >
                    Завершить
                  </button>
                  <button
                    v-if="['pending', 'accepted', 'in_progress'].includes(order.status)"
                    @click="updateStatus(order.order_id, 'cancelled')"
                    class="bg-gray-400 hover:bg-gray-500 text-white px-4 py-2 rounded"
                  >
                    Отменить
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import axios from 'axios'

const orders = ref([])
const loading = ref(true)
let intervalId = null

const statusText = (status) => {
  const map = {
    pending: 'Ожидает',
    accepted: 'Принят',
    in_progress: 'В работе',
    ready: 'Готово',
    completed: 'Завершён',
    cancelled: 'Отменён',
    rejected: 'Отклонён',
  }
  return map[status] || status
}

const fetchOrders = async () => {
  const token = localStorage.getItem('access_token')
  try {
    const resp = await axios.get('http://127.0.0.1:8000/api/v1/admin/orders/', {
      headers: { Authorization: `Bearer ${token}` },
    })
    orders.value = resp.data
  } catch (e) {
    console.error('Ошибка загрузки заказов')
  } finally {
    if (loading.value) loading.value = false
  }
}

const updateStatus = async (orderId, newStatus) => {
  const token = localStorage.getItem('access_token')
  try {
    await axios.put(
      `http://127.0.0.1:8000/api/v1/admin/orders/${orderId}/status`,
      { status: newStatus },
      { headers: { Authorization: `Bearer ${token}` } },
    )
    await fetchOrders()
  } catch (e) {
    alert('Ошибка обновления статуса')
    console.error(e)
  }
}

onMounted(() => {
  fetchOrders()
  intervalId = setInterval(fetchOrders, 120000)
})

onBeforeUnmount(() => {
  if (intervalId) clearInterval(intervalId)
})
</script>

<style scoped>
.fade-enter-active {
  transition: opacity 0.8s ease;
}
.fade-enter-from {
  opacity: 0;
}
</style>
