<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import Sidebar from './components/Sidebar.vue'
import Topbar from './components/Topbar.vue'
import { useLayoutStore } from '@/stores/layout'
import { useUserStore } from '@/stores/user'

const layoutStore = useLayoutStore()
const userStore = useUserStore()
const isMobile = ref(typeof window !== 'undefined' ? window.innerWidth < 960 : false)

function handleResize() {
  if (typeof window === 'undefined') return
  isMobile.value = window.innerWidth < 960

  if (isMobile.value) {
    layoutStore.setCollapse(true)
  }
}

onMounted(() => {
  userStore.fetchMockUserData()

  if (typeof window !== 'undefined') {
    handleResize()
    window.addEventListener('resize', handleResize)
  }
})

onBeforeUnmount(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('resize', handleResize)
  }
})
</script>

<template>
  <div
    class="basic-layout"
    :class="{
      'is-collapse': layoutStore.isCollapse,
      'is-mobile': isMobile,
      'is-sidebar-open': isMobile && !layoutStore.isCollapse,
    }"
  >
    <Sidebar :is-mobile="isMobile" />

    <button
      v-if="isMobile && !layoutStore.isCollapse"
      class="basic-layout__mask"
      type="button"
      aria-label="关闭侧边栏"
      @click="layoutStore.setCollapse(true)"
    />

    <div class="basic-layout__main">
      <Topbar />

      <main class="basic-layout__content">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<style scoped>
.basic-layout {
  --sidebar-width: 288px;
  display: grid;
  grid-template-columns: var(--sidebar-width) minmax(0, 1fr);
  min-height: 100vh;
  background:
    radial-gradient(circle at top right, rgba(232, 192, 122, 0.2), transparent 28%),
    radial-gradient(circle at bottom left, rgba(74, 124, 111, 0.12), transparent 24%),
    var(--bg-primary);
  transition: grid-template-columns 0.28s ease;
}

.basic-layout.is-collapse {
  --sidebar-width: 104px;
}

.basic-layout__main {
  position: relative;
  min-width: 0;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.basic-layout__content {
  flex: 1;
  min-width: 0;
  padding: 0 28px 28px;
}

.basic-layout__mask {
  position: fixed;
  inset: 0;
  z-index: 30;
  border: none;
  background: rgba(55, 53, 47, 0.36);
}

@media (max-width: 959px) {
  .basic-layout {
    grid-template-columns: 1fr;
  }

  .basic-layout :deep(.sidebar) {
    position: fixed;
    inset: 0 auto 0 0;
    width: min(84vw, 304px);
    transform: translateX(-100%);
    transition: transform 0.28s ease;
  }

  .basic-layout.is-sidebar-open :deep(.sidebar) {
    transform: translateX(0);
  }

  .basic-layout__content {
    padding: 0 18px 18px;
  }
}
</style>
