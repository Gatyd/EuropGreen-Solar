<script setup lang="ts">
import { toast } from '#build/ui'
import { onMounted, onBeforeUnmount, ref, watch, nextTick, markRaw } from 'vue'

type EnedisMandateDraft = Record<string, any>

const props = defineProps<{ draft: EnedisMandateDraft, mode: 'edit' | 'preview', formId?: string | number }>()
const emit = defineEmits<{ (e: 'refresh-requested'): void }>()

const loading = ref(false)
const error = ref<string | null>(null)
const lastUpdated = ref<Date | null>(null)
let abortController: AbortController | null = null
let debounceTimer: any = null
const nowTS = ref<number>(Date.now())
let nowInterval: any = null

const viewerRef = ref<HTMLDivElement | null>(null)
const pageCanvases = ref<HTMLCanvasElement[]>([])
const pageLayers = ref<HTMLDivElement[]>([])
const pdfDoc = ref<any>(null)
const totalPages = ref(0)
const pages = ref<number[]>([])
let resizeObserver: ResizeObserver | null = null
let getDocumentFn: any = null
let GlobalWorkerOptionsObj: any = null

function updateLastUpdated() { lastUpdated.value = new Date() }
function timeSince(d?: Date | null) {
    if (!d) return '—'
    const current = nowTS.value
    const secs = Math.floor((current - d.getTime()) / 1000)
    if (secs < 60) return `${secs}s`
    const mins = Math.floor(secs / 60)
    if (mins < 60) return `${mins} min`
    const hrs = Math.floor(mins / 60)
    const rem = mins % 60
    return rem > 0 ? `${hrs} h ${rem} min` : `${hrs} h`
}

async function fetchPreview(immediate = false) {
    if (debounceTimer && !immediate) clearTimeout(debounceTimer)
    if (!immediate) { debounceTimer = setTimeout(() => fetchPreview(true), 4000); return }
    if (abortController) abortController.abort()
    abortController = new AbortController()
    loading.value = true
    error.value = null
    try {
        // Construire un payload plat compatible serializer (éviter d'envoyer les objets signature)
        const d: any = props.draft || {}
        const payload: Record<string, any> = {}
        for (const k of Object.keys(d)) {
            if (k === 'client_signature' || k === 'installer_signature') continue
            if (props.formId != null) payload.form_id = String(props.formId)
            payload[k] = d[k]
        }
        if (d.client_signature?.dataUrl) payload.client_signature_data_url = d.client_signature.dataUrl
        if (d.client_signature?.signer_name) payload.client_signature_signer_name = d.client_signature.signer_name
        if (d.installer_signature?.dataUrl) payload.installer_signature_data_url = d.installer_signature.dataUrl
        if (d.installer_signature?.signer_name) payload.installer_signature_signer_name = d.installer_signature.signer_name

        const resp = await apiRequest(
            () => $fetch<Blob>(`/api/administrative/enedis-mandate/preview/`, {
                method: 'POST',
                body: payload,
                credentials: 'include',
                // @ts-ignore runtime options
                responseType: 'blob',
                signal: abortController?.signal,
            }),
            toast
        )
        if (resp instanceof Blob) {
            const arrayBuffer = await resp.arrayBuffer()
            await loadPdf(arrayBuffer)
            updateLastUpdated()
        }
    } catch (e: any) {
        error.value = e?.data?.message || e?.message || 'Erreur de chargement'
        console.log(error.value)
    } finally {
        loading.value = false
    }
}

function manualRefresh() { emit('refresh-requested'); fetchPreview(true) }

watch(() => props.draft, () => { fetchPreview(false) }, { deep: true })

