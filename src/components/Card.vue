<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()

const props = defineProps({
  productId: { type: Number, required: true },
  title: String,
  imageUrl: String,
  price: Number,
  wheight: Number,
  cartQuantity: { type: Number, default: 0 },
  isAdded: Boolean,
  isFavorite: Boolean,
  hasExpiring: { type: Boolean, default: false },
  onClickAdd: Function,
  onClickDecrement: Function,
  onClickFavorite: Function,
})

const goToProduct = () => {
  router.push(`/product/${props.productId}`)
}
</script>

<template>
  <div
    class="relative bg-white m-10 border border-slate-100 rounded-xl p-8 cursor-pointer hover:-translate-y-2 hover:shadow-xl transition flex flex-col overflow-visible"
    :class="{ 'opacity-60 grayscale': cartQuantity >= 15 }"
    @click="goToProduct"
  >
    <!-- Значок "Скоро истекает" (центр в левом верхнем углу) -->
    <img
      v-if="hasExpiring"
      src="/Sale.svg"
      alt="Скоро истекает"
      class="absolute top-0 left-0 transform -translate-x-1/2 -translate-y-1/2 w-36 h-36 z-10"
    />

    <img :src="imageUrl" alt="Product" class="mx-auto h-40 object-contain" />

    <p class="font-bold mt-5 text-center min-h-[3rem]">{{ title }}</p>

    <div class="flex justify-center gap-4 text-gray-500 mt-2">
      <!-- Цена со скидкой -->
      <template v-if="hasExpiring">
        <span class="line-through text-red-400">{{ price }} руб.</span>
        <span class="font-semibold text-gray-800">{{ Math.round(price * 0.6) }} руб.</span>
      </template>
      <template v-else>
        <span>{{ price }} руб.</span>
      </template>
      <span>{{ wheight }} гр.</span>
    </div>

    <!-- Кнопки (клик по ним не вызывает переход) -->
    <div class="flex justify-center gap-2 mt-auto pt-4" @click.stop>
      <div v-if="cartQuantity > 0" class="flex items-center gap-3">
        <!-- ПЛЮС (скрыт, если >= 15) -->
        <img
          v-if="cartQuantity < 15"
          @click="onClickAdd"
          src="/Plus_Main.svg"
          alt="Plus"
          class="w-6 h-6 cursor-pointer transition duration-100 active:scale-90"
        />
        <span class="text-lg font-semibold">{{ cartQuantity }}</span>
        <!-- МИНУС (всегда) -->
        <img
          @click="onClickDecrement"
          src="/Minus_Main.svg"
          alt="Minus"
          class="w-6 h-6 cursor-pointer transition duration-100 active:scale-90"
        />
      </div>
      <img
        v-else
        @click="onClickAdd"
        src="/ButtonOrder_off.svg"
        class="cursor-pointer transition duration-100 active:scale-90"
      />

      <img
        @click="onClickFavorite"
        :src="isFavorite ? '/ButtonSave_on.svg' : '/ButtonSave_off.svg'"
        alt="Favorite"
        class="cursor-pointer transition duration-100 active:scale-90"
      />
    </div>

    <!-- Сообщение о лимите -->
    <transition name="fade">
      <div
        v-if="cartQuantity >= 15"
        class="absolute inset-0 flex items-center justify-center z-20 pointer-events-none"
      >
        <p class="text-red-600 text-xl font-bold">Товара больше добавить нельзя</p>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
