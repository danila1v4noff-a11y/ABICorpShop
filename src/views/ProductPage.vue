<template>
  <div class="min-h-screen bg-gray-100 p-8">
    <transition name="fade" appear>
      <div v-if="product" class="max-w-6xl mx-auto">
        <img
          src="/Logo.svg"
          alt="Логотип"
          class="absolute top-0 left-4 h-12 w-auto mt-4 cursor-pointer"
          @click="$router.push('/')"
        />
        <!-- Кнопка назад -->
        <div class="mb-4">
          <img
            src="/ArrowLeft.svg"
            alt="Назад"
            class="w-8 h-8 cursor-pointer opacity-50 hover:opacity-100 transition-opacity"
            @click="$router.back()"
          />
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <!-- Левая часть: фото и кнопки -->
          <div class="flex flex-col items-center">
            <img
              :src="product.image_url"
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

          <!-- Правая часть: информация -->
          <div>
            <h1 class="text-3xl font-bold text-gray-800 mb-4">{{ product.name }}</h1>
            <p class="text-gray-600 mb-4" v-if="product.description">{{ product.description }}</p>

            <div class="space-y-2 mb-6">
              <div class="flex gap-4">
                <span class="font-semibold">Цена:</span>
                <span>{{ product.price }} руб.</span>
              </div>
              <div class="flex gap-4">
                <span class="font-semibold">Вес:</span>
                <span>{{ product.weight }} гр.</span>
              </div>
              <div class="flex gap-4" v-if="product.expiration_date">
                <span class="font-semibold">Срок годности:</span>
                <span>{{ new Date(product.expiration_date).toLocaleDateString('ru-RU') }}</span>
              </div>
              <div class="flex gap-4" v-if="product.cooking_info">
                <span class="font-semibold">Приготовление:</span>
                <span>{{ product.cooking_info }}</span>
              </div>
            </div>

            <!-- Оценки (реальные) -->
            <div class="grid grid-cols-2 gap-6 mb-8">
              <div>
                <p class="text-sm text-gray-500 mb-1">Общая оценка</p>
                <div class="flex items-center gap-1">
                  <img
                    v-for="i in 5"
                    :key="'avg' + i"
                    :src="i <= averageRating ? '/Star_on.svg' : '/Star_off.svg'"
                    class="w-8 h-8"
                  />
                  <span class="ml-2 text-sm text-gray-600">{{
                    averageRating ? averageRating + '/5' : 'нет оценок'
                  }}</span>
                </div>
              </div>
              <div>
                <p class="text-sm text-gray-500 mb-1">Ваша оценка</p>
                <div class="flex items-center gap-1">
                  <img
                    v-for="i in 5"
                    :key="'user' + i"
                    :src="i <= userRating ? '/Star_on.svg' : '/Star_off.svg'"
                    class="w-8 h-8 cursor-pointer transition hover:scale-110"
                    @click="rateProduct(i)"
                  />
                  <span class="ml-2 text-sm text-gray-600">{{
                    userRating ? userRating + '/5' : 'не оценено'
                  }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Похожие товары -->
        <div v-if="relatedProducts.length" class="mt-12">
          <h3 class="text-xl font-semibold mb-4">Похожие товары</h3>
          <div class="grid grid-cols-2 gap-4">
            <div
              v-for="rel in relatedProducts"
              :key="rel.product_id"
              class="flex items-center gap-4 border rounded-lg p-3 cursor-pointer hover:shadow transition bg-white"
              @click="$router.push(`/product/${rel.product_id}`)"
            >
              <img :src="rel.image_url" :alt="rel.name" class="w-16 h-16 object-contain rounded" />
              <p class="font-medium">{{ rel.name }}</p>
            </div>
          </div>
        </div>
      </div>
    </transition>
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

const loadProduct = async () => {
  try {
    const [prodResp, relResp, ratingResp] = await Promise.all([
      axios.get(`http://127.0.0.1:8000/api/v1/products/${productId.value}`),
      axios.get(`http://127.0.0.1:8000/api/v1/products/${productId.value}/related`),
      axios
        .get(`http://127.0.0.1:8000/api/v1/products/${productId.value}/rating`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
        })
        .catch(() => ({ data: { average_rating: null, user_rating: 0 } })), // если не авторизован
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
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.4s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
