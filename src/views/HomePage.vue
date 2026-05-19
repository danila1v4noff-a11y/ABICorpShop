<script setup>
import { ref } from 'vue'
import Header from '../components/Header.vue'
import CardList from '../components/CardList.vue'
import Drawer from '../components/Drawer.vue'
import Footer from '../components/Footer.vue'

const isDrawerOpen = ref(false)
const searchQuery = ref('')
const selectedCategoryNames = ref([])

const toggleDrawer = () => {
  isDrawerOpen.value = !isDrawerOpen.value
}

const onSearchUpdate = (query) => {
  searchQuery.value = query
}

const onApplyFilters = (categoryNames) => {
  selectedCategoryNames.value = [...categoryNames]
}
</script>

<template>
  <div class="flex flex-col min-h-screen">
    <Header @toggle-drawer="toggleDrawer" @update:search-query="onSearchUpdate" />
    <div class="flex-1">
      <CardList :search-query="searchQuery" :category-names="selectedCategoryNames" />
    </div>
    <Footer />
    <Drawer :isOpen="isDrawerOpen" @close="isDrawerOpen = false" @apply-filters="onApplyFilters" />
  </div>
</template>
