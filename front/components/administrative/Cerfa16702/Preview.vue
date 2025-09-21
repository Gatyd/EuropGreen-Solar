<script setup lang="ts">
import { toast } from '#build/ui'
import { onMounted, onBeforeUnmount, ref, watch, nextTick, markRaw } from 'vue'
type Cerfa16702Draft = {
    declarant_type: string
    last_name: string
    first_name: string
    birth_date: string
    birth_place: string
    birth_department: string
    birth_country: string
    company_denomination: string
    company_reason: string
    company_siret: string
    company_type: string
    address_street: string
    address_number: string
    address_lieu_dit: string
    address_locality: string
    address_postal_code: string
    address_bp: string
    address_cedex: string
    phone_country_code: string
    phone: string
    email: string
    email_consent: boolean
    land_street: string
    land_number: string
    land_lieu_dit: string
    land_locality: string
    land_postal_code: string
    cadastral_prefix: string
    cadastral_section: string
    cadastral_number: string
    cadastral_surface_m2: number | null
    project_new_construction: boolean
    project_existing_works: boolean
    project_description: string
    destination_primary_residence: boolean
    destination_secondary_residence: boolean
    agrivoltaic_project: boolean
    electrical_power_text: string
    peak_power_text: string
    energy_destination: string
    protection_site_patrimonial: boolean
    protection_site_classe_or_instance: boolean
    protection_monument_abords: boolean
    engagement_city: string
    engagement_date: string
    declarant_signature?: { signer_name: string; dataUrl?: string }
}

const props = defineProps<{
    draft: Cerfa16702Draft & {
        generated_at?: string
        declarant_signature_image_url?: string | null
        declarant_signature_signed_at?: string | null
    }
    mode?: 'print' | 'edit'
}>()

const emit = defineEmits<{ (e: 'refresh-requested'): void }>()

const loading = ref(false)
const error = ref<string | null>(null)
const lastUpdated = ref<Date | null>(null)
let abortController: AbortController | null = null
let debounceTimer: any = null
// Ticker pour rafraîchir l'horodatage "Actualisé il y a ..."
const nowTS = ref<number>(Date.now())
let nowInterval: any = null

// PDF.js minimal (pages empilées)
const viewerRef = ref<HTMLDivElement | null>(null)
const pageCanvases = ref<HTMLCanvasElement[]>([])
const pageLayers = ref<HTMLDivElement[]>([])
const pdfDoc = ref<any>(null)
const totalPages = ref(0)
const pages = ref<number[]>([])
let resizeObserver: ResizeObserver | null = null
// Références PDF.js chargées dynamiquement (client-only)
let getDocumentFn: any = null
let GlobalWorkerOptionsObj: any = null
// Pas d'AnnotationLayer si module indisponible; on s'appuie sur le rendu des apparences

function updateLastUpdated() {
    lastUpdated.value = new Date()
}

function timeSince(d?: Date | null) {
    if (!d) return '—'
    // Lire nowTS pour créer une dépendance réactive (maj automatique)
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
    if (!immediate) {
        debounceTimer = setTimeout(() => fetchPreview(true), 4000)
        return
    }
    if (abortController) abortController.abort()
    abortController = new AbortController()
    loading.value = true
    error.value = null
    try {
        // construire le payload léger (sans fichiers)
        const { dpc1, dpc2, dpc3, dpc4, dpc5, dpc6, dpc7, dpc8, dpc11, ...rest } = props.draft as any
        const resp = await apiRequest(
            () => $fetch<Blob>(`/api/administrative/cerfa/preview/`, {
                method: 'POST',
                body: rest,
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
    } finally {
        loading.value = false
    }
}

function manualRefresh() {
    emit('refresh-requested')
    fetchPreview(true)
}

watch(() => props.draft, () => {
    fetchPreview(false)
}, { deep: true })

onMounted(async () => {
    // Charger PDF.js côté client uniquement pour éviter SSR (document/window undefined)
    try {
        const core: any = await import('pdfjs-dist')
        getDocumentFn = core.getDocument
        GlobalWorkerOptionsObj = core.GlobalWorkerOptions
        const worker: any = await import('pdfjs-dist/build/pdf.worker.mjs?url')
        if (GlobalWorkerOptionsObj && worker?.default) {
            GlobalWorkerOptionsObj.workerSrc = worker.default
        }
        // On ignore l'annotation viewer si non disponible
    } catch { }
    // démarrer le ticker (toutes les secondes)
    nowInterval = setInterval(() => { nowTS.value = Date.now() }, 1000)
    await fetchPreview(true)
    // resize: re-render pages à la largeur
    await nextTick()
    if (viewerRef.value) {
        let ticking = false
        const rerender = () => {
            if (ticking) return; ticking = true
            requestAnimationFrame(async () => {
                if (pdfDoc.value) {
                    for (let i = 1; i <= totalPages.value; i++) await renderSinglePage(i)
                }
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
    if (pdfDoc.value) {
        try { pdfDoc.value.destroy?.() } catch { }
        try { pdfDoc.value.cleanup?.() } catch { }
        pdfDoc.value = null
    }
})

// PDF.js helpers
async function loadPdf(data: ArrayBuffer) {
    // nettoyer l'ancien doc
    if (pdfDoc.value) {
        try { await pdfDoc.value.destroy?.() } catch { }
        try { pdfDoc.value.cleanup?.() } catch { }
        pdfDoc.value = null
    }
    if (!getDocumentFn) throw new Error('PDF.js non chargé')
    const task = getDocumentFn({ data })
    const doc = await ((task as any).promise ?? (task as unknown as Promise<any>))
    pdfDoc.value = markRaw(doc)
    totalPages.value = pdfDoc.value.numPages
    pages.value = Array.from({ length: totalPages.value }, (_, i) => i + 1)
    await nextTick()
    for (let i = 1; i <= totalPages.value; i++) {
        await renderSinglePage(i)
    }
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
    const renderTask: any = page.render({
        canvasContext: ctx,
        viewport,
        intent: 'display',
    })
    await (renderTask?.promise ?? renderTask)

    // Rendu de la couche d'annotations (affiche les champs et leurs valeurs)
    if (layerDiv) {
        try {
            // Si les apparences sont présentes (NeedAppearances + AP), le canvas les reflète.
            // On garde le layer vide comme overlay pour garder la structure, sans erreur SSR.
            layerDiv.innerHTML = ''
            layerDiv.style.position = 'absolute'
            layerDiv.style.top = '0'
            layerDiv.style.left = '0'
            layerDiv.style.width = `${Math.floor(viewport.width)}px`
            layerDiv.style.height = `${Math.floor(viewport.height)}px`
        } catch (e) {
            // fallback silencieux si la couche échoue
        }
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
        <div v-if="error" class="absolute inset-0 flex items-center justify-center text-red-600">
            {{ error }}
        </div>
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

        <!-- Barre d’action en bas -->
        <div
            class="absolute bottom-2 left-5 right-8 z-20 flex items-center justify-between text-xs text-gray-600 pointer-events-none">
            <UButton class="pointer-events-auto" size="xs" color="neutral" icon="i-heroicons-arrow-path"
                :loading="loading" @click="manualRefresh">
                Actualiser
            </UButton>
            <div>
                Actualisé il y a {{ timeSince(lastUpdated) }}
            </div>
        </div>
    </div>
</template>
