<template>
  <div class="min-h-screen bg-gray-100 p-8">
    <!-- Основной контент корзины (показывается до оформления заказа) -->
    <div v-if="!orderPlaced">
      <!-- Стрелка назад -->
      <div class="mb-4">
        <img
          src="/ArrowLeft.svg"
          alt="Назад"
          class="w-8 h-8 cursor-pointer opacity-50 hover:opacity-100 transition-opacity"
          @click="$router.push('/')"
        />
      </div>

      <div class="max-w-6xl mx-auto">
        <div class="bg-white rounded-lg shadow p-6 mb-6">
          <h1 class="text-3xl font-bold">Корзина</h1>
        </div>

        <div
          v-if="combinedItems.length === 0"
          class="bg-white rounded-lg shadow p-6 text-center text-gray-500"
        >
          Корзина пуста
        </div>

        <div v-else class="grid grid-cols-2 gap-6 items-stretch">
          <!-- Левая колонка: товары -->
          <div class="bg-white rounded-lg shadow p-6">
            <h2 class="text-xl font-semibold mb-4">Товары</h2>
            <div class="space-y-4">
              <div
                v-for="item in combinedItems"
                :key="item.isShared ? `s_${item.shared_item_id}` : `p_${item.cart_item_id}`"
                class="flex items-center gap-4 border-b pb-4"
              >
                <img :src="item.image_url" alt="product" class="w-16 h-16 object-contain rounded" />
                <div class="flex-1">
                  <p class="font-semibold">{{ item.product_name }}</p>
                  <!-- Цена с учётом скидки -->
                  <p class="text-gray-600">
                    <template v-if="item.discount_price">
                      <span class="line-through text-red-400 mr-2">{{ item.price }} руб.</span>
                      <span class="font-semibold text-gray-800"
                        >{{ item.discount_price }} руб.</span
                      >
                    </template>
                    <template v-else> {{ item.price }} руб. </template>
                  </p>
                  <p
                    v-if="item.isShared && item.added_by_user_name"
                    class="text-xs text-blue-600 mt-1"
                  >
                    Добавил: {{ item.added_by_user_name }}
                  </p>
                </div>
                <div class="flex items-center gap-2">
                  <!-- ПЛЮС (скрыт, если >= 15) -->
                  <button
                    v-if="item.quantity < 15"
                    @click="increaseQuantity(item)"
                    class="w-8 h-8 rounded border hover:bg-gray-100 flex items-center justify-center"
                  >
                    <img src="/Plus_Main.svg" alt="+" class="w-4 h-4" />
                  </button>
                  <span class="w-8 text-center">{{ item.quantity }}</span>
                  <!-- МИНУС (всегда) -->
                  <button
                    @click="decreaseQuantity(item)"
                    class="w-8 h-8 rounded border hover:bg-gray-100 flex items-center justify-center"
                  >
                    <img src="/Minus_Main.svg" alt="-" class="w-4 h-4" />
                  </button>
                </div>
                <button @click="removeItem(item)" class="text-red-500 hover:text-red-700 ml-2">
                  Удалить
                </button>
              </div>
            </div>
          </div>

          <!-- Правая колонка -->
          <div class="flex flex-col gap-6">
            <div class="bg-white rounded-lg shadow p-6">
              <div class="space-y-4">
                <div class="flex justify-between text-lg">
                  <span>Сумма заказа</span>
                  <span class="font-bold">{{ totalSumCombined }} руб.</span>
                </div>
                <div class="flex justify-between text-lg">
                  <span>Масса нетто заказа</span>
                  <span class="font-bold">{{ totalWeightCombined }} г.</span>
                </div>
              </div>
              <div class="border-t mt-4 pt-4">
                <h3 class="font-semibold mb-3">Способ доставки</h3>
                <div class="space-y-2">
                  <label class="flex items-center gap-3 cursor-pointer" @click="openDeliveryModal">
                    <input
                      type="radio"
                      name="delivery"
                      value="delivery"
                      class="w-5 h-5"
                      v-model="deliveryMethod"
                    />
                    <span>Доставка</span>
                  </label>
                  <label class="flex items-center gap-3 cursor-pointer" @click="setPickup">
                    <input
                      type="radio"
                      name="delivery"
                      value="pickup"
                      class="w-5 h-5"
                      v-model="deliveryMethod"
                    />
                    <span>Самовывоз</span>
                  </label>
                </div>
                <!-- Информация о выбранном офисе при доставке -->
                <div
                  v-if="deliveryMethod === 'delivery' && selectedOffice"
                  class="mt-2 text-sm text-gray-700 bg-gray-50 p-2 rounded"
                >
                  <p>Офис: {{ selectedOffice.address }}</p>
                  <p>Кабинет: {{ selectedCabinet }}</p>
                  <p class="text-gray-500 mt-1">
                    Доставка в офис осуществляется ежедневно в {{ selectedOffice.deliveryTime }}
                  </p>
                </div>
                <!-- Блок выбора даты и времени для самовывоза -->
                <div v-if="deliveryMethod === 'pickup'" class="mt-4">
                  <h4 class="text-sm font-medium text-gray-800 mb-2">Выберите дату и время</h4>
                  <div class="grid grid-cols-3 gap-2 mb-3">
                    <button
                      v-for="d in pickupDates"
                      :key="d.value"
                      @click="selectedPickupDate = d.value"
                      :disabled="getDateRemaining(d.value) === 0"
                      class="text-sm border rounded px-2 py-1 transition"
                      :class="{
                        'bg-[#FFA100] text-white border-[#FFA100]': selectedPickupDate === d.value,
                        'border-gray-300 hover:border-[#FFA100]':
                          selectedPickupDate !== d.value && getDateRemaining(d.value) > 0,
                        'opacity-50 cursor-not-allowed': getDateRemaining(d.value) === 0,
                      }"
                    >
                      {{ d.label }}
                      <span class="block text-xs mt-1" v-if="getDateRemaining(d.value) !== null">
                        ({{ getDateRemaining(d.value) }} мест)
                      </span>
                    </button>
                  </div>
                  <div class="grid grid-cols-2 gap-2">
                    <button
                      v-for="slot in pickupSlots"
                      :key="slot.value"
                      @click="selectedPickupSlot = slot"
                      :disabled="!selectedPickupDate || getSlotRemaining(slot.value) === 0"
                      class="text-sm border rounded px-2 py-1 transition"
                      :class="{
                        'bg-[#FFA100] text-white border-[#FFA100]':
                          selectedPickupSlot?.value === slot.value,
                        'border-gray-300 hover:border-[#FFA100]':
                          selectedPickupSlot?.value !== slot.value &&
                          getSlotRemaining(slot.value) > 0,
                        'opacity-50 cursor-not-allowed': getSlotRemaining(slot.value) === 0,
                      }"
                    >
                      {{ slot.label }}
                      <span
                        class="block text-xs mt-1"
                        v-if="selectedPickupDate && getSlotRemaining(slot.value) !== null"
                      >
                        ({{ getSlotRemaining(slot.value) }} мест)
                      </span>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Блок "Поделиться корзиной" -->
            <div
              class="bg-white rounded-lg shadow p-6 cursor-pointer hover:shadow-md transition"
              @click="shareCart"
            >
              <div class="flex items-center gap-4">
                <img src="/Plus.svg" alt="Поделиться" class="w-24 h-24 flex-shrink-0" />
                <div>
                  <p class="font-semibold">Поделитесь корзиной с коллегами</p>
                  <p class="text-gray-600">чтобы они могли добавлять в корзину свои продукты</p>
                </div>
              </div>
            </div>

            <div class="bg-white rounded-lg shadow p-6">
              <h2 class="text-xl font-semibold mb-4">Способ оплаты</h2>
              <div class="space-y-3">
                <label class="flex items-center gap-3 cursor-pointer">
                  <input
                    type="radio"
                    name="payment"
                    value="sbp"
                    class="w-5 h-5"
                    v-model="paymentMethod"
                  />
                  <span>СБП</span>
                </label>
                <!-- Картой доступно всегда -->
                <label class="flex items-center gap-3 cursor-pointer">
                  <input
                    type="radio"
                    name="payment"
                    value="card"
                    class="w-5 h-5"
                    v-model="paymentMethod"
                  />
                  <span>Картой</span>
                </label>
                <!-- Наличные только при самовывозе -->
                <label
                  v-if="deliveryMethod === 'pickup'"
                  class="flex items-center gap-3 cursor-pointer"
                >
                  <input
                    type="radio"
                    name="payment"
                    value="cash"
                    class="w-5 h-5"
                    v-model="paymentMethod"
                  />
                  <span>Наличными</span>
                </label>
              </div>
              <p v-if="paymentMethod === 'cash'" class="text-xs text-gray-400 mt-2">
                Подготовьте, пожалуйста, без сдачи
              </p>
            </div>
          </div>
        </div>

        <!-- Блок кнопки "Продолжить" -->
        <div v-if="combinedItems.length > 0" class="mt-8 flex flex-col items-center">
          <button
            @click="handleContinue"
            :disabled="!canProceed"
            class="bg-[#FFA100] hover:bg-[#e09000] text-white font-bold py-2 px-6 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Продолжить
          </button>
          <p v-if="!canProceed" class="mt-3 text-red-500 text-sm">
            Заполните информацию о заказе (способ доставки, данные, способ оплаты)
          </p>
        </div>
      </div>
    </div>

    <!-- Сообщение об успешном оформлении заказа (показывается вместо интерфейса) -->
    <div v-else class="flex items-center justify-center min-h-screen">
      <div class="text-center">
        <h2 class="text-2xl font-bold text-gray-800 mb-2">Ваш заказ взят в работу</h2>
        <p class="text-gray-600">Сейчас вы будете перенаправлены на главную страницу...</p>
      </div>
    </div>

    <!-- Модальное окно выбора доставки -->
    <div
      v-if="showDeliveryModal && !orderPlaced"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-md relative">
        <button
          @click="closeDeliveryModal"
          class="absolute top-3 right-3 text-gray-400 hover:text-gray-600 transition"
        >
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

        <h2 class="text-xl font-bold mb-4">Выберите офис и кабинет</h2>

        <div class="space-y-3 mb-6">
          <div
            v-for="office in offices"
            :key="office.id"
            @click="selectOffice(office)"
            class="border rounded-lg p-3 cursor-pointer transition hover:border-[#FFA100]"
            :class="{ 'border-[#FFA100] bg-orange-50': selectedOffice?.id === office.id }"
          >
            <p class="font-medium">{{ office.address }}</p>
            <p class="text-sm text-gray-600" v-if="selectedOffice?.id === office.id">
              Доставка в офис осуществляется ежедневно в {{ office.deliveryTime }}
            </p>
          </div>
        </div>

        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Номер кабинета</label>
          <input
            v-model="selectedCabinet"
            type="text"
            class="w-full border rounded px-3 py-2 focus:outline-none focus:ring-1 focus:ring-[#FFA100]"
            placeholder="Введите кабинет"
          />
        </div>

        <button
          @click="confirmDelivery"
          :disabled="!selectedOffice"
          class="w-full bg-[#FFA100] hover:bg-[#e09000] text-white font-bold py-2 px-4 rounded transition-colors disabled:opacity-50"
        >
          ОК
        </button>
      </div>
    </div>

    <!-- Модальное окно QR-кода (СБП) -->
    <div
      v-if="showQrModal && !orderPlaced"
      class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg shadow-xl p-6 max-w-sm w-full text-center relative">
        <button
          @click="showQrModal = false"
          class="absolute top-3 right-3 text-gray-400 hover:text-gray-600 transition"
        >
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
        <h2 class="text-xl font-bold mb-4">Оплата по СБП</h2>
        <p class="mb-4 text-gray-600">Отсканируйте QR-код в приложении банка</p>
        <img src="/qr-placeholder.svg" alt="QR-код" class="mx-auto w-48 h-48" />
        <p class="mt-4 text-sm text-gray-500">После оплаты нажмите «Готово»</p>
        <button
          @click="completePayment"
          class="mt-4 w-full bg-[#FFA100] hover:bg-[#e09000] text-white font-bold py-2 rounded transition-colors"
        >
          Готово
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useCart } from '../composables/useCart'

