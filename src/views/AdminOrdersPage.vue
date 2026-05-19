<template>
  <div class="min-h-screen bg-gray-100 p-8">
    <!-- Стрелка назад в левом верхнем углу -->
    <div class="absolute top-8 left-8 z-10">
      <img
        src="/ArrowLeft.svg"
        alt="Назад"
        class="w-8 h-8 cursor-pointer opacity-50 hover:opacity-100 transition-opacity"
        @click="$router.push('/')"
      />
    </div>

    <div class="max-w-6xl mx-auto">
      <h1 class="text-3xl font-bold mb-6">Управление заказами</h1>
      <div v-if="loading" class="text-center">Загрузка...</div>
      <div v-else class="space-y-6">
        <div v-for="order in orders" :key="order.order_id" class="bg-white rounded-lg shadow p-6">
          <div class="flex justify-between items-start">
            <div>
              <p class="font-semibold">Заказ №{{ order.order_id }}</p>
              <p class="text-sm text-gray-600">Сотрудник: {{ order.user_name }}</p>
              <p class="text-sm">Статус: {{ statusText(order.status) }}</p>
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
                  </li>
                </ul>
              </div>
            </div>
            <div class="flex flex-col gap-2">
              <!-- Кнопки в зависимости от статуса -->
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const orders = ref([])
const loading = ref(true)

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
    alert('Ошибка загрузки заказов')
    console.error(e)
  } finally {
    loading.value = false
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

onMounted(fetchOrders)
</script>
