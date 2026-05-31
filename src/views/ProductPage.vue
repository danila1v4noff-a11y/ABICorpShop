<template>
  <div class="min-h-screen bg-gray-100 p-4 md:p-8 relative">
    <div v-if="product" class="max-w-6xl mx-auto">
      <transition name="fade" appear>
        <div class="mb-4">
          <img
            src="/ArrowLeft.svg"
            alt="Назад"
            class="w-8 h-8 cursor-pointer opacity-50 hover:opacity-100 transition-opacity"
            @click="$router.back()"
          />
        </div>
      </transition>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <transition name="slide-up" appear>
          <div class="flex flex-col items-center">
            <img
              :src="productImage"
              :alt="product.name"
              class="w-full max-w-sm md:max-w-md h-60 md:h-80 object-contain mb-6"
            />
            <div class="flex gap-4 md:gap-6 mt-4">
              <div class="flex items-center gap-4">
                <div v-if="cartQuantity > 0" class="flex items-center gap-4">
                  <img
                    @click="handleDecrement"
                    src="/Minus_Main.svg"
                    class="w-8 h-8 md:w-10 md:h-10 cursor-pointer transition active:scale-90"
                  />
                  <span class="text-xl md:text-2xl font-bold">{{ cartQuantity }}</span>
                  <img
                    v-if="cartQuantity < 15"
                    @click="handleIncrement"
                    src="/Plus_Main.svg"
                    class="w-8 h-8 md:w-10 md:h-10 cursor-pointer transition active:scale-90"
                  />
                </div>
                <img
                  v-else
                  @click="handleIncrement"
                  src="/ButtonOrder_off.svg"
                  class="cursor-pointer transition active:scale-90 w-24 h-24 md:w-40 md:h-40"
                />
              </div>
              <img
                @click="toggleFavorite"
                :src="isFavorite ? '/ButtonSave_on.svg' : '/ButtonSave_off.svg'"
                class="cursor-pointer transition active:scale-90 w-24 h-24 md:w-40 md:h-40"
              />
            </div>
            <p v-if="cartQuantity >= 15" class="text-red-500 text-sm mt-2">
              Товара больше добавить нельзя
            </p>
          </div>
        </transition>

        <transition name="slide-up" appear>
          <div class="flex flex-col justify-center">
            <h1 class="text-3xl md:text-5xl font-extrabold text-gray-800 mb-4 md:mb-6">
              {{ product.name }}
            </h1>
            <p class="text-gray-600 text-base md:text-lg mb-4 md:mb-6" v-if="product.description">
              {{ product.description }}
            </p>

            <div class="space-y-3 md:space-y-4 mb-6 md:mb-8">
              <div class="flex gap-4 items-baseline">
                <span class="font-semibold text-lg md:text-xl w-20 md:w-24">Цена:</span>
                <span class="text-lg md:text-xl">{{ product.price }} руб.</span>
              </div>
              <div class="flex gap-4 items-baseline">
                <span class="font-semibold text-lg md:text-xl w-20 md:w-24">Вес:</span>
                <span class="text-lg md:text-xl">{{ product.weight }} гр.</span>
              </div>
              <div class="flex gap-4 items-baseline">
                <span class="font-semibold text-lg md:text-xl w-20 md:w-24">Цена за кг:</span>
                <span class="text-lg md:text-xl">{{ pricePerKg }} руб.</span>
              </div>
              <div class="flex gap-4 items-baseline" v-if="product.expiration_date">
                <span class="font-semibold text-lg md:text-xl w-20 md:w-24">Срок годности:</span>
                <span class="text-lg md:text-xl">{{
                  new Date(product.expiration_date).toLocaleDateString('ru-RU')
                }}</span>
              </div>
              <div class="flex flex-col gap-1" v-if="product.cooking_info">
                <span class="font-semibold text-lg md:text-xl">Приготовление:</span>
                <span class="text-lg md:text-xl break-words">{{ product.cooking_info }}</span>
              </div>
            </div>

            <!-- Блок оценок: каждая строго на своей строке, адаптивно -->
            <div class="flex flex-col gap-6 md:gap-8 mb-8">
              <div>
                <p class="text-sm md:text-base text-gray-500 mb-2">Общая оценка</p>
                <div class="flex items-center gap-2">
                  <img
                    v-for="i in 5"
                    :key="'avg' + i"
                    :src="i <= averageRating ? '/Star_on.svg' : '/Star_off.svg'"
                    class="w-8 h-8 md:w-10 md:h-10 flex-shrink-0"
                  />
                  <span
                    class="ml-2 text-lg md:text-xl font-semibold text-gray-700 whitespace-nowrap"
                  >
                    {{ averageRating ? averageRating + '/5' : 'нет оценок' }}
                  </span>
                </div>
              </div>
              <div>
                <p class="text-sm md:text-base text-gray-500 mb-2">Ваша оценка</p>
                <div class="flex items-center gap-2">
                  <img
                    v-for="i in 5"
                    :key="'user' + i"
                    :src="i <= userRating ? '/Star_on.svg' : '/Star_off.svg'"
                    class="w-8 h-8 md:w-10 md:h-10 cursor-pointer transition hover:scale-110 flex-shrink-0"
                    @click="rateProduct(i)"
                  />
                  <span
                    class="ml-2 text-lg md:text-xl font-semibold text-gray-700 whitespace-nowrap"
                  >
                    {{ userRating ? userRating + '/5' : 'не оценено' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </transition>
      </div>

      <transition name="slide-up" appear>
        <div v-if="relatedProducts.length" class="mt-12">
          <h3 class="text-xl md:text-2xl font-semibold mb-4 md:mb-6">Похожие товары</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 md:gap-6">
            <div
              v-for="rel in relatedProducts"
              :key="rel.product_id"
              class="flex items-center gap-4 border rounded-lg p-3 md:p-4 cursor-pointer hover:shadow transition bg-white"
              @click="$router.push(`/product/${rel.product_id}`)"
            >
              <img
                :src="rel.image_url"
                :alt="rel.name"
                class="w-16 h-16 md:w-24 md:h-24 object-contain rounded"
              />
              <p class="font-medium text-base md:text-lg">{{ rel.name }}</p>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { useCart } from '../composables/useCart'
import { useFavorites } from '../composables/useFavorites'

const route = useRoute()
const router = useRouter()
const productId = computed(() => parseInt(route.params.id))

const product = ref(null)
const relatedProducts = ref([])
const cartQuantity = ref(0)
const isFavorite = ref(false)
const averageRating = ref(null)
const userRating = ref(0)

const { cartItems, fetchCart, addToCart, updateCartItem, removeFromCart } = useCart()
const { favorites, fetchFavorites, addFavorite, removeFavorite } = useFavorites()

const productImage = computed(() => {
  if (!product.value?.image_url) return ''
  const url = product.value.image_url
  const lastDot = url.lastIndexOf('.')
  if (lastDot === -1) return url
  const base = url.substring(0, lastDot)
  const ext = url.substring(lastDot)
  return `${base}_1${ext}`
})

const pricePerKg = computed(() => {
  if (!product.value?.weight || product.value.weight === 0) return 0
  return Math.round((product.value.price / (product.value.weight / 1000)) * 100) / 100
})

const loadProduct = async () => {
  try {
    const [prodResp, relResp, ratingResp] = await Promise.all([
      axios.get(`http://127.0.0.1:8000/api/v1/products/${productId.value}`),
      axios.get(`http://127.0.0.1:8000/api/v1/products/${productId.value}/related`),
      axios
        .get(`http://127.0.0.1:8000/api/v1/products/${productId.value}/rating`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
        })
        .catch(() => ({ data: { average_rating: null, user_rating: 0 } })),
    ])
    product.value = prodResp.data
    relatedProducts.value = relResp.data
    averageRating.value = ratingResp.data.average_rating
    userRating.value = ratingResp.data.user_rating || 0
    updateLocalState()
  } catch (e) {
    console.error('Ошибка загрузки товара')
    router.push('/')
  }
}

// Получает реальное количество товара в корзине, суммируя по всем партиям этого продукта
const getCurrentCartQuantity = () => {
  if (!product.value) return 0
  return cartItems.value
    .filter((item) => item.product_id === product.value.product_id)
    .reduce((sum, item) => sum + item.quantity, 0)
}

const updateLocalState = () => {
  if (!product.value) return
  cartQuantity.value = getCurrentCartQuantity()
  isFavorite.value = favorites.value.some((fav) => fav.product_id === product.value.product_id)
}

// Для добавления выбираем первую доступную партию (любую, т.к. на странице товара нет выбора партии)
const handleIncrement = async () => {
  if (cartQuantity.value >= 15) return
  const token = localStorage.getItem('access_token')
  if (!token) {
    alert('Необходимо авторизоваться')
    return
  }

  // Ищем первую партию с остатком
  let batchId = null
  try {
    const resp = await axios.get(`http://127.0.0.1:8000/api/v1/products/${productId.value}`)
    const productData = resp.data
    // Получаем все партии товара
    const batchesResp = await axios.get(`http://127.0.0.1:8000/api/v1/products/`)
    const allBatches = batchesResp.data
    const productBatches = allBatches.filter(
      (b) => b.product_id === productId.value && b.quantity > 0,
    )
    if (productBatches.length > 0) {
      batchId = productBatches[0].batch_id
    } else {
      alert('Товара нет в наличии')
      return
    }
  } catch (e) {
    alert('Ошибка получения данных о партии')
    return
  }

  try {
    // Находим элемент корзины с таким же batch_id
    const existingItem = cartItems.value.find((i) => i.batch_id === batchId)
    if (existingItem) {
      await updateCartItem(existingItem.cart_item_id, existingItem.quantity + 1)
    } else {
      await addToCart(product.value.product_id, batchId, 1)
    }
    await fetchCart()
    updateLocalState()
  } catch (e) {
    alert(e?.response?.data?.detail || 'Ошибка')
  }
}

const handleDecrement = async () => {
  const token = localStorage.getItem('access_token')
  if (!token) return

  // Находим любой элемент корзины для этого товара
  const existingItem = cartItems.value.find(
    (i) => i.product_id === product.value.product_id && i.quantity > 0,
  )
  if (!existingItem) return

  try {
    if (existingItem.quantity > 1) {
      await updateCartItem(existingItem.cart_item_id, existingItem.quantity - 1)
    } else {
      await removeFromCart(existingItem.cart_item_id)
    }
    await fetchCart()
    updateLocalState()
  } catch (e) {
    alert(e?.response?.data?.detail || 'Ошибка')
  }
}

const toggleFavorite = async () => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    alert('Необходимо авторизоваться')
    return
  }
  try {
    if (isFavorite.value) {
      await removeFavorite(product.value.product_id)
    } else {
      await addFavorite(product.value.product_id)
    }
    await fetchFavorites()
    isFavorite.value = !isFavorite.value
  } catch {
    alert('Ошибка')
  }
}

const rateProduct = async (rating) => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    alert('Необходимо авторизоваться')
    return
  }
  try {
    const resp = await axios.post(
      `http://127.0.0.1:8000/api/v1/products/${productId.value}/rate`,
      { rating },
      { headers: { Authorization: `Bearer ${token}` } },
    )
    averageRating.value = resp.data.average_rating
    userRating.value = resp.data.user_rating
  } catch {
    alert('Ошибка при оценке')
  }
}

onMounted(async () => {
  await Promise.all([fetchCart(), fetchFavorites()])
  await loadProduct()
})

watch(
  () => route.params.id,
  () => {
    if (route.name === 'Product') loadProduct()
  },
)
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.4s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active {
  transition: all 0.5s ease-out;
}
.slide-up-leave-active {
  transition: all 0.3s ease-in;
}
.slide-up-enter-from {
  opacity: 0;
  transform: translateY(30px);
}
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