const router = useRouter()
const { cartItems, totalSum, totalWeight, fetchCart, updateCartItem, removeFromCart, clearCart } =
  useCart()

const sharedCart = ref(null)
const sharedToken = ref('')
const showDeliveryModal = ref(false)
const selectedOffice = ref(null)
const selectedCabinet = ref('')

const deliveryMethod = ref('delivery')
const paymentMethod = ref('sbp')

const selectedPickupDate = ref(null)
const selectedPickupSlot = ref(null)

const orderPlaced = ref(false)

const offices = ref([
  { id: 1, address: 'Дворянская 27АК17', deliveryTime: '16:00' },
  { id: 2, address: 'Ленина 15АК17', deliveryTime: '15:30' },
  { id: 3, address: 'Пушкина 10АК17', deliveryTime: '17:00' },
  { id: 4, address: 'Гагарина 5АК17', deliveryTime: '14:45' },
])

// Генерация рабочих дней (с учётом времени 16:00)
const pickupDates = computed(() => {
  const dates = []
  let current = new Date()
  const now = new Date()
  if (now.getHours() >= 16) {
    current.setDate(current.getDate() + 1)
  }
  while (dates.length < 3) {
    const day = current.getDay()
    if (day !== 0 && day !== 6) {
      dates.push({
        value: current.toISOString().split('T')[0],
        label: current.toLocaleDateString('ru-RU', {
          day: 'numeric',
          month: 'long',
          weekday: 'short',
        }),
      })
    }
    current.setDate(current.getDate() + 1)
  }
  return dates
})

