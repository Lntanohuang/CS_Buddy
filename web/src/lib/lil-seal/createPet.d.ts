export type PetSpeechMode = 'normal' | 'excited' | 'soft' | 'surprised'

export interface PetPosition {
  strategy?: 'fixed' | 'absolute'
  top?: string
  right?: string
  bottom?: string
  left?: string
  scale?: number
  zIndex?: number
}

export interface PetController {
  mount(target?: Element | string | null): Promise<PetController>
  destroy(): PetController
  show(): PetController
  hide(): PetController
  play(actionId: string): boolean
  talk(options?: {
    mode?: PetSpeechMode
    text?: string
    continuous?: boolean
    onFinish?: () => void
    onText?: (text: string, char: string, index: number) => void
  }): boolean
  say(
    text: string,
    options?: {
      mode?: PetSpeechMode
      onFinish?: () => void
      onText?: (text: string, char: string, index: number) => void
    },
  ): boolean
  stopAction(): PetController
  sleep(): PetController
  wake(): PetController
  setPosition(position?: PetPosition): PetController
  readonly element: HTMLElement | null
  readonly mounted: boolean
  readonly ready: Promise<PetController>
}

export interface CreatePetOptions {
  mount?: Element | string | null
  assetBase?: string | URL
  assetManifest?: unknown
  hidden?: boolean
  labels?: {
    idle?: string
    sleep?: string
  }
  position?: PetPosition
}

export function createPet(options?: CreatePetOptions): PetController

export default createPet
