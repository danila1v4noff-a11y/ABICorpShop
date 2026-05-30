<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
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

const localCart = reactive({})

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
    products.value = response.data
    restoreLocalCart()
  } catch (err) {
    console.error('Ошибка загрузки товаров:', err)
  } finally {
    loading.value = false
  }
}

const restoreLocalCart = () => {
  for (const item of cartItems.value) {
    if (item.batch_id) {
      localCart[item.batch_id] = item.quantity
    }
  }
}

const isProductInFavorites = (productId) =>
  favorites.value.some((fav) => fav.product_id === productId)

const handleAddToCart = async (productId, batchId, batchQuantity) => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    alert('Для добавления в корзину необходимо авторизоваться')
    return
  }
  const currentQty = localCart[batchId] || 0
  if (currentQty >= 15 || currentQty >= batchQuantity) return

  try {
    const item = cartItems.value.find((i) => i.batch_id === batchId)
    if (item) {
      await updateCartItem(item.cart_item_id, item.quantity + 1)
    } else {
      await addToCart(productId, batchId, 1)
    }
    localCart[batchId] = (localCart[batchId] || 0) + 1
    await fetchCart()
  } catch {
    alert('Не удалось изменить количество')
  }
}

const handleDecrement = async (productId, batchId) => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    alert('Для изменения корзины необходимо авторизоваться')
    return
  }
  const currentQty = localCart[batchId] || 0
  if (currentQty <= 0) return

  try {
    const item = cartItems.value.find((i) => i.batch_id === batchId)
    if (!item) return
    if (item.quantity > 1) {
      await updateCartItem(item.cart_item_id, item.quantity - 1)
    } else {
      await removeFromCart(item.cart_item_id)
    }
    localCart[batchId] = Math.max(0, currentQty - 1)
    await fetchCart()
  } catch {
    alert('Не удалось изменить количество')
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
  } catch {
    alert('Не удалось изменить избранное')
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
    await loadProducts()
  } else {
    await loadProducts()
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
        v-for="batch in products"
        :key="batch.batch_id"
        :productId="batch.product_id"
        :batchId="batch.batch_id"
        :title="batch.product_name"
        :imageUrl="batch.image_url"
        :price="batch.price"
        :wheight="batch.weight"
        :cartQuantity="localCart[batch.batch_id] || 0"
        :isAdded="(localCart[batch.batch_id] || 0) > 0"
        :isFavorite="isProductInFavorites(batch.product_id)"
        :hasExpiring="batch.has_expiring"
        :quantity="batch.quantity"
        :expirationDate="batch.expiration_date"
        :onClickAdd="() => handleAddToCart(batch.product_id, batch.batch_id, batch.quantity)"
        :onClickDecrement="() => handleDecrement(batch.product_id, batch.batch_id)"
        :onClickFavorite="() => handleToggleFavorite(batch.product_id)"
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