const pickupSlots = [
  { label: '10:00 – 12:00', value: '10-12' },
  { label: '14:00 – 16:00', value: '14-16' },
]

// === Логика слотов ===
const availableSlots = ref([])

const fetchAvailableSlots = async () => {
  try {
    const resp = await axios.get('http://127.0.0.1:8000/api/v1/pickup-slots/available')
    availableSlots.value = resp.data
  } catch (e) {
    console.error('Ошибка загрузки слотов')
  }
}

// Сумма оставшихся мест по всем слотам на дату
const getDateRemaining = (dateStr) => {
  if (!availableSlots.value.length) return null
  return availableSlots.value
    .filter((s) => s.date === dateStr)
    .reduce((sum, s) => sum + s.remaining, 0)
}

// Оставшиеся места в конкретном слоте на выбранную дату
const getSlotRemaining = (timeSlot) => {
  const selDate = selectedPickupDate.value
  if (!selDate || !availableSlots.value.length) return null
  const slot = availableSlots.value.find((s) => s.date === selDate && s.time_slot === timeSlot)
  return slot ? slot.remaining : 0
}

// Переключение на самовывоз – подгружаем слоты
watch(deliveryMethod, (newVal) => {
  if (newVal === 'pickup') {
    fetchAvailableSlots()
  }
})

