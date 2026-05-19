<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

defineProps({ isOpen: Boolean })
const emit = defineEmits(['close', 'apply-filters'])

const categories = ref([])
const selectedCategoryNames = ref([]) // массив названий

onMounted(async () => {
  try {
    const resp = await axios.get('http://127.0.0.1:8000/api/v1/categories/')
    categories.value = resp.data
  } catch (e) {
    console.error('Ошибка загрузки категорий')
  }
})

const toggleCategory = (categoryName) => {
  const index = selectedCategoryNames.value.indexOf(categoryName)
  if (index === -1) {
    selectedCategoryNames.value.push(categoryName)
  } else {
    selectedCategoryNames.value.splice(index, 1)
  }
}

const applyFilters = () => {
  emit('apply-filters', [...selectedCategoryNames.value])
  emit('close')
}
</script>

<template>
  <div
    v-show="isOpen"
    class="bg-white w-96 fixed right-4 top-[calc(50%+65px)] transform -translate-y-1/2 rounded-2xl shadow-xl p-8 z-20"
  >
    <div class="flex items-center gap-4 mb-6">
      <img
        class="opacity-30 cursor-pointer hover:opacity-100 transition hover:-translate-x-1"
        src="/ArrowLeft.svg"
        alt="Close"
        @click="emit('close')"
      />
      <h2 class="text-2xl font-bold text-[#4F0B26]">Фильтры</h2>
    </div>

    <div class="space-y-4">
      <label
        v-for="cat in categories"
        :key="cat.category_id"
        class="flex items-center gap-3 cursor-pointer"
      >
        <input
          type="checkbox"
          :value="cat.name"
          :checked="selectedCategoryNames.includes(cat.name)"
          @change="toggleCategory(cat.name)"
          class="w-5 h-5"
        />
        <span>{{ cat.name }}</span>
      </label>
    </div>

    <div class="mt-8">
      <button
        @click="applyFilters"
        class="w-full py-2 bg-[#4F0B26] text-white rounded-full hover:bg-[#3a0920] transition-colors duration-200"
      >
        Применить
      </button>
    </div>
  </div>
</template>
