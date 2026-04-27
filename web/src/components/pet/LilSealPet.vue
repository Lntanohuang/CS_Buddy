<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { createPet, type PetController, type PetSpeechMode } from '@/lib/lil-seal/createPet.js'
import type { LilSealAction } from './types'
import '@/lib/lil-seal/styles.css'

type NormalizedSealAction = 'idle' | 'thinking' | 'talking' | 'happy' | 'starry' | 'sleep' | 'wave'

const props = withDefaults(defineProps<{
  action?: LilSealAction
  actionKey?: string | number
  speechText?: string
  speechMode?: PetSpeechMode
  visible?: boolean
}>(), {
  action: 'idle',
  actionKey: 0,
  speechText: '',
  speechMode: 'soft',
  visible: true,
})

const mountRef = ref<HTMLDivElement | null>(null)
const ready = ref(false)
let pet: PetController | null = null
let thinkingTimer: number | undefined
let activeAction: NormalizedSealAction = 'idle'
let syncToken = 0

const speechPreview = computed(() => normalizeSpeech(props.speechText))
const showSpeech = computed(() =>
  props.visible && normalizeAction(props.action) === 'talking' && speechPreview.value.length > 0
)

onMounted(() => {
  if (!mountRef.value) return

  pet = createPet({
    mount: mountRef.value,
    assetBase: '/pet/',
    labels: {
      idle: '小海豹学习搭档',
      sleep: '小海豹睡着了',
    },
    position: {
      right: 'clamp(16px, 3vw, 32px)',
      bottom: 'clamp(96px, 13vh, 132px)',
      left: 'auto',
      scale: 0.72,
      zIndex: 42,
    },
  })

  void pet.ready.then(() => {
    ready.value = true
    syncAction(normalizeAction(props.action))
  })
})

onBeforeUnmount(() => {
  clearThinkingLoop()
  pet?.destroy()
  pet = null
})

watch(
  () => [props.action, props.actionKey, props.visible, props.speechMode] as const,
  ([nextAction]) => syncAction(normalizeAction(nextAction)),
)

function syncAction(nextAction: NormalizedSealAction) {
  const current = pet
  if (!current) return

  const token = ++syncToken
  void current.ready.then((controller) => {
    if (token !== syncToken || controller !== pet) return

    if (!props.visible) {
      clearThinkingLoop()
      controller.hide()
      activeAction = nextAction
      return
    }

    controller.show()

    if (nextAction !== 'thinking') {
      clearThinkingLoop()
    }

    switch (nextAction) {
      case 'thinking':
        startThinkingLoop(controller)
        break
      case 'talking':
        startTalking(controller)
        break
      case 'happy':
        playOneShot(controller, 'laugh')
        break
      case 'starry':
        playOneShot(controller, 'happy_star')
        break
      case 'sleep':
        controller.sleep()
        break
      case 'wave':
        playOneShot(controller, 'wave')
        break
      case 'idle':
      default:
        if (activeAction === 'talking') {
          controller.stopAction()
        }
        if (activeAction === 'sleep') {
          controller.wake()
        }
        break
    }

    activeAction = nextAction
  })
}

function startThinkingLoop(controller: PetController) {
  if (activeAction !== 'thinking') {
    controller.play('thinking')
  }

  if (thinkingTimer === undefined) {
    thinkingTimer = window.setInterval(() => {
      pet?.play('thinking')
    }, 8600)
  }
}

function startTalking(controller: PetController) {
  if (activeAction !== 'talking') {
    controller.talk({ mode: props.speechMode })
  }
}

function playOneShot(controller: PetController, actionId: string) {
  if (activeAction === 'talking') {
    controller.stopAction()
  }
  controller.play(actionId)
}

function clearThinkingLoop() {
  if (thinkingTimer !== undefined) {
    window.clearInterval(thinkingTimer)
    thinkingTimer = undefined
  }
}

function normalizeSpeech(value: string) {
  return value
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/[#>*_`[\]()|~-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(-86)
}

function normalizeAction(action: LilSealAction): NormalizedSealAction {
  if (action === 'think') return 'thinking'
  if (action === 'talk') return 'talking'
  return action
}
</script>

<template>
  <div class="lil-seal-pet" :class="{ 'is-ready': ready }">
    <div ref="mountRef" />
    <Transition name="seal-speech">
      <p v-if="showSpeech" class="lil-seal-pet__speech">
        {{ speechPreview }}
      </p>
    </Transition>
  </div>
</template>

<style scoped>
.lil-seal-pet {
  pointer-events: none;
}

.lil-seal-pet__speech {
  position: fixed;
  right: clamp(138px, 16vw, 226px);
  bottom: clamp(210px, 28vh, 278px);
  z-index: 43;
  width: max-content;
  max-width: min(280px, calc(100vw - 32px));
  margin: 0;
  padding: 10px 14px;
  border: 1px solid rgba(var(--accent-primary-rgb), 0.16);
  border-radius: 16px 16px 4px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: var(--shadow-md);
  color: var(--text-primary);
  font-size: 13px;
  line-height: 1.55;
  word-break: break-word;
}

.seal-speech-enter-active,
.seal-speech-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.seal-speech-enter-from,
.seal-speech-leave-to {
  opacity: 0;
  transform: translateY(6px) scale(0.98);
}

@media (max-width: 720px) {
  .lil-seal-pet__speech {
    right: 16px;
    bottom: 218px;
    max-width: calc(100vw - 32px);
  }
}
</style>
