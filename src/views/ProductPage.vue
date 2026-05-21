<template>
  <div class="min-h-screen bg-gray-100 p-8 relative">
    <!-- Логотип -->
    <img
      src="/Logo.svg"
      alt="Логотип"
      class="absolute top-0 left-4 h-12 w-auto mt-4 cursor-pointer"
      @click="$router.push('/')"
    />

    <div v-if="product" class="max-w-6xl mx-auto">
      <!-- Кнопка назад -->
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
        <!-- Левая часть: фото и кнопки -->
        <transition name="slide-up" appear>
          <div class="flex flex-col items-center">
            <img
              :src="productImage"
              :alt="product.name"
              class="w-full max-w-md h-80 object-contain mb-6"
            />
            <div class="flex gap-6 mt-4">
              <div class="flex items-center gap-4">
                <div v-if="cartQuantity > 0" class="flex items-center gap-4">
                  <img
                    @click="handleDecrement"
                    src="/Minus_Main.svg"
                    class="w-10 h-10 cursor-pointer transition active:scale-90"
                  />
                  <span class="text-2xl font-bold">{{ cartQuantity }}</span>
                  <img
                    v-if="cartQuantity < 15"
                    @click="handleIncrement"
                    src="/Plus_Main.svg"
                    class="w-10 h-10 cursor-pointer transition active:scale-90"
                  />
                </div>
                <img
                  v-else
                  @click="handleIncrement"
                  src="/ButtonOrder_off.svg"
                  class="cursor-pointer transition active:scale-90 w-40 h-40"
                />
              </div>
              <img
                @click="toggleFavorite"
                :src="isFavorite ? '/ButtonSave_on.svg' : '/ButtonSave_off.svg'"
                class="cursor-pointer transition active:scale-90 w-40 h-40"
              />
            </div>
            <p v-if="cartQuantity >= 15" class="text-red-500 text-sm mt-2">
              Товара больше добавить нельзя
            </p>
          </div>
        </transition>

        <!-- Правая часть: информация -->
        <transition name="slide-up" appear>
          <div class="flex flex-col justify-center">
            <h1 class="text-5xl font-extrabold text-gray-800 mb-6">{{ product.name }}</h1>
            <p class="text-gray-600 text-lg mb-6" v-if="product.description">
              {{ product.description }}
            </p>

            <div class="space-y-4 mb-8">
              <div class="flex gap-4 items-baseline">
                <span class="font-semibold text-xl w-24">Цена:</span>
                <span class="text-xl">{{ product.price }} руб.</span>
              </div>
              <div class="flex gap-4 items-baseline">
                <span class="font-semibold text-xl w-24">Вес:</span>
                <span class="text-xl">{{ product.weight }} гр.</span>
              </div>
              <!-- НОВАЯ СТРОКА: цена за кг -->
              <div class="flex gap-4 items-baseline">
                <span class="font-semibold text-xl w-24">Цена за кг:</span>
                <span class="text-xl">{{ pricePerKg }} руб.</span>
              </div>
              <div class="flex gap-4 items-baseline" v-if="product.expiration_date">
                <span class="font-semibold text-xl w-24">Срок годности:</span>
                <span class="text-xl">{{
                  new Date(product.expiration_date).toLocaleDateString('ru-RU')
                }}</span>
              </div>
              <div class="flex flex-col gap-1" v-if="product.cooking_info">
                <span class="font-semibold text-xl">Приготовление:</span>
                <span class="text-xl break-words">{{ product.cooking_info }}</span>
              </div>
            </div>

            <!-- Оценки -->
            <div class="grid grid-cols-2 gap-8 mb-8">
              <div>
                <p class="text-base text-gray-500 mb-2">Общая оценка</p>
                <div class="flex items-center gap-2">
                  <img
                    v-for="i in 5"
                    :key="'avg' + i"
                    :src="i <= averageRating ? '/Star_on.svg' : '/Star_off.svg'"
                    class="w-8 h-8"
                  />
                  <span class="ml-2 text-xl font-semibold text-gray-700">{{
                    averageRating ? averageRating + '/5' : 'нет оценок'
                  }}</span>
                </div>
              </div>
              <div>
                <p class="text-base text-gray-500 mb-2">Ваша оценка</p>
                <div class="flex items-center gap-2">
                  <img
                    v-for="i in 5"
                    :key="'user' + i"
                    :src="i <= userRating ? '/Star_on.svg' : '/Star_off.svg'"
                    class="w-8 h-8 cursor-pointer transition hover:scale-110"
                    @click="rateProduct(i)"
                  />
                  <span class="ml-2 text-xl font-semibold text-gray-700">{{
                    userRating ? userRating + '/5' : 'не оценено'
                  }}</span>
                </div>
              </div>
            </div>
          </div>
        </transition>
      </div>

      <!-- Похожие товары -->
      <transition name="slide-up" appear>
        <div v-if="relatedProducts.length" class="mt-12">
          <h3 class="text-2xl font-semibold mb-6">Похожие товары</h3>
          <div class="grid grid-cols-2 gap-6">
            <div
              v-for="rel in relatedProducts"
              :key="rel.product_id"
              class="flex items-center gap-4 border rounded-lg p-4 cursor-pointer hover:shadow transition bg-white"
              @click="$router.push(`/product/${rel.product_id}`)"
            >
              <img :src="rel.image_url" :alt="rel.name" class="w-24 h-24 object-contain rounded" />
              <p class="font-medium text-lg">{{ rel.name }}</p>
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

// Вычисляемое свойство для нового URL картинки продукта
const productImage = computed(() => {
  if (!product.value?.image_url) return ''
  const url = product.value.image_url
  const lastDot = url.lastIndexOf('.')
  if (lastDot === -1) return url
  const base = url.substring(0, lastDot)
  const ext = url.substring(lastDot)
  return `${base}_1${ext}`
})

// НОВОЕ: цена за кг
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

const updateLocalState = () => {
  if (!product.value) return
  const item = cartItems.value.find((i) => i.product_id === product.value.product_id)
  cartQuantity.value = item ? item.quantity : 0
  isFavorite.value = favorites.value.some((fav) => fav.product_id === product.value.product_id)
}

const handleIncrement = async () => {
  if (cartQuantity.value >= 15) return
  const token = localStorage.getItem('access_token')
  if (!token) {
    alert('Необходимо авторизоваться')
    return
  }
  try {
    if (cartQuantity.value > 0) {
      const item = cartItems.value.find((i) => i.product_id === product.value.product_id)
      if (item) await updateCartItem(item.cart_item_id, item.quantity + 1)
    } else {
      await addToCart(product.value.product_id, 1)
    }
    await fetchCart()
    updateLocalState()
  } catch {
    alert('Ошибка')
  }
}

const handleDecrement = async () => {
  const token = localStorage.getItem('access_token')
  if (!token) return
  try {
    const item = cartItems.value.find((i) => i.product_id === product.value.product_id)
    if (item) {
      if (item.quantity > 1) {
        await updateCartItem(item.cart_item_id, item.quantity - 1)
      } else {
        await removeFromCart(item.cart_item_id)
      }
    }
    await fetchCart()
    updateLocalState()
  } catch {
    alert('Ошибка')
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
/* Анимация прозрачности */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.4s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Анимация выезда снизу */
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