onMounted(async () => {
    try {
        const core: any = await import('pdfjs-dist')
        getDocumentFn = core.getDocument
        GlobalWorkerOptionsObj = core.GlobalWorkerOptions
        const worker: any = await import('pdfjs-dist/build/pdf.worker.mjs?url')
        if (GlobalWorkerOptionsObj && worker?.default) GlobalWorkerOptionsObj.workerSrc = worker.default
    } catch { }
    nowInterval = setInterval(() => { nowTS.value = Date.now() }, 1000)
    await fetchPreview(true)
    await nextTick()
    if (viewerRef.value) {
        let ticking = false
        const rerender = () => {
            if (ticking) return; ticking = true
            requestAnimationFrame(async () => {
                if (pdfDoc.value) { for (let i = 1; i <= totalPages.value; i++) await renderSinglePage(i) }
                ticking = false
            })
        }
        resizeObserver = new ResizeObserver(rerender)
        resizeObserver.observe(viewerRef.value)
    }
})
onBeforeUnmount(() => {
    if (abortController) { try { abortController.abort() } catch { } }
    if (nowInterval) { clearInterval(nowInterval); nowInterval = null }
    if (resizeObserver && viewerRef.value) {
        try { resizeObserver.unobserve(viewerRef.value) } catch { }
        try { resizeObserver.disconnect() } catch { }
    }
    if (pdfDoc.value) { try { pdfDoc.value.destroy?.() } catch { }; try { pdfDoc.value.cleanup?.() } catch { }; pdfDoc.value = null }
})

async function loadPdf(data: ArrayBuffer) {
    if (pdfDoc.value) { try { await pdfDoc.value.destroy?.() } catch { }; try { pdfDoc.value.cleanup?.() } catch { }; pdfDoc.value = null }
    if (!getDocumentFn) throw new Error('PDF.js non chargé')
    const task = getDocumentFn({ data })
    const doc = await ((task as any).promise ?? (task as unknown as Promise<any>))
    pdfDoc.value = markRaw(doc)
    totalPages.value = pdfDoc.value.numPages
    pages.value = Array.from({ length: totalPages.value }, (_, i) => i + 1)
    await nextTick()
    for (let i = 1; i <= totalPages.value; i++) await renderSinglePage(i)
}

async function renderSinglePage(pageNumber: number) {
    if (!pdfDoc.value) return
    const canvas = pageCanvases.value[pageNumber - 1]
    if (!canvas) return
    const layerDiv = pageLayers.value[pageNumber - 1]
    const page = await pdfDoc.value.getPage(pageNumber)
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    const containerWidth = viewerRef.value?.clientWidth || 800
    const baseViewport = page.getViewport({ scale: 1 })
    const scale = Math.max(0.1, (containerWidth - 24) / baseViewport.width)
    const viewport = page.getViewport({ scale })
    canvas.width = Math.floor(viewport.width)
    canvas.height = Math.floor(viewport.height)
    const renderTask: any = page.render({ canvasContext: ctx, viewport, intent: 'display' })
    await (renderTask?.promise ?? renderTask)
    if (layerDiv) {
        try { layerDiv.innerHTML = ''; layerDiv.style.position = 'absolute'; layerDiv.style.top = '0'; layerDiv.style.left = '0'; layerDiv.style.width = `${Math.floor(viewport.width)}px`; layerDiv.style.height = `${Math.floor(viewport.height)}px` } catch { }
    }
}
</script>

<template>
    <div class="relative h-full flex flex-col">
        <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-white/60 z-10">
            <div class="flex items-center gap-2 text-gray-600">
                <span class="i-heroicons-arrow-path-20-solid animate-spin"></span>
                <span>Génération de l’aperçu…</span>
            </div>
        </div>
        <!-- <div v-if="error" class="absolute inset-0 flex items-center justify-center text-red-600">
            {{ error }}
        </div> -->
        <div ref="viewerRef" class="w-full flex-1 overflow-auto px-4">
            <div v-if="!error" class="mx-auto max-w-[1100px] flex flex-col items-center gap-6">
                <div v-for="n in pages" :key="n" class="relative bg-white shadow-xl">
                    <canvas :ref="(el: any) => pageCanvases[n - 1] = el" class="block"></canvas>
                    <div :ref="(el: any) => pageLayers[n - 1] = el" class="pointer-events-none"></div>
                </div>
            </div>
            <div v-else class="h-full w-full flex items-center justify-center text-gray-500">
                Aucun aperçu disponible
            </div>
        </div>
        <div v-if="mode === 'edit'"
            class="absolute bottom-2 left-5 right-8 z-20 flex items-center justify-between text-xs text-gray-600 pointer-events-none">
            <UButton class="pointer-events-auto" size="xs" color="neutral" icon="i-heroicons-arrow-path"
                :loading="loading" @click="manualRefresh">Actualiser</UButton>
            <div>Actualisé il y a {{ timeSince(lastUpdated) }}</div>
        </div>
    </div>
</template>