// === Остальные функции без изменений ===

const setPickup = () => {
  deliveryMethod.value = 'pickup'
  selectedOffice.value = null
  selectedCabinet.value = ''
  showDeliveryModal.value = false
}

const openDeliveryModal = () => {
  deliveryMethod.value = 'delivery'
  selectedPickupDate.value = null
  selectedPickupSlot.value = null
  showDeliveryModal.value = true
}

const closeDeliveryModal = () => {
  showDeliveryModal.value = false
  if (!selectedOffice.value) deliveryMethod.value = 'pickup'
}

const selectOffice = (office) => {
  selectedOffice.value = office
}

const confirmDelivery = () => {
  if (!selectedOffice.value) return
  showDeliveryModal.value = false
}

const canProceed = computed(() => {
  if (deliveryMethod.value === 'delivery') {
    return selectedOffice.value && selectedCabinet.value.trim() !== '' && paymentMethod.value
  } else if (deliveryMethod.value === 'pickup') {
    return selectedPickupDate.value && selectedPickupSlot.value && paymentMethod.value
  }
  return false
})

const showQrModal = ref(false)

const submitOrder = async () => {
  try {
    const mergedItems = combinedItems.value.reduce((acc, item) => {
      const existing = acc.find((p) => p.product_id === item.product_id)
      if (existing) {
        existing.quantity += item.quantity
      } else {
        acc.push({
          product_id: item.product_id,
          quantity: item.quantity,
        })
      }
      return acc
    }, [])

    const orderData = {
      delivery_method: deliveryMethod.value,
      office_address:
        deliveryMethod.value === 'delivery' ? selectedOffice.value?.address || '' : null,
      cabinet: deliveryMethod.value === 'delivery' ? selectedCabinet.value : null,
      delivery_date: deliveryMethod.value === 'pickup' ? selectedPickupDate.value : null,
      delivery_time_slot:
        deliveryMethod.value === 'pickup' ? selectedPickupSlot.value?.value : null,
      payment_method: paymentMethod.value,
      items: mergedItems,
    }

    const token = localStorage.getItem('access_token')
    await axios.post('http://127.0.0.1:8000/api/v1/orders/', orderData, {
      headers: { Authorization: `Bearer ${token}` },
    })
    clearCart()
    if (sharedToken.value) {
      localStorage.removeItem('shared_cart_token')
      sharedToken.value = ''
      sharedCart.value = null
    }
    // Обновляем слоты после успешного заказа
    if (deliveryMethod.value === 'pickup') {
      fetchAvailableSlots()
    }
    return true
  } catch (err) {
    console.error(err)
    alert(err.response?.data?.detail || 'Ошибка при оформлении заказа')
    return false
  }
}

