<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch, nextTick, markRaw } from 'vue'

const props = defineProps<{ draft: any; mode?: 'print' | 'edit' }>()

const loading = ref(false)
const error = ref<string | null>(null)
const viewerRef = ref<HTMLDivElement | null>(null)
const pageCanvases = ref<HTMLCanvasElement[]>([])
const pageLayers = ref<HTMLDivElement[]>([])
const pdfDoc = ref<any>(null)
let abortController: AbortController | null = null
let debounceTimer: any = null

let getDocumentFn: any = null
let GlobalWorkerOptionsObj: any = null

async function fetchPreview(immediate = false) {
	if (debounceTimer && !immediate) clearTimeout(debounceTimer)
	if (!immediate) {
		debounceTimer = setTimeout(() => fetchPreview(true), 600)
		return
	}
	if (abortController) abortController.abort()
	abortController = new AbortController()
	loading.value = true
	error.value = null
	try {
		const body = { ...props.draft }
		const resp = await $fetch<Blob>(`/api/administrative/consuel/preview/`, {
			method: 'POST',
			body,
			credentials: 'include',
			// @ts-ignore
			responseType: 'blob',
			signal: abortController.signal,
		})
		const arrayBuffer = await resp.arrayBuffer()
		await loadPdf(arrayBuffer)
	} catch (e: any) {
		error.value = e?.data?.message || e?.message || 'Erreur de chargement'
	} finally {
		loading.value = false
	}
}

watch(() => props.draft, () => fetchPreview(false), { deep: true })

onMounted(async () => {
	try {
		const core: any = await import('pdfjs-dist')
		getDocumentFn = core.getDocument
		GlobalWorkerOptionsObj = core.GlobalWorkerOptions
		const worker: any = await import('pdfjs-dist/build/pdf.worker.mjs?url')
		if (GlobalWorkerOptionsObj && worker?.default) {
			GlobalWorkerOptionsObj.workerSrc = worker.default
		}
	} catch {}
	await fetchPreview(true)
})

onBeforeUnmount(() => {
	if (abortController) try { abortController.abort() } catch {}
	if (pdfDoc.value) {
		try { pdfDoc.value.destroy?.() } catch {}
		try { pdfDoc.value.cleanup?.() } catch {}
		pdfDoc.value = null
	}
})

async function loadPdf(data: ArrayBuffer) {
	if (pdfDoc.value) {
		try { await pdfDoc.value.destroy?.() } catch {}
		try { pdfDoc.value.cleanup?.() } catch {}
		pdfDoc.value = null
	}
	if (!getDocumentFn) throw new Error('PDF.js non chargé')
	const task = getDocumentFn({ data })
	const doc = await ((task as any).promise ?? (task as unknown as Promise<any>))
	pdfDoc.value = markRaw(doc)
	await renderAllPages()
}

async function renderAllPages() {
	if (!pdfDoc.value) return
	const viewer = viewerRef.value
	if (!viewer) return
	viewer.innerHTML = ''
	const count = pdfDoc.value.numPages
	for (let i = 1; i <= count; i++) {
		const wrap = document.createElement('div')
		wrap.className = 'relative mb-4'
		const canvas = document.createElement('canvas')
		const layer = document.createElement('div')
		pageCanvases.value.push(canvas)
		pageLayers.value.push(layer)
		wrap.appendChild(canvas)
		wrap.appendChild(layer)
		viewer.appendChild(wrap)
		await renderSinglePage(i, canvas, layer)
	}
}

async function renderSinglePage(pageNumber: number, canvas: HTMLCanvasElement, layerDiv: HTMLDivElement) {
	if (!pdfDoc.value) return
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
		layerDiv.innerHTML = ''
		layerDiv.style.position = 'absolute'
		layerDiv.style.top = '0'
		layerDiv.style.left = '0'
		layerDiv.style.height = `${Math.floor(viewport.height)}px`
	}
}
</script>

<template>
	<div class="relative h-full flex flex-col">
		<div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-white/60 z-10" />
		<div v-if="error" class="absolute inset-0 flex items-center justify-center text-red-600">{{ error }}</div>
		<div ref="viewerRef" class="w-full flex-1 overflow-auto px-4"></div>
	</div>
</template>
