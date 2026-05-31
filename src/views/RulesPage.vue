<template>
  <div class="min-h-screen bg-gray-100 p-4 md:p-8 relative">
    <!-- Коллаж слева с размытой тенью -->
    <transition name="fade" appear>
      <img
        src="/COLLAGEICON.svg"
        alt="коллаж слева"
        class="absolute top-0 left-0 h-full w-16 md:w-auto object-contain pointer-events-none z-0 opacity-40 md:opacity-100"
        style="filter: drop-shadow(2px 2px 8px rgba(0, 0, 0, 0.15))"
      />
    </transition>
    <!-- Коллаж справа с размытой тенью -->
    <transition name="fade" appear>
      <img
        src="/COLLAGEICON.svg"
        alt="коллаж справа"
        class="absolute top-0 right-0 h-full w-16 md:w-auto object-contain pointer-events-none z-0 opacity-40 md:opacity-100"
        style="transform: scaleX(-1); filter: drop-shadow(-2px 2px 8px rgba(0, 0, 0, 0.15))"
      />
    </transition>

    <transition name="fade" appear>
      <div class="max-w-3xl mx-auto relative z-10">
        <!-- Стрелка назад -->
        <div class="mb-4">
          <img
            src="/ArrowLeft.svg"
            alt="Назад"
            class="w-8 h-8 cursor-pointer opacity-50 hover:opacity-100 transition-opacity"
            @click="$router.back()"
          />
        </div>

        <div class="bg-white rounded-xl shadow-lg p-4 md:p-8">
          <h1 class="text-2xl md:text-3xl font-bold text-gray-800 mb-6 md:mb-8">
            Правила пользования магазином
          </h1>
          <div class="space-y-6 text-gray-700 leading-relaxed text-sm md:text-base">
            <section>
              <h2 class="text-lg md:text-xl font-semibold text-gray-800 mb-3">
                1. Общие положения
              </h2>
              <p>1.1. Корпоративный магазин предназначен исключительно для сотрудников АО «АБИ».</p>
              <p>
                1.2. Каждый сотрудник несёт личную ответственность за действия, совершённые под его
                учётной записью.
              </p>
              <p>
                1.3. Администрация оставляет за собой право временно или постоянно ограничить доступ
                к магазину при нарушении настоящих правил.
              </p>
            </section>
            <section>
              <h2 class="text-lg md:text-xl font-semibold text-gray-800 mb-3">
                2. Оформление заказа
              </h2>
              <p>
                2.1. Заказ может быть оформлен только в пределах доступного остатка товаров и не
                должен превышать 25 кг общего веса.
              </p>
              <p>2.2. Количество одного наименования в заказе не может превышать 15 штук.</p>
              <p>
                2.3. При совместном использовании корзины ответственность за состав заказа несёт
                владелец корзины.
              </p>
            </section>
            <section>
              <h2 class="text-lg md:text-xl font-semibold text-gray-800 mb-3">
                3. Получение заказа
              </h2>
              <p>3.1. Заказ необходимо забрать в выбранный временной интервал.</p>
              <p>
                3.2. При доставке в офис заказ доставляется согласно расписанию доставки выбранного
                офиса.
              </p>
              <p>3.3. Сотрудник обязан лично получить заказ или уполномочить доверенное лицо.</p>
            </section>
            <section>
              <h2 class="text-lg md:text-xl font-semibold text-gray-800 mb-3">4. Отмена заказа</h2>
              <p>4.1. Отменить заказ можно до того, как менеджер принял его в обработку.</p>
              <p>
                4.2. Для отмены принятого заказа необходимо обратиться к менеджеру с объяснением
                причины.
              </p>
              <p>
                4.3. Частые отмены могут служить основанием для временной блокировки учётной записи.
              </p>
            </section>
            <section>
              <h2 class="text-lg md:text-xl font-semibold text-gray-800 mb-3">
                5. Оценки и отзывы
              </h2>
              <p>5.1. Оценка товаров помогает формировать объективный рейтинг продукции.</p>
              <p>5.2. Запрещается намеренно занижать или завышать оценки.</p>
            </section>
            <section>
              <h2 class="text-lg md:text-xl font-semibold text-gray-800 mb-3">
                6. Ответственность и блокировка
              </h2>
              <p>
                6.1. Менеджер вправе добавить сотрудника в чёрный список при систематическом
                нарушении правил.
              </p>
              <p>6.2. Блокировка накладывается с обязательным указанием причины.</p>
              <p>6.3. Разблокировка производится только менеджером после устранения причины.</p>
            </section>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.fade-enter-active {
  transition: opacity 0.8s ease;
}
.fade-enter-from {
  opacity: 0;
}
</style>
