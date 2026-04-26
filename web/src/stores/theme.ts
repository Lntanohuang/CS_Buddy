import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

export type ThemeName = 'sky' | 'rose' | 'mint' | 'sunny' | 'coral'

export interface ThemeOption {
  id: ThemeName
  label: string
  description: string
  swatches: string[]
  metaColor: string
}

const STORAGE_KEY = 'cs-buddy-theme'

export const themeOptions: ThemeOption[] = [
  {
    id: 'sky',
    label: '天空蓝',
    description: '当前默认',
    swatches: ['#5ba5ea', '#8dc8ff'],
    metaColor: '#5ba5ea',
  },
  {
    id: 'rose',
    label: '柔粉',
    description: '轻快温柔',
    swatches: ['#ec6aa0', '#f7a7c8'],
    metaColor: '#ec6aa0',
  },
  {
    id: 'mint',
    label: '薄荷绿',
    description: '清爽专注',
    swatches: ['#4fb982', '#8edeb2'],
    metaColor: '#4fb982',
  },
  {
    id: 'sunny',
    label: '暖黄色',
    description: '明亮活力',
    swatches: ['#d08a16', '#f6c95d'],
    metaColor: '#d08a16',
  },
  {
    id: 'coral',
    label: '珊瑚橙',
    description: '温暖醒目',
    swatches: ['#e66f51', '#f6a982'],
    metaColor: '#e66f51',
  },
]

function isThemeName(value: string | null): value is ThemeName {
  return themeOptions.some((theme) => theme.id === value)
}

function readStoredTheme() {
  if (typeof window === 'undefined') return 'sky'

  const storedTheme = window.localStorage.getItem(STORAGE_KEY)
  return isThemeName(storedTheme) ? storedTheme : 'sky'
}

function persistTheme(theme: ThemeName) {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(STORAGE_KEY, theme)
}

function updateMetaThemeColor(theme: ThemeName) {
  if (typeof document === 'undefined') return

  const option = themeOptions.find((item) => item.id === theme) ?? themeOptions[0]
  document.querySelector('meta[name="theme-color"]')?.setAttribute('content', option.metaColor)
}

function applyTheme(theme: ThemeName) {
  if (typeof document === 'undefined') return

  document.documentElement.dataset.theme = theme
  updateMetaThemeColor(theme)
}

export const useThemeStore = defineStore('theme', () => {
  const currentTheme = ref<ThemeName>('sky')
  const initialized = ref(false)

  const currentThemeOption = computed(
    () => themeOptions.find((theme) => theme.id === currentTheme.value) ?? themeOptions[0],
  )

  function initTheme() {
    if (initialized.value) return

    currentTheme.value = readStoredTheme()
    applyTheme(currentTheme.value)
    initialized.value = true
  }

  function setTheme(theme: ThemeName) {
    currentTheme.value = theme
    applyTheme(theme)
    persistTheme(theme)
  }

  return {
    currentTheme,
    currentThemeOption,
    themeOptions,
    initTheme,
    setTheme,
  }
})
