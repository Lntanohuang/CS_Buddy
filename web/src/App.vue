<script setup lang="ts">
import { RouterView } from 'vue-router'
import { useThemeStore } from '@/stores/theme'

useThemeStore().initTheme()
</script>

<template>
  <RouterView />
</template>
