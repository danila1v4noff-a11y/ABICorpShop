<template>
  <footer class="bg-[#4F0B26] text-white py-6 px-4 md:px-8">
    <div
      class="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-start md:items-center gap-4"
    >
      <div class="max-w-lg">
        <p class="text-sm md:text-xl font-extrabold leading-relaxed">
          Корпоративный магазин для лучших сотрудников по лучшим ценам
        </p>
      </div>
      <div class="flex flex-col md:flex-row items-end md:items-center gap-4">
        <div class="text-right text-xs md:text-sm space-y-1">
          <p>Контакты: +7902708294996 abi@gmail.ru</p>
          <p>Служба поддержки: +7409480342520 support@gmail.ru</p>
        </div>
        <button
          @click="scrollToTop"
          class="flex items-center gap-2 bg-white/10 hover:bg-white/20 text-white px-3 py-2 rounded-lg transition-colors text-sm mt-2 md:mt-0"
          title="Наверх"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-4 w-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M5 10l7-7m0 0l7 7m-7-7v18"
            />
          </svg>
          <span class="hidden md:inline">Наверх</span>
        </button>
      </div>
    </div>
  </footer>
</template>

<script setup>
const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>
