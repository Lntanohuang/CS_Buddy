import { ref } from 'vue'
import { defineStore } from 'pinia'

function getInitialCollapseState() {
  if (typeof window === 'undefined') return false
  return window.innerWidth < 960
}

export const useLayoutStore = defineStore('layout', () => {
  const isCollapse = ref(getInitialCollapseState())

  function toggleCollapse() {
    isCollapse.value = !isCollapse.value
  }

  function setCollapse(value: boolean) {
    isCollapse.value = value
  }

  return {
    isCollapse,
    toggleCollapse,
    setCollapse,
  }
})
