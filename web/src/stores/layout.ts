import { ref } from 'vue'
import { defineStore } from 'pinia'

function getInitialCollapseState() {
  return true
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
