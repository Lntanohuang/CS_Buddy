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
      'is-sidebar-open': !layoutStore.isCollapse,
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
  --sidebar-rail-width: 72px;
  min-height: 100dvh;
  background:
    radial-gradient(circle at top right, rgba(232, 192, 122, 0.2), transparent 28%),
    radial-gradient(circle at bottom left, rgba(74, 124, 111, 0.12), transparent 24%),
    var(--bg-primary);
  overflow: hidden;
}

.basic-layout__main {
  margin-left: var(--sidebar-rail-width);
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.basic-layout__content {
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding: 0 28px 28px;
}

.basic-layout__mask {
  position: fixed;
  inset: 0;
  z-index: 38;
  border: none;
  background: rgba(55, 53, 47, 0.3);
}

@media (max-width: 959px) {
  .basic-layout__main {
    margin-left: 0;
  }

  .basic-layout__content {
    padding: 0 16px 16px;
  }
}
</style>
