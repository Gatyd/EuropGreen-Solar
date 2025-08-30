<script setup lang="ts">
// Champ de signature réutilisable (dessin sur canvas ou upload image), inspiré de components/quote/SignatureForm.vue
// Props
const props = defineProps<{
    label?: string
    required?: boolean
    modelValue?: { signer_name: string; method: 'draw' | 'upload'; dataUrl?: string; file?: File | null }
}>()

const emit = defineEmits<{
    (e: 'update:modelValue', v: { signer_name: string; method: 'draw' | 'upload'; dataUrl?: string; file?: File | null }): void
}>()

// Etat local
const state = reactive({
    signer_name: props.modelValue?.signer_name || '',
    method: (props.modelValue?.method || 'draw') as 'draw' | 'upload',
    file: (props.modelValue?.file || null) as File | null,
    dataUrl: props.modelValue?.dataUrl || '',
})

watch(state, (v) => emit('update:modelValue', { ...v }), { deep: true })

// Canvas drawing (responsive DPR aware)
const canvasRef = ref<HTMLCanvasElement | null>(null)
const drawing = ref(false)
const hasDrawn = ref(false)
const DRAW_BREAKPOINT = 1024
const currentMode = ref<'mobile' | 'desktop'>(typeof window !== 'undefined' && window.innerWidth <= DRAW_BREAKPOINT ? 'mobile' : 'desktop')

let unbindCanvas: null | (() => void) = null
let unbindResize: null | (() => void) = null

const computeMode = () => (window.innerWidth <= DRAW_BREAKPOINT ? 'mobile' : 'desktop')

const clearCanvas = () => {
    const c = canvasRef.value
    if (!c) return
    const ctx = c.getContext('2d')!
    ctx.save()
    ctx.setTransform(1, 0, 0, 1, 0, 0)
    ctx.clearRect(0, 0, c.width, c.height)
    ctx.fillStyle = '#fff'
    ctx.fillRect(0, 0, c.width, c.height)
    ctx.restore()
    hasDrawn.value = false
    state.dataUrl = ''
}

function setupCanvas() {
    const c = canvasRef.value
    if (!c) return

    const mode = currentMode.value

    if (mode === 'mobile') {
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
            state.dataUrl = c.toDataURL('image/png')
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
        const onUp = () => { drawing.value = false; state.dataUrl = c.toDataURL('image/png') }

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
        if (state.method === 'draw') nextTick(() => setupCanvas())
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
    if (prev === 'draw' && unbindCanvas) { unbindCanvas(); unbindCanvas = null }
    if (val === 'draw') nextTick(() => setupCanvas())
})

onBeforeUnmount(() => {
    if (unbindCanvas) { unbindCanvas(); unbindCanvas = null }
    if (unbindResize) { unbindResize(); unbindResize = null }
})

// Validation locale pour UFormField
const validate = () => {
    const errors: { name: string; message: string }[] = []
    if (props.required && !state.signer_name.trim()) {
        errors.push({ name: 'signer_name', message: 'Nom complet requis.' })
    }
    if (props.required && state.method === 'upload' && !state.file) {
        errors.push({ name: 'file', message: 'Veuillez sélectionner une image de signature.' })
    }
    if (props.required && state.method === 'draw' && !hasDrawn.value) {
        errors.push({ name: 'signature', message: 'Veuillez dessiner votre signature.' })
    }
    return errors
}
</script>

<template>
    <UForm :state="state" :validate="validate" class="space-y-3">
        <UFormField name="signer_name" :label="label || 'Nom du signataire'" :required="required">
            <UInput v-model="state.signer_name" class="w-full" />
        </UFormField>

        <UFormField name="method" label="Méthode">
            <USelect v-model="state.method" class="w-full"
                :items="[{ label: 'Dessiner', value: 'draw' }, { label: 'Uploader une image', value: 'upload' }]" />
        </UFormField>

        <div v-if="state.method === 'upload'">
            <UFormField name="file" label="Image de signature (png/jpg)">
                <UFileUpload class="h-[180px]" v-model="state.file" accept="image/png,image/jpeg" :multiple="false" />
            </UFormField>
        </div>

        <UFormField v-else name="signature" label="Signature (dessin)">
            <div class="border rounded-md p-2 bg-white">
                <canvas ref="canvasRef" class="w-full h-[180px] touch-none select-none"></canvas>
                <div class="mt-2">
                    <UButton type="button" size="xs" variant="soft" @click="clearCanvas">Effacer</UButton>
                </div>
            </div>
        </UFormField>
    </UForm>
</template>
