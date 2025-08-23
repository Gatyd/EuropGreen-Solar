<script setup lang="ts">
// Formulaire de signature SES avec canvas (image base64) + nom/email
const props = defineProps<{ quoteId: string | null | undefined }>()
const emit = defineEmits<{ (e: 'submitted'): void }>()
const loading = ref(false)

const canvasRef = ref<HTMLCanvasElement | null>(null)
const drawing = ref(false)
const hasDrawn = ref(false)
const DRAW_BREAKPOINT = 1024 // px, phones/tablettes <= 1024, desktop > 1024
const currentMode = ref<'mobile' | 'desktop'>(typeof window !== 'undefined' && window.innerWidth <= DRAW_BREAKPOINT ? 'mobile' : 'desktop')
const state = reactive({ signer_name: '', method: 'draw' as 'draw' | 'upload', file: null as File | null })

const validate = (s: typeof state) => {
  const errors: { name: string; message: string }[] = []
  if (!s.signer_name || !s.signer_name.trim()) {
    errors.push({ name: 'signer_name', message: 'Nom complet requis.' })
  }
  if (s.method === 'upload' && !state.file) {
    errors.push({ name: 'file', message: 'Veuillez sélectionner une image de signature.' })
  }
  if (s.method === 'draw' && !hasDrawn.value) {
    errors.push({ name: 'signature', message: 'Veuillez dessiner votre signature.' })
  }
  return errors
}

const clearCanvas = () => {
  const c = canvasRef.value
  if (!c) return
  const ctx = c.getContext('2d')!
  // Remplir un fond blanc en tenant compte d'un éventuel scale (DPR)
  ctx.save()
  ctx.setTransform(1, 0, 0, 1, 0, 0)
  ctx.clearRect(0, 0, c.width, c.height)
  ctx.fillStyle = '#fff'
  ctx.fillRect(0, 0, c.width, c.height)
  ctx.restore()
  hasDrawn.value = false
}

let unbindCanvas: null | (() => void) = null
let unbindResize: null | (() => void) = null

const computeMode = () => (window.innerWidth <= DRAW_BREAKPOINT ? 'mobile' : 'desktop')

function setupCanvas() {
  const c = canvasRef.value
  if (!c) return

  const mode = currentMode.value

  if (mode === 'mobile') {
    // Mode mobile/tablette: normalisation des coords + DPR
    const dpr = Math.max(1, window.devicePixelRatio || 1)
    const rect = c.getBoundingClientRect()
    const cssWidth = rect.width || 640
    const cssHeight = rect.height || 180

    c.width = Math.round(cssWidth * dpr)
    c.height = Math.round(cssHeight * dpr)

    const ctx = c.getContext('2d')!
    ctx.setTransform(1, 0, 0, 1, 0, 0)
    ctx.scale(dpr, dpr)

    clearCanvas()

    ctx.lineWidth = 2
    ctx.lineCap = 'round'

    const getPos = (e: PointerEvent) => {
      const r = c.getBoundingClientRect()
      return { x: e.clientX - r.left, y: e.clientY - r.top }
    }

    const onDown = (e: PointerEvent) => {
      e.preventDefault()
      drawing.value = true
      const { x, y } = getPos(e)
      ctx.beginPath()
      ctx.moveTo(x, y)
      try { c.setPointerCapture?.(e.pointerId) } catch { }
    }
    const onMove = (e: PointerEvent) => {
      if (!drawing.value) return
      e.preventDefault()
      const { x, y } = getPos(e)
      hasDrawn.value = true
      ctx.lineTo(x, y)
      ctx.stroke()
    }
    const onUp = (e?: PointerEvent) => {
      drawing.value = false
      try { if (e) c.releasePointerCapture?.(e.pointerId) } catch { }
    }

    c.addEventListener('pointerdown', onDown, { passive: false })
    c.addEventListener('pointermove', onMove, { passive: false })
    window.addEventListener('pointerup', onUp)
    window.addEventListener('pointercancel', onUp)

    unbindCanvas = () => {
      c.removeEventListener('pointerdown', onDown as any)
      c.removeEventListener('pointermove', onMove as any)
      window.removeEventListener('pointerup', onUp as any)
      window.removeEventListener('pointercancel', onUp as any)
    }
  } else {
    // Mode desktop: ancien comportement simple
    c.width = 640
    c.height = 180

    const ctx = c.getContext('2d')!
    clearCanvas()
    ctx.lineWidth = 2
    ctx.lineCap = 'round'

    const onDown = (e: PointerEvent) => {
      drawing.value = true
      ctx.beginPath()
      ctx.moveTo(e.offsetX, e.offsetY)
    }
    const onMove = (e: PointerEvent) => {
      if (!drawing.value) return
      hasDrawn.value = true
      ctx.lineTo(e.offsetX, e.offsetY)
      ctx.stroke()
    }
    const onUp = () => { drawing.value = false }

    c.addEventListener('pointerdown', onDown)
    c.addEventListener('pointermove', onMove)
    window.addEventListener('pointerup', onUp)

    unbindCanvas = () => {
      c.removeEventListener('pointerdown', onDown as any)
      c.removeEventListener('pointermove', onMove as any)
      window.removeEventListener('pointerup', onUp as any)
    }
  }
}

