<script setup lang="ts">
import type { InstallationForm } from '~/types/installations'

type Cerfa16702Draft = {
    dpc1: File | null
    dpc2: File | null
    dpc3: File | null
    dpc4: File | null
    dpc5: File | null
    dpc6: File | null
    dpc7: File | null
    dpc8: File | null
    dpc11: File | null
    dpc11_notice_materiaux: string
}

const props = defineProps<{
    draft: Cerfa16702Draft & {
        generated_at?: string
        declarant_signature_image_url?: string | null
        declarant_signature_signed_at?: string | null
        dpc1_url?: string | null
        dpc2_url?: string | null
        dpc3_url?: string | null
        dpc4_url?: string | null
        dpc5_url?: string | null
        dpc6_url?: string | null
        dpc7_url?: string | null
        dpc8_url?: string | null
        dpc11_url?: string | null
    }
    cerfa16702?: InstallationForm['cerfa16702'] | null
    mode?: 'print' | 'edit'
}>()

const currentMode = computed(() => props.mode || 'print')
const isPrint = computed(() => currentMode.value === 'print')
const isEdit = computed(() => currentMode.value === 'edit')

const yn = (v: boolean) => (v ? 'Oui' : 'Non')
const ynu = (v: boolean) => (v ? 'Oui' : 'Non')

// Liste ordonnée des pièces jointes avec titres exacts
const dpcLabels = [
    { key: 'dpc1', name: "DPC1 - PLAN DE SITUATION" },
    { key: 'dpc2', name: "DPC2 - PLAN DE MASSE" },
    { key: 'dpc3', name: "DPC3 - PLAN EN COUPE" },
    { key: 'dpc4', name: "DPC4 - PLAN DES FACADES ET DES TOITURES" },
    { key: 'dpc5', name: "DPC5 - REPRESENTATION DE L'ASPECT EXTERIEUR" },
    { key: 'dpc6', name: "DPC6 - DOCUMENT GRAPHIQUE" },
    { key: 'dpc7', name: "DPC7 - PHOTOGRAPHIE DE SITUATION DU TERRAIN DANS L'ENVIRONNEMENT PROCHE" },
    { key: 'dpc8', name: "DPC8 - PHOTOGRAPHIE DE SITUATION DU TERRAIN DANS LE PAYSAGE LOINTAIN" },
    { key: 'dpc11', name: "DPC11 - NOTICE DES MATERIAUX UTILISES" },
]

const getAttachmentUrl = (key: string): string | undefined => {
    switch (key) {
        case 'dpc1': return props.draft.dpc1_url || undefined
        case 'dpc2': return props.draft.dpc2_url || undefined
        case 'dpc3': return props.draft.dpc3_url || undefined
        case 'dpc4': return props.draft.dpc4_url || undefined
        case 'dpc5': return props.draft.dpc5_url || undefined
        case 'dpc6': return props.draft.dpc6_url || undefined
        case 'dpc7': return props.draft.dpc7_url || undefined
        case 'dpc8': return props.draft.dpc8_url || undefined
        case 'dpc11': return props.draft.dpc11_url || undefined
        default: return undefined
    }
}

// Accès File par clé
const getAttachmentFile = (key: string): File | null => {
    const d: any = props.draft as any
    return (d && key in d) ? (d[key] as File | null) : null
}

// Cache d'Object URLs pour les fichiers locaux
const objectUrlCache = new Map<string, string>()
onBeforeUnmount(() => {
    for (const url of objectUrlCache.values()) {
        try { URL.revokeObjectURL(url) } catch { }
    }
    objectUrlCache.clear()
})

// Source d'image: priorité URL, sinon fichier sélectionné (en mode edit ou si pas d'URL)
const getAttachmentSrc = (key: string): string | undefined => {
    const url = getAttachmentUrl(key)
    if (url) return url
    const file = getAttachmentFile(key)
    if (!file) return undefined
    if (!isEdit.value && url) return undefined
    if (objectUrlCache.has(key)) return objectUrlCache.get(key)
    const obj = URL.createObjectURL(file)
    objectUrlCache.set(key, obj)
    return obj
}

