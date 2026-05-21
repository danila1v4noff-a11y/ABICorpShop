<script setup>
import { ref, watch, onMounted } from 'vue'
import axios from 'axios'
import Card from './Card.vue'
import { useCart } from '../composables/useCart'
import { useFavorites } from '../composables/useFavorites'

const props = defineProps({
  searchQuery: { type: String, default: '' },
  categoryNames: { type: Array, default: () => [] },
})

const API_BASE = 'http://127.0.0.1:8000/api/v1'
const products = ref([])
const loading = ref(false)

const { cartItems, fetchCart, addToCart, updateCartItem, removeFromCart } = useCart()
const { favorites, fetchFavorites, addFavorite, removeFavorite } = useFavorites()

const loadProducts = async () => {
  loading.value = true
  try {
    const queryParts = []
    if (props.searchQuery) queryParts.push(`search=${encodeURIComponent(props.searchQuery)}`)
    if (props.categoryNames && props.categoryNames.length > 0) {
      props.categoryNames.forEach((name) =>
        queryParts.push(`category_names=${encodeURIComponent(name)}`),
      )
    }
    const queryString = queryParts.length ? `?${queryParts.join('&')}` : ''
    const response = await axios.get(`${API_BASE}/products/${queryString}`)
    products.value = response.data.sort((a, b) => {
      if (a.has_expiring && !b.has_expiring) return -1
      if (!a.has_expiring && b.has_expiring) return 1
      return a.name.localeCompare(b.name, 'ru')
    })
  } catch (err) {
    console.error('Ошибка загрузки товаров:', err)
  } finally {
    loading.value = false
  }
}

const isProductInCart = (productId) => cartItems.value.some((item) => item.product_id === productId)
const isProductInFavorites = (productId) =>
  favorites.value.some((fav) => fav.product_id === productId)
const getCartQuantity = (productId) => {
  const item = cartItems.value.find((i) => i.product_id === productId)
  return item ? item.quantity : 0
}

const handleAddToCart = async (productId) => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    alert('Для добавления в корзину необходимо авторизоваться')
    return
  }
  try {
    const item = cartItems.value.find((i) => i.product_id === productId)
    if (item) {
      await updateCartItem(item.cart_item_id, item.quantity + 1)
    } else {
      await addToCart(productId, 1)
    }
  } catch (err) {
    // Показываем конкретную причину от сервера (например, чёрный список)
    alert(err.response?.data?.detail || 'Не удалось изменить количество')
  }
}

const handleDecrement = async (productId) => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    alert('Для изменения корзины необходимо авторизоваться')
    return
  }
  try {
    const item = cartItems.value.find((i) => i.product_id === productId)
    if (item) {
      if (item.quantity > 1) {
        await updateCartItem(item.cart_item_id, item.quantity - 1)
      } else {
        await removeFromCart(item.cart_item_id)
      }
    }
  } catch (err) {
    alert(err.response?.data?.detail || 'Не удалось изменить количество')
  }
}

const handleToggleFavorite = async (productId) => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    alert('Для работы с избранным необходимо авторизоваться')
    return
  }
  try {
    if (isProductInFavorites(productId)) {
      await removeFavorite(productId)
    } else {
      await addFavorite(productId)
    }
  } catch (err) {
    alert(err.response?.data?.detail || 'Не удалось изменить избранное')
  }
}
watch(
  () => [props.searchQuery, props.categoryNames],
  () => loadProducts(),
  { immediate: true },
)

onMounted(async () => {
  const token = localStorage.getItem('access_token')
  if (token) {
    await fetchCart()
    await fetchFavorites()
  }
})
</script>

<template>
  <div class="p-10">
    <div v-if="loading" class="text-center">Загрузка товаров...</div>
    <div v-else-if="products.length === 0" class="text-center text-gray-500">Ничего не найдено</div>
    <transition-group
      v-else
      name="card-list"
      tag="div"
      class="grid grid-cols-4 justify-center"
      appear
    >
      <Card
        v-for="product in products"
        :key="product.product_id"
        :productId="product.product_id"
        :title="product.name"
        :imageUrl="product.image_url"
        :price="product.price"
        :wheight="product.weight"
        :cartQuantity="getCartQuantity(product.product_id)"
        :isAdded="isProductInCart(product.product_id)"
        :isFavorite="isProductInFavorites(product.product_id)"
        :hasExpiring="product.has_expiring"
        :onClickAdd="() => handleAddToCart(product.product_id)"
        :onClickDecrement="() => handleDecrement(product.product_id)"
        :onClickFavorite="() => handleToggleFavorite(product.product_id)"
      />
    </transition-group>
  </div>
</template>

<style scoped>
.card-list-enter-active {
  transition: all 0.4s ease-out;
}
.card-list-leave-active {
  transition: all 0.2s ease-in;
}
.card-list-enter-from {
  opacity: 0;
  transform: scale(0.9);
}
.card-list-leave-to {
  opacity: 0;
  transform: scale(0.9);
}
</style>
