<script setup lang="ts">
// Formulaire de signature SES avec canvas (image base64) + nom/email
const props = defineProps<{ quoteId: string | null | undefined }>()
const emit = defineEmits<{ (e: 'submitted'): void }>()
const loading = ref(false)

const canvasRef = ref<HTMLCanvasElement | null>(null)
const drawing = ref(false)
const state = reactive({ signer_name: '', method: 'draw' as 'draw' | 'upload', file: null as File | null })

const validate = (s: typeof state) => {
  const errors: { path: string; message: string }[] = []
  if (!s.signer_name || !s.signer_name.trim()) {
    errors.push({ path: 'signer_name', message: 'Nom complet requis.' })
  }
  if (s.method === 'upload' && !state.file) {
    errors.push({ path: 'file', message: 'Veuillez sélectionner une image de signature.' })
  }
  return errors
}

const clearCanvas = () => {
  const c = canvasRef.value
  if (!c) return
  const ctx = c.getContext('2d')!
  ctx.fillStyle = '#fff'
  ctx.fillRect(0, 0, c.width, c.height)
}

let unbindCanvas: null | (() => void) = null

function setupCanvas() {
  const c = canvasRef.value
  if (!c) return
  c.width = 640
  c.height = 180
  clearCanvas()
  const ctx = c.getContext('2d')!
  ctx.lineWidth = 2
  ctx.lineCap = 'round'
  const onDown = (e: PointerEvent) => {
    drawing.value = true
    ctx.beginPath()
    ctx.moveTo(e.offsetX, e.offsetY)
  }
  const onMove = (e: PointerEvent) => {
    if (!drawing.value) return
    ctx.lineTo(e.offsetX, e.offsetY)
    ctx.stroke()
  }
  const onUp = () => {
    drawing.value = false
  }
  c.addEventListener('pointerdown', onDown)
  c.addEventListener('pointermove', onMove)
  window.addEventListener('pointerup', onUp)
  unbindCanvas = () => {
    c.removeEventListener('pointerdown', onDown)
    c.removeEventListener('pointermove', onMove)
    window.removeEventListener('pointerup', onUp)
  }
}

onMounted(() => {
  if (state.method === 'draw') {
    nextTick(() => setupCanvas())
  }
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