// Infos en-tête
const fullName = computed(() => {
    const f = props.cerfa16702 as any
    const first = f?.first_name || ''
    const last = f?.last_name || ''
    return `${first} ${last}`.trim()
})

const projectAddress = computed(() => {
    const f = props.cerfa16702 as any
    if (!f) return ''
    const parts = [
        [f.land_number, f.land_street].filter(Boolean).join(' '),
        f.land_lieu_dit,
        [f.land_postal_code, f.land_locality].filter(Boolean).join(' '),
    ].filter(Boolean)
    return parts.join(' \u2013 ')
})
</script>

<template>
    <div :class="isPrint ? 'cerfa-print-root' : 'p-6'">
        <section v-for="(label, idx) in dpcLabels" :key="label.key" class="cerfa-page">
            <!-- En-tête Demandeur / Adresse du projet -->
            <div class="text-[14px] flex items-start justify-between mb-4">
                <div class="min-w-0">
                    <div class="text-zinc-600 font-semibold leading-tight">Demandeur</div>
                    <div class="truncate">{{ fullName }}</div>
                </div>
                <div class="text-right min-w-0 ml-6">
                    <div class="text-zinc-600 font-semibold leading-tight">Adresse du projet</div>
                    <div class="truncate" :title="projectAddress">{{ projectAddress }}</div>
                </div>
            </div>

            <!-- Titre de la pièce jointe -->
            <div class="text-lg font-bold text-zinc-800 tracking-tight uppercase mb-3">
                {{ label.name }}
            </div>
            <template v-if="label.key === 'dpc11' && props.draft.dpc11_notice_materiaux">
                <div class="prose max-w-none text-gray-500 whitespace-pre-line px-6">
                    <p>{{ props.draft.dpc11_notice_materiaux }}</p>
                </div>
            </template>

            <!-- Contenu image pleine page -->
            <div
                class="rounded-md bg-white flex items-center justify-center min-h-[220mm] max-h-[240mm] overflow-hidden">
                <template v-if="getAttachmentSrc(label.key)">
                    <img :src="getAttachmentSrc(label.key)" :alt="label.name"
                        class="max-w-full max-h-[235mm] h-auto w-auto" />
                </template>
                <template v-else>
                    <div class="text-gray-500 text-sm">Aucun document fourni</div>
                </template>
            </div>
        </section>
    </div>
</template>

<style scoped>
.cerfa-print-root {
    width: 100%;
    min-height: 297mm;
    /* A4 height */
    background: white;
    color: #222;
    font-size: 15px;
    padding: 24px 32px 64px 32px;
    box-sizing: border-box;
    position: relative;
}

.cerfa-page {
    width: 100%;
    min-height: 297mm;
    box-sizing: border-box;
    /* page-break-after: always; */
    /* break-after: page; */
    padding: 12mm 14mm;
    /* internal page margins */
    background: white;
    display: block;
}

.cerfa-page img {
    max-width: 100%;
    height: auto;
    display: block;
}

.pdf-footer {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    height: 32px;
    text-align: center;
    font-size: 13px;
    color: #888;
    width: 100vw;
    background: white;
    z-index: 100;
}

.page-break-before {
    page-break-before: always;
    break-before: page;
}

.page-break-after {
    page-break-after: always;
    break-after: page;
}

/* Force A4 size and remove browser default margins when printing (helps Playwright) */
@page {
    size: A4;
    margin: 0;
}

@media print {
    .cerfa-print-root {
        font-size: 14px;
        padding: 0;
        /* use @page margins instead */
    }

    .cerfa-page {
        padding: 12mm 14mm;
    }

    .pdf-footer {
        display: none;
        /* Playwright can add its own footer */
    }

    .page-break-before {
        page-break-before: always;
        break-before: page;
    }

    .page-break-after {
        page-break-after: always;
        break-after: page;
    }
}
</style>