const handleContinue = async () => {
  if (!canProceed.value) return
  if (paymentMethod.value === 'sbp') {
    showQrModal.value = true
  } else {
    const success = await submitOrder()
    if (success) {
      orderPlaced.value = true
      setTimeout(() => {
        router.push('/')
      }, 2000)
    }
  }
}

const completePayment = async () => {
  showQrModal.value = false
  const success = await submitOrder()
  if (success) {
    orderPlaced.value = true
    setTimeout(() => {
      router.push('/')
    }, 2000)
  }
}

// ====== Логика общей корзины (ИСПРАВЛЕНО) ======
const combinedItems = computed(() => {
  const personal = cartItems.value.map((item) => ({
    ...item,
    isShared: false,
    added_by_user_name: null,
    shared_item_id: null,
  }))

  const shared = (sharedCart.value?.items || []).map((item) => ({
    cart_item_id: null,
    product_id: item.product_id,
    product_name: item.product_name,
    price: item.price, // исходная цена
    discount_price: item.discount_price, // <-- теперь берём из ответа API
    image_url: item.image_url,
    quantity: item.quantity,
    isShared: true,
    added_by_user_name: item.added_by_user_name,
    shared_item_id: item.id,
  }))

  const merged = [...personal, ...shared].sort((a, b) =>
    a.product_name.localeCompare(b.product_name, 'ru'),
  )
  return merged
})

const totalSumCombined = computed(() => {
  let sum = totalSum.value
  if (sharedCart.value) {
    sum += sharedCart.value.items.reduce((acc, item) => {
      const price = item.discount_price || item.price
      return acc + price * item.quantity
    }, 0)
  }
  return sum
})

const totalWeightCombined = computed(() => totalWeight.value)

const currentUserId = ref(null)

// Исправленная загрузка общей корзины
const loadSharedCart = async () => {
  if (!sharedToken.value) {
    sharedCart.value = null
    return
  }
  try {
    const response = await axios.get(
      `http://127.0.0.1:8000/api/v1/shared-cart/${sharedToken.value}`,
    )
    const data = response.data
    console.log('Общая корзина загружена:', data)

    if (currentUserId.value && data.owner_id !== currentUserId.value) {
      console.warn('Токен чужой корзины, сбрасываем')
      localStorage.removeItem('shared_cart_token')
      sharedToken.value = ''
      sharedCart.value = null
      return
    }
    // Принудительно создаём новый объект для реактивности
    sharedCart.value = { ...data, items: data.items ? [...data.items] : [] }
  } catch (err) {
    console.error('Ошибка загрузки общей корзины:', err)
    localStorage.removeItem('shared_cart_token')
    sharedToken.value = ''
    sharedCart.value = null
  }
}

