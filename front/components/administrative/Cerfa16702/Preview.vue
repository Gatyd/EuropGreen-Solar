<script setup lang="ts">
import Logo from '~/components/Logo.vue'

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
    mode?: 'print' | 'edit'
}>()

const currentMode = computed(() => props.mode || 'print')
const isPrint = computed(() => currentMode.value === 'print')
const isEdit = computed(() => currentMode.value === 'edit')

const getFileName = (file: File | string | null | undefined): string => {
    if (!file) return ''
    if (typeof file === 'string') {
        return file.split('/').pop()?.split('?')[0] || 'Document'
    }
    return file.name
}

const yn = (v: boolean) => (v ? 'Oui' : 'Non')
const ynu = (v: boolean) => (v ? 'Oui' : 'Non')

console.log('[Preview.vue]:', props.draft)

// Liste ordonnée des pièces jointes (ordre de pages 4..12)
const dpcLabels = [
    { key: 'dpc1', name: 'DPC1 - Plan de masse' },
    { key: 'dpc2', name: 'DPC2 - Plan en coupe' },
    { key: 'dpc3', name: 'DPC3 - Notice descriptive' },
    { key: 'dpc4', name: 'DPC4 - Façades et toitures' },
    { key: 'dpc5', name: 'DPC5 - Document graphique' },
    { key: 'dpc6', name: 'DPC6 - Photo terrain' },
    { key: 'dpc7', name: 'DPC7 - Photo terrain' },
    { key: 'dpc8', name: 'DPC8 - Photo terrain' },
    { key: 'dpc11', name: 'DPC11 - Notice descriptive des matériaux' },
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

// idx 0 -> page 4, idx 1 -> page 5, ..., idx 8 -> page 12
const attachmentPageNumber = (idx: number) => props.draft.dpc11_notice_materiaux ? 3 : 2 + idx

</script>

<template>
    <div :class="isPrint ? 'cerfa-print-root' : 'p-6'">
        <!-- Page 1 -->
        <section :class="isPrint ? 'cerfa-page' : ''">
            <header class="flex justify-between items-center mb-6">
                <Logo size="sm" />
                <div class="text-right">
                    <p class="text-2xl text-black font-normal mb-1">CERFA 16702</p>
                    <p class="text-[11px] text-gray-500">Déclaration préalable en Mairie</p>
                </div>
            </header>

            <div class="mb-4">
                <div class="text-sm font-semibold text-zinc-700 mb-2">1. Identité du déclarant</div>
                <div class="overflow-hidden rounded-md border border-zinc-200">
                    <table class="w-full text-sm border-collapse">
                        <tbody>
                            <tr class="odd:bg-zinc-50">
                                <td class="w-[45%] p-2 text-gray-600">Type de déclarant</td>
                                <td class="p-2">{{ props.draft.declarant_type === 'individual' ? 'Individu' :
                                    'Entreprise' }}</td>
                            </tr>
                            <tr class="odd:bg-zinc-50">
                                <td class="p-2 text-gray-600">Nom</td>
                                <td class="p-2">{{ props.draft.last_name || '—' }}</td>
                            </tr>
                            <tr class="odd:bg-zinc-50">
                                <td class="p-2 text-gray-600">Prénom</td>
                                <td class="p-2">{{ props.draft.first_name || '—' }}</td>
                            </tr>
                            <template v-if="props.draft.declarant_type === 'individual'">
                                <tr class="odd:bg-zinc-50">
                                    <td class="p-2 text-gray-600">Date de naissance</td>
                                    <td class="p-2">{{ props.draft.birth_date || '—' }}</td>
                                </tr>
                                <tr class="odd:bg-zinc-50">
                                    <td class="p-2 text-gray-600">Commune de naissance</td>
                                    <td class="p-2">{{ props.draft.birth_place || '—' }}</td>
                                </tr>
                                <tr class="odd:bg-zinc-50">
                                    <td class="p-2 text-gray-600">Département de naissance</td>
                                    <td class="p-2">{{ props.draft.birth_department || '—' }}</td>
                                </tr>
                                <tr class="odd:bg-zinc-50">
                                    <td class="p-2 text-gray-600">Pays de naissance</td>
                                    <td class="p-2">{{ props.draft.birth_country || '—' }}</td>
                                </tr>
                            </template>
                            <template v-if="props.draft.declarant_type === 'company'">
                                <tr class="odd:bg-zinc-50">
                                    <td class="p-2 text-gray-600">Dénomination</td>
                                    <td class="p-2">{{ props.draft.company_denomination || '—' }}</td>
                                </tr>
                                <tr class="odd:bg-zinc-50">
                                    <td class="p-2 text-gray-600">Raison sociale</td>
                                    <td class="p-2">{{ props.draft.company_reason || '—' }}</td>
                                </tr>
                                <tr class="odd:bg-zinc-50">
                                    <td class="p-2 text-gray-600">N° SIRET</td>
                                    <td class="p-2">{{ props.draft.company_siret || '—' }}</td>
                                </tr>
                                <tr class="odd:bg-zinc-50">
                                    <td class="p-2 text-gray-600">Type de société</td>
                                    <td class="p-2">{{ props.draft.company_type || '—' }}</td>
                                </tr>
                            </template>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="mb-4">
                <div class="text-sm font-semibold text-zinc-700 mb-2">2. Coordonnées du déclarant 
                    ({{ `${draft.email_consent ? 'Consentement' : 'Non consentement'} à la communication par courrier électronique` }})</div>
                <div class="overflow-hidden rounded-md border border-zinc-200 mb-1">
                    <table class="w-full text-sm border-collapse">
                        <tbody>
                            <tr class="odd:bg-zinc-50">
                                <td class="p-2 text-gray-600">Adresse (numéro)</td>
                                <td class="p-2 text-gray-600">Adresse (voie)</td>
                            </tr>
                            <tr class="odd:bg-zinc-50">
                                <td class="p-2">{{ props.draft.address_number || '—' }}</td>
                                <td class="p-2">{{ props.draft.address_street || '—' }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div class="overflow-hidden rounded-md border border-zinc-200 mb-1">
                    <table class="w-full text-sm border-collapse mb-1">
                        <tbody>
                            <tr class="odd:bg-zinc-50">
                                <td class="p-2 text-gray-600">Lieu-dit</td>
                                <td class="p-2 text-gray-600">Localité</td>
                            </tr>
                            <tr class="odd:bg-zinc-50">
                                <td class="p-2">{{ props.draft.address_lieu_dit || '—' }}</td>
                                <td class="p-2">{{ props.draft.address_locality || '—' }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div class="overflow-hidden rounded-md border border-zinc-200 mb-1">
                    <table class="w-full text-sm border-collapse mb-1">
                        <tbody>
                            <tr class="odd:bg-zinc-50">
                                <td class="p-2 text-gray-600">Code Postal</td>
                                <td class="p-2 text-gray-600">BP</td>
                                <td class="p-2 text-gray-600">Cedex</td>
                            </tr>
                            <tr class="odd:bg-zinc-50">
                                <td class="p-2">{{ props.draft.address_postal_code || '—' }}</td>
                                <td class="p-2">{{ props.draft.address_bp || '—' }}</td>
                                <td class="p-2">{{ props.draft.address_cedex || '—' }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div class="overflow-hidden rounded-md border border-zinc-200 mb-1">
                    <table class="w-full text-sm border-collapse">
                        <tbody>
                            <tr class="odd:bg-zinc-50">
                                <td class="p-2 text-gray-600">Téléphone</td>
                                <td class="p-2 text-gray-600">Adresse électronique</td>
                            </tr>
                            <tr class="odd:bg-zinc-50">
                                <td class="p-2">{{ draft.phone_country_code ? `(+${draft.phone_country_code}) ` : ''}}{{ draft.phone || '—' }}</td>
                                <td class="p-2">{{ props.draft.email || '—' }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="mb-4">
                <div class="text-sm font-semibold text-zinc-700 mb-2">3. Le terrain</div>
                <div class="overflow-hidden rounded-md border border-zinc-200 mb-1">
                    <table class="w-full text-sm border-collapse">
                        <tbody>
                            <tr class="odd:bg-zinc-50">
                                <td class="p-2 text-gray-600">Adresse du terrain (numéro)</td>
                                <td class="p-2 text-gray-600">Adresse du terrain (voie)</td>
                                <td class="p-2 text-gray-600">Adresse du terrain (Code postal)</td>
                            </tr>
                            <tr class="odd:bg-zinc-50">
                                <td class="p-2">{{ props.draft.land_street || '—' }}</td>
                                <td class="p-2">{{ props.draft.land_number || '—' }}</td>
                                <td class="p-2">{{ props.draft.land_postal_code || '—' }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div class="overflow-hidden rounded-md border border-zinc-200 mb-1">
                    <table class="w-full text-sm border-collapse">
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Adresse du terrain (Lieu-dit)</td>
                            <td class="p-2 text-gray-600">Adresse du terrain (Localité)</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2">{{ props.draft.land_lieu_dit || '—' }}</td>
                            <td class="p-2">{{ props.draft.land_locality || '—' }}</td>
                        </tr>
                    </table>
                </div>
                <div class="overflow-hidden rounded-md border border-zinc-200">
                    <table class="w-full text-sm border-collapse">
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Préfixe cadastral</td>
                            <td class="p-2 text-gray-600">Section cadastrale</td>
                            <td class="p-2 text-gray-600">Numéro cadastral</td>
                            <td class="p-2 text-gray-600">Surface (m²)</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2">{{ props.draft.cadastral_prefix || '—' }}</td>
                            <td class="p-2">{{ props.draft.cadastral_section || '—' }}</td>
                            <td class="p-2">{{ props.draft.cadastral_number || '—' }}</td>
                            <td class="p-2">{{ props.draft.cadastral_surface_m2 || '—' }}</td>
                        </tr>
                    </table>
                </div>
            </div>
        </section>

        <!-- Page 2 -->
        <section :class="isPrint ? 'cerfa-page' : ''">
            <div class="mt-8"></div>

            <div class="mb-4">
                <div class="text-sm font-semibold text-zinc-700 mb-2">4.1 Le projet</div>
                <div class="overflow-hidden rounded-md border border-zinc-200">
                    <table class="w-full text-sm border-collapse">
                        <tbody>
                            <tr class="odd:bg-zinc-50">
                                <td class="p-2 text-gray-600">Nouvelle construction</td>
                                <td class="p-2 text-gray-600">Construction existante</td>
                                <td class="p-2 text-gray-600">Résidence principale</td>
                                <td class="p-2 text-gray-600">Résidence secondaire</td>
                                <td class="p-2 text-gray-600">Projet agrivoltaïque</td>
                            </tr>
                            <tr class="odd:bg-zinc-50">
                                <td class="p-2">{{ yn(props.draft.project_new_construction) }}</td>
                                <td class="p-2">{{ yn(props.draft.project_existing_works) }}</td>
                                <td class="p-2">{{ yn(props.draft.destination_primary_residence) }}</td>
                                <td class="p-2">{{ yn(props.draft.destination_secondary_residence) }}</td>
                                <td class="p-2">{{ yn(props.draft.agrivoltaic_project) }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div v-if="draft.electrical_power_text || draft.peak_power_text || draft.energy_destination"
                class="mb-4 overflow-hidden rounded-md border border-zinc-200">
                <table class="w-full text-sm border-collapse">
                    <tbody>
                        <tr v-if="draft.electrical_power_text" class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Puissance électrique</td>
                            <td class="p-2">{{ draft.electrical_power_text }}</td>
                        </tr>
                        <tr v-if="draft.peak_power_text" class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Puissance crête</td>
                            <td class="p-2">{{ draft.peak_power_text }}</td>
                        </tr>
                        <tr v-if="draft.energy_destination" class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Destination de l'énergie</td>
                            <td class="p-2">{{ draft.energy_destination }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div v-if="draft.project_description" class="mb-6">
                <div class="text-sm font-semibold text-zinc-700 mb-2">Description du projet</div>
                <div class="overflow-hidden rounded-md border border-zinc-200 p-3">
                    <div class="whitespace-pre-line text-sm text-gray-800">{{ props.draft.project_description }}
                    </div>
                </div>
            </div>

            <div class="mb-4">
                <div class="text-sm font-semibold text-zinc-700 mb-2">5. Périmètres de protection</div>
                <div class="overflow-hidden rounded-md border border-zinc-200">
                    <table class="w-full text-sm border-collapse">
                        <tbody>
                            <tr class="odd:bg-zinc-50">
                                <td class="p-2 text-gray-600">Site patrimonial</td>
                                <td class="p-2">{{ yn(props.draft.protection_site_patrimonial) }}</td>
                            </tr>
                            <tr class="odd:bg-zinc-50">
                                <td class="p-2 text-gray-600">Site classé/instance de classement</td>
                                <td class="p-2">{{ yn(props.draft.protection_site_classe_or_instance) }}</td>
                            </tr>
                            <tr class="odd:bg-zinc-50">
                                <td class="p-2 text-gray-600">Abords d'un monument historique</td>
                                <td class="p-2">{{ yn(props.draft.protection_monument_abords) }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div class="mb-4">
                <div class="text-sm font-semibold text-zinc-700 mb-2">Pièces jointes (DPC)</div>
                <div class="overflow-hidden rounded-md border border-zinc-200">
                    <table class="w-full text-sm border-collapse">
                        <tbody>
                            <tr class="odd:bg-zinc-50" v-for="(label, idx) in dpcLabels" :key="label.key">
                                <td class="w-[65%] p-2 text-gray-600">{{ label.name }}</td>
                                <td class="p-2">
                                    <template v-if="getAttachmentUrl(label.key)">
                                        {{ getFileName(getAttachmentUrl(label.key)) }}
                                    </template>
                                    <template v-else>
                                        —
                                    </template>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div v-if="!draft.dpc11_notice_materiaux" class="mt-8">
                <div class="mb-3 text-sm font-semibold text-zinc-700">Signature</div>
                <div class="flex justify-center">
                    <div class="w-full max-w-md">
                        <div
                            class="border rounded-md p-3 inline-flex w-full min-h-[120px] items-center justify-center bg-white">
                            <template
                                v-if="props.draft.declarant_signature_image_url || props.draft.declarant_signature?.dataUrl">
                                <img :src="props.draft.declarant_signature_image_url || props.draft.declarant_signature?.dataUrl"
                                    alt="Signature déclarant" class="max-w-full h-auto" />
                            </template>
                            <template v-else>
                                <div class="text-gray-500 italic">Pas encore signée</div>
                            </template>
                        </div>
                        <div class="mt-2 text-gray-700">
                            À <span class="font-semibold">{{ props.draft.engagement_city || '—' }}</span>
                            <span v-if="props.draft.engagement_date"> • le {{ new
                                Date(props.draft.engagement_date).toLocaleString('fr-FR', {
                                    year: 'numeric', month:
                                        'numeric', day:
                                        'numeric'
                                }) }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section v-if="draft.dpc11_notice_materiaux" :class="isPrint ? 'cerfa-page' : ''">
            <div class="mt-8"></div>
            <!-- Notice matériaux (pleine largeur) -->
            <div v-if="props.draft.dpc11_notice_materiaux" class="mb-6">
                <div class="text-sm font-semibold text-zinc-700 mb-2">Notice matériaux</div>
                <div class="overflow-hidden rounded-md border border-zinc-200 p-3">
                    <div class="whitespace-pre-line text-sm text-gray-800">{{ props.draft.dpc11_notice_materiaux }}
                    </div>
                </div>
            </div>

            <div class="mt-8">
                <div class="mb-3 text-sm font-semibold text-zinc-700">Signature</div>
                <div class="flex justify-center">
                    <div class="w-full max-w-md">
                        <div
                            class="border rounded-md p-3 inline-flex w-full min-h-[120px] items-center justify-center bg-white">
                            <template
                                v-if="props.draft.declarant_signature_image_url || props.draft.declarant_signature?.dataUrl">
                                <img :src="props.draft.declarant_signature_image_url || props.draft.declarant_signature?.dataUrl"
                                    alt="Signature déclarant" class="max-w-full h-auto" />
                            </template>
                            <template v-else>
                                <div class="text-gray-500 italic">Pas encore signée</div>
                            </template>
                        </div>
                        <div class="mt-2 text-gray-700">
                            À <span class="font-semibold">{{ props.draft.engagement_city || '—' }}</span>
                            <span v-if="props.draft.engagement_date"> • le {{ new
                                Date(props.draft.engagement_date).toLocaleString('fr-FR', {
                                    year: 'numeric', month:
                                        'numeric', day:
                                        'numeric'
                                }) }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Pages 4..12: une pièce jointe par page (impression seulement) -->
        <section v-if="isPrint" v-for="(label, idx) in dpcLabels" :key="label.key" :class="isPrint ? 'cerfa-page' : ''">
            <div class="text-sm font-semibold text-zinc-700 mb-2">{{ label.name }}</div>
            <div class="rounded-md p-4 bg-white h-full flex items-center justify-center">
                <template v-if="getAttachmentUrl(label.key)">
                    <img :src="getAttachmentUrl(label.key)" :alt="label.name"
                        class="max-w-full h-auto max-h-[95vh] mx-auto" />
                </template>
                <template v-else>
                    <div class="text-gray-500">Aucun document fourni — Page {{ attachmentPageNumber(idx) }}</div>
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