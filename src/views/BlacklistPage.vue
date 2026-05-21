<template>
  <div class="min-h-screen bg-gray-100 p-8">
    <div class="max-w-4xl mx-auto">
      <div class="mb-4">
        <img
          src="/ArrowLeft.svg"
          class="w-8 h-8 cursor-pointer opacity-50 hover:opacity-100"
          @click="$router.push('/admin/orders')"
        />
      </div>
      <h1 class="text-3xl font-bold mb-6">Чёрный список</h1>

      <!-- Добавление -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">Добавить сотрудника</h2>
        <div class="flex gap-4 mb-4">
          <select v-model="selectedUserId" class="border rounded px-3 py-2 flex-1">
            <option :value="null">Выберите сотрудника</option>
            <option v-for="u in users" :key="u.employee_id" :value="u.employee_id">
              {{ u.fio }}
            </option>
          </select>
          <input
            v-model="reason"
            type="text"
            placeholder="Причина блокировки"
            class="border rounded px-3 py-2 flex-1"
          />
          <button
            @click="addToBlacklist"
            class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded"
          >
            Заблокировать
          </button>
        </div>
      </div>

      <!-- Список заблокированных -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-xl font-semibold mb-4">Заблокированные сотрудники</h2>
        <div v-if="blacklist.length === 0" class="text-gray-500">Пусто</div>
        <div
          v-for="entry in blacklist"
          :key="entry.blacklist_id"
          class="flex items-center justify-between border-b py-3"
        >
          <div>
            <p class="font-medium">{{ entry.user_name }} (ID {{ entry.user_id }})</p>
            <p class="text-sm text-gray-600">Причина: {{ entry.reason }}</p>
            <p class="text-xs text-gray-400">
              Добавлен: {{ formatDate(entry.created_at) }} ({{ entry.created_by_name }})
            </p>
          </div>
          <button
            @click="removeFromBlacklist(entry.user_id)"
            class="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded"
          >
            Разблокировать
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const users = ref([])
const selectedUserId = ref(null)
const reason = ref('')
const blacklist = ref([])

const fetchUsers = async () => {
  const token = localStorage.getItem('access_token')
  const resp = await axios.get('http://127.0.0.1:8000/api/v1/users/', {
    headers: { Authorization: `Bearer ${token}` },
  })
  users.value = resp.data
}

const fetchBlacklist = async () => {
  const token = localStorage.getItem('access_token')
  const resp = await axios.get('http://127.0.0.1:8000/api/v1/admin/blacklist/', {
    headers: { Authorization: `Bearer ${token}` },
  })
  blacklist.value = resp.data
}

const addToBlacklist = async () => {
  if (!selectedUserId.value || !reason.value.trim()) return
  const token = localStorage.getItem('access_token')
  try {
    await axios.post(
      'http://127.0.0.1:8000/api/v1/admin/blacklist/',
      {
        user_id: selectedUserId.value,
        reason: reason.value,
      },
      {
        headers: { Authorization: `Bearer ${token}` },
      },
    )
    selectedUserId.value = null
    reason.value = ''
    await fetchBlacklist()
  } catch (err) {
    alert(err.response?.data?.detail || 'Ошибка')
  }
}

const removeFromBlacklist = async (userId) => {
  const token = localStorage.getItem('access_token')
  try {
    await axios.delete(`http://127.0.0.1:8000/api/v1/admin/blacklist/${userId}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    await fetchBlacklist()
  } catch (err) {
    alert('Ошибка при разблокировке')
  }
}

const formatDate = (iso) => new Date(iso).toLocaleDateString('ru-RU')

onMounted(() => {
  fetchUsers()
  fetchBlacklist()
})
</script>
