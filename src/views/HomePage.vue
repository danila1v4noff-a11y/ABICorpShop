<script setup>
import { ref } from 'vue'
import Header from '../components/Header.vue'
import CardList from '../components/CardList.vue'
import Drawer from '../components/Drawer.vue'
import Footer from '../components/Footer.vue'

const isDrawerOpen = ref(false)
const searchQuery = ref('')
const selectedCategoryNames = ref([])
const dateFrom = ref('')
const dateTo = ref('')

const toggleDrawer = () => {
  isDrawerOpen.value = !isDrawerOpen.value
}

const onSearchUpdate = (query) => {
  searchQuery.value = query
}

const onApplyFilters = (filters) => {
  selectedCategoryNames.value = [...filters.categories]
  dateFrom.value = filters.dateFrom
  dateTo.value = filters.dateTo
}
</script>

<template>
  <div class="flex flex-col min-h-screen">
    <Header @toggle-drawer="toggleDrawer" @update:search-query="onSearchUpdate" />
    <div class="flex-1 relative">
      <!-- Коллажи (скрыты на мобильных) -->
      <transition name="fade" appear>
        <img
          src="/ICONSBACK.svg"
          alt=""
          class="hidden sm:block absolute bottom-0 left-0 w-48 md:w-64 lg:w-80 h-auto opacity-80 pointer-events-none"
        />
      </transition>
      <transition name="fade" appear>
        <img
          src="/ICONSBACK.svg"
          alt=""
          class="hidden sm:block absolute bottom-0 right-0 w-48 md:w-64 lg:w-80 h-auto opacity-80 pointer-events-none scale-x-[-1]"
        />
      </transition>
      <!-- Карточки товаров -->
      <CardList
        :search-query="searchQuery"
        :category-names="selectedCategoryNames"
        :date-from="dateFrom"
        :date-to="dateTo"
      />
    </div>
    <Footer />
    <Drawer :isOpen="isDrawerOpen" @close="isDrawerOpen = false" @apply-filters="onApplyFilters" />
  </div>
</template>

<style scoped>
.fade-enter-active {
  transition: opacity 1s ease;
}
.fade-enter-from {
  opacity: 0;
}
</style>