onMounted(() => {
  const init = () => {
    currentMode.value = computeMode()
    if (state.method === 'draw') {
      nextTick(() => setupCanvas())
    }
  }
  init()
  const onResize = () => {
    const newMode = computeMode()
    const modeChanged = newMode !== currentMode.value
    if (modeChanged || newMode === 'mobile') {
      if (unbindCanvas) { unbindCanvas(); unbindCanvas = null }
      currentMode.value = newMode
      nextTick(() => setupCanvas())
    }
  }
  window.addEventListener('resize', onResize)
  unbindResize = () => window.removeEventListener('resize', onResize)
})

watch(() => state.method, (val, prev) => {
  if (prev === 'draw' && unbindCanvas) {
    unbindCanvas()
    unbindCanvas = null
  }
  if (val === 'draw') {
    nextTick(() => setupCanvas())
  }
})

onBeforeUnmount(() => {
  if (unbindCanvas) {
    unbindCanvas()
    unbindCanvas = null
  }
  if (unbindResize) {
    unbindResize()
    unbindResize = null
  }
})

const onSubmit = async () => {
  if (!props.quoteId) return
  const toast = useToast()
  loading.value = true
  let res
  if (state.method === 'upload') {
    const fd = new FormData()
    fd.append('signer_name', state.signer_name)
    if (state.file) fd.append('signature_file', state.file)
    res = await apiRequest(() => $fetch(`/api/quotes/${props.quoteId}/sign/`, { method: 'POST', body: fd }), toast)
  } else {
    // Empêcher l'envoi si aucune trace n'a été dessinée
    if (!hasDrawn.value) {
      loading.value = false
      return
    }
    const dataUrl = canvasRef.value?.toDataURL('image/png') || ''
    res = await apiRequest(() => $fetch(`/api/quotes/${props.quoteId}/sign/`, {
      method: 'POST', body: {
        signer_name: state.signer_name,
        signature_image: dataUrl,
      }
    }), toast)
  }
  if (res) emit('submitted')
  loading.value = false
}
</script>

<template>
  <UForm :state="state" :validate="validate" class="space-y-5" @submit.prevent="onSubmit">
    <UFormField name="signer_name" label="Nom complet">
      <UInput v-model="state.signer_name" class="w-full" />
    </UFormField>
    <UFormField name="method" label="Méthode" class="mt-3">
      <USelect v-model="state.method" class="w-full"
        :items="[{ label: 'Dessiner', value: 'draw' }, { label: 'Uploader une image', value: 'upload' }]" />
    </UFormField>
    <div v-if="state.method === 'upload'">
      <UFormField name="file" label="Image de signature (png/jpg)" class="mt-3">
        <UFileUpload class="h-[180px]" v-model="state.file" accept="image/png,image/jpeg" :multiple="false" />
      </UFormField>
    </div>
    <UFormField v-else name="signature" label="Signature (dessin)">
      <div v-if="state.method === 'draw'" class="border rounded-md p-2 bg-white">
        <canvas ref="canvasRef" class="w-full h-[180px] touch-none select-none"></canvas>
        <div class="mt-2">
          <UButton type="button" size="xs" variant="soft" @click="clearCanvas">Effacer</UButton>
        </div>
      </div>
      <div v-else class="text-gray-500 text-sm">Choisissez un fichier image à uploader.</div>
    </UFormField>
    <div class="mt-4">
      <UButton type="submit" :loading="loading" color="primary" label="Signer le devis" />
    </div>
  </UForm>
</template>
