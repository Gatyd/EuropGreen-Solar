<script setup lang="ts">

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
const pdfUrl = ref<string | null>(null)
const lastUpdated = ref<Date | null>(null)
let abortController: AbortController | null = null
let debounceTimer: any = null
// Ticker pour rafraîchir l'horodatage "Actualisé il y a ..."
const nowTS = ref<number>(Date.now())
let nowInterval: any = null

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
        debounceTimer = setTimeout(() => fetchPreview(true), 900)
        return
    }
    if (abortController) abortController.abort()
    abortController = new AbortController()
    loading.value = true
    error.value = null
    try {
        // construire le payload léger (sans fichiers)
        const { dpc1, dpc2, dpc3, dpc4, dpc5, dpc6, dpc7, dpc8, dpc11, ...rest } = props.draft as any
            const resp = await $fetch<Blob>(`/api/administrative/cerfa/preview/`, {
            method: 'POST',
            body: rest,
                credentials: 'include',
            // @ts-ignore runtime options
            responseType: 'blob',
            signal: abortController.signal,
        })
        // Nuxt $fetch renvoie déjà le Blob; créer un object URL
        if (pdfUrl.value) URL.revokeObjectURL(pdfUrl.value)
        const url = URL.createObjectURL(resp)
        pdfUrl.value = url
        updateLastUpdated()
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

onMounted(() => {
    // démarrer le ticker (toutes les secondes)
    nowInterval = setInterval(() => { nowTS.value = Date.now() }, 1000)
    fetchPreview(true)
})
onBeforeUnmount(() => {
    if (pdfUrl.value) URL.revokeObjectURL(pdfUrl.value)
    if (nowInterval) { clearInterval(nowInterval); nowInterval = null }
})
</script>

<template>
    <div class="relative w-full h-[88vh] border rounded overflow-hidden bg-zinc-50">
        <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-white/60 z-10">
            <div class="flex items-center gap-2 text-gray-600">
                <span class="i-heroicons-arrow-path-20-solid animate-spin"></span>
                <span>Génération de l’aperçu…</span>
            </div>
        </div>
        <div v-if="error" class="absolute inset-0 flex items-center justify-center text-red-600">
            {{ error }}
        </div>
        <object v-if="pdfUrl && !error" :data="pdfUrl" type="application/pdf" class="w-full h-full">
            <div class="p-6 text-gray-600">Votre navigateur ne peut pas afficher le PDF. <a :href="pdfUrl" target="_blank" class="underline">Ouvrir dans un nouvel onglet</a>.</div>
        </object>
        <div v-else class="h-full w-full flex items-center justify-center text-gray-500">
            Aucun aperçu disponible
        </div>

        <!-- Barre d’action en bas -->
        <div class="absolute bottom-2 left-2 right-2 flex items-center justify-between text-xs text-gray-600">
            <button type="button" @click="manualRefresh" class="px-2 py-1 rounded border bg-white hover:bg-gray-50 shadow">
                Actualiser
            </button>
            <div>
                Actualisé il y a {{ timeSince(lastUpdated) }}
            </div>
        </div>
    </div>
</template>