const increaseSharedQuantity = async (item) => {
  if (item.quantity >= 15) {
    alert('Максимальное количество товара — 15 шт.')
    return
  }
  const token = localStorage.getItem('access_token')
  if (!token) return
  try {
    await axios.put(
      `http://127.0.0.1:8000/api/v1/shared-cart/${sharedToken.value}/item/${item.shared_item_id}`,
      { quantity: item.quantity + 1 },
      { headers: { Authorization: `Bearer ${token}` } },
    )
    await loadSharedCart()
  } catch (err) {
    alert('Ошибка изменения количества')
  }
}

const decreaseSharedQuantity = async (item) => {
  const token = localStorage.getItem('access_token')
  if (!token) return
  try {
    if (item.quantity <= 1) {
      await axios.delete(
        `http://127.0.0.1:8000/api/v1/shared-cart/${sharedToken.value}/item/${item.shared_item_id}`,
        { headers: { Authorization: `Bearer ${token}` } },
      )
    } else {
      await axios.put(
        `http://127.0.0.1:8000/api/v1/shared-cart/${sharedToken.value}/item/${item.shared_item_id}`,
        { quantity: item.quantity - 1 },
        { headers: { Authorization: `Bearer ${token}` } },
      )
    }
    await loadSharedCart()
  } catch (err) {
    alert('Ошибка изменения количества')
  }
}

const removeSharedItem = async (sharedItemId) => {
  const token = localStorage.getItem('access_token')
  if (!token) return
  try {
    await axios.delete(
      `http://127.0.0.1:8000/api/v1/shared-cart/${sharedToken.value}/item/${sharedItemId}`,
      { headers: { Authorization: `Bearer ${token}` } },
    )
    await loadSharedCart()
  } catch (err) {
    alert('Ошибка удаления')
  }
}

const increaseQuantity = (item) => {
  if (item.quantity >= 15) {
    alert('Максимальное количество товара — 15 шт.')
    return
  }
  if (item.isShared) {
    increaseSharedQuantity(item)
  } else {
    updateCartItem(item.cart_item_id, item.quantity + 1)
  }
}

const decreaseQuantity = (item) => {
  if (item.isShared) {
    decreaseSharedQuantity(item)
  } else {
    if (item.quantity > 1) {
      updateCartItem(item.cart_item_id, item.quantity - 1)
    } else {
      removeFromCart(item.cart_item_id)
    }
  }
}

const removeItem = (item) => {
  if (item.isShared) {
    if (confirm('Удалить товар из общей корзины?')) {
      removeSharedItem(item.shared_item_id)
    }
  } else {
    if (confirm('Удалить товар из корзины?')) {
      removeFromCart(item.cart_item_id)
    }
  }
}

const shareCart = async () => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    alert('Необходимо авторизоваться')
    return
  }
  try {
    const response = await axios.post(
      'http://127.0.0.1:8000/api/v1/shared-cart/',
      {},
      { headers: { Authorization: `Bearer ${token}` } },
    )
    const newToken = response.data.token
    localStorage.setItem('shared_cart_token', newToken)
    sharedToken.value = newToken
    await loadSharedCart()
    const link = `${window.location.origin}/shared/${newToken}`
    await navigator.clipboard.writeText(link)
    alert('Ссылка скопирована! Отправьте её коллегам.')
  } catch (err) {
    console.error(err)
    alert('Ошибка при создании общей корзины')
  }
}

onMounted(async () => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      const user = JSON.parse(userStr)
      currentUserId.value = user.employee_id
    } catch (e) {
      // ignore
    }
  }
  await fetchCart()
  const savedSharedToken = localStorage.getItem('shared_cart_token')
  if (savedSharedToken) {
    sharedToken.value = savedSharedToken
    await loadSharedCart()
  }
  // Первоначальная загрузка слотов
  fetchAvailableSlots()
})
</script>
