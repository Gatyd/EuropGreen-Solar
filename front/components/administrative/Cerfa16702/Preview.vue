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

const props = defineProps<{ draft: Cerfa16702Draft & {
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
} }>()

const getFileName = (file: File | string | null): string => {
    if (!file) return ''
    if (typeof file === 'string') {
        return file.split('/').pop()?.split('?')[0] || 'Document'
    }
    return file.name
}

const yn = (v: boolean) => (v ? 'Oui' : 'Non')
const ynu = (v: boolean) => (v ? 'Oui' : 'Non')

console.log('[Preview.vue]:', props.draft)

</script>

<template>
    <div class="inline-block w-full xl:min-h-[1122.66px] xl:mx-auto bg-white text-xs px-6 py-4">
        <!-- En-tête -->
        <div class="flex justify-between items-center mb-6">
            <div>
                <Logo size="sm" />
            </div>
            <div class="text-right">
                <p class="text-2xl text-black font-normal mb-1">CERFA 16702</p>
                <p class="text-[11px] text-gray-500">Déclaration préalable en Mairie</p>
                <!-- <p class="text-[11px] text-gray-500">Généré le {{
                    props.draft.generated_at ? new Date(props.draft.generated_at).toLocaleDateString('fr-FR') : new Date().toLocaleDateString('fr-FR')
                }}</p> -->
            </div>
        </div>

        <!-- 1. Identité du déclarant -->
        <div class="mb-4">
            <div class="text-sm font-semibold text-zinc-700 mb-2">1. Identité du déclarant</div>
            <div class="overflow-hidden rounded-md border border-zinc-200">
                <table class="w-full text-sm border-collapse">
                    <tbody>
                        <tr class="odd:bg-zinc-50">
                            <td class="w-[45%] p-2 text-gray-600">Type de déclarant</td>
                            <td class="p-2">{{ props.draft.declarant_type === 'individual' ? 'Individu' : 'Entreprise' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Nom</td>
                            <td class="p-2">{{ props.draft.last_name || '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Prénom</td>
                            <td class="p-2">{{ props.draft.first_name || '—' }}</td>
                        </tr>
                        <tr v-if="props.draft.declarant_type === 'individual'" class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Date de naissance</td>
                            <td class="p-2">{{ props.draft.birth_date || '—' }}</td>
                        </tr>
                        <tr v-if="props.draft.declarant_type === 'individual'" class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Lieu de naissance</td>
                            <td class="p-2">{{ props.draft.birth_place || '—' }}</td>
                        </tr>
                        <tr v-if="props.draft.declarant_type === 'individual'" class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Département de naissance</td>
                            <td class="p-2">{{ props.draft.birth_department || '—' }}</td>
                        </tr>
                        <tr v-if="props.draft.declarant_type === 'individual'" class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Pays de naissance</td>
                            <td class="p-2">{{ props.draft.birth_country || '—' }}</td>
                        </tr>
                        <tr v-if="props.draft.declarant_type === 'company'" class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Dénomination</td>
                            <td class="p-2">{{ props.draft.company_denomination || '—' }}</td>
                        </tr>
                        <tr v-if="props.draft.declarant_type === 'company'" class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Raison sociale</td>
                            <td class="p-2">{{ props.draft.company_reason || '—' }}</td>
                        </tr>
                        <tr v-if="props.draft.declarant_type === 'company'" class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">N° SIRET</td>
                            <td class="p-2">{{ props.draft.company_siret || '—' }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 2. Coordonnées du déclarant -->
        <div class="mb-4">
            <div class="text-sm font-semibold text-zinc-700 mb-2">2. Coordonnées du déclarant</div>
            <div class="overflow-hidden rounded-md border border-zinc-200">
                <table class="w-full text-sm border-collapse">
                    <tbody>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Adresse (numéro)</td>
                            <td class="p-2">{{ props.draft.address_number || '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Adresse (voie)</td>
                            <td class="p-2">{{ props.draft.address_street || '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Adresse (Lieu-dit)</td>
                            <td class="p-2">{{ props.draft.address_lieu_dit || '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Adresse (Localité)</td>
                            <td class="p-2">{{ props.draft.address_locality || '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Adresse (Code postal)</td>
                            <td class="p-2">{{ props.draft.address_postal_code || '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Adresse (BP)</td>
                            <td class="p-2">{{ props.draft.address_bp || '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Adresse (CEDEX)</td>
                            <td class="p-2">{{ props.draft.address_cedex || '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Téléphone</td>
                            <td class="p-2">
                                <span v-if="props.draft.phone_country_code">({{ props.draft.phone_country_code }}) </span>
                                {{ props.draft.phone || '—' }}
                            </td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Adresse électronique</td>
                            <td class="p-2">{{ props.draft.email || '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Consentement email</td>
                            <td class="p-2">{{ yn(props.draft.email_consent) }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 3. Le terrain -->
        <div class="mb-4">
            <div class="text-sm font-semibold text-zinc-700 mb-2">3. Le terrain</div>
            <div class="overflow-hidden rounded-md border border-zinc-200">
                <table class="w-full text-sm border-collapse">
                    <tbody>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Adresse du terrain (voie)</td>
                            <td class="p-2">{{ props.draft.land_street || '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Adresse du terrain (numéro)</td>
                            <td class="p-2">{{ props.draft.land_number || '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Adresse du terrain (Lieu-dit)</td>
                            <td class="p-2">{{ props.draft.land_lieu_dit || '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Adresse du terrain (Localité)</td>
                            <td class="p-2">{{ props.draft.land_locality || '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Adresse du terrain (Code postal)</td>
                            <td class="p-2">{{ props.draft.land_postal_code || '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Préfixe cadastral</td>
                            <td class="p-2">{{ props.draft.cadastral_prefix || '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Section cadastral</td>
                            <td class="p-2">{{ props.draft.cadastral_section || '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Numéro cadastral</td>
                            <td class="p-2">{{ props.draft.cadastral_number || '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Surface (m²)</td>
                            <td class="p-2">{{ props.draft.cadastral_surface_m2 || '—' }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 4.1 Le projet -->
        <div class="mb-4">
            <div class="text-sm font-semibold text-zinc-700 mb-2">4.1 Le projet</div>
            <div class="overflow-hidden rounded-md border border-zinc-200">
                <table class="w-full text-sm border-collapse">
                    <tbody>
                        <tr class="odd:bg-zinc-50">
                            <td class="w-[45%] p-2 text-gray-600">Type de projet</td>
                            <td class="p-2">
                                <span v-if="props.draft.project_new_construction">Nouvelle construction</span>
                                <span v-if="props.draft.project_new_construction && props.draft.project_existing_works">, </span>
                                <span v-if="props.draft.project_existing_works">Travaux sur construction existante</span>
                                <span v-if="!props.draft.project_new_construction && !props.draft.project_existing_works">—</span>
                            </td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Description du projet</td>
                            <td class="p-2 whitespace-pre-line">{{ props.draft.project_description || '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Destination</td>
                            <td class="p-2">
                                <span v-if="props.draft.destination_primary_residence">Résidence principale</span>
                                <span v-if="props.draft.destination_primary_residence && props.draft.destination_secondary_residence">, </span>
                                <span v-if="props.draft.destination_secondary_residence">Résidence secondaire</span>
                                <span v-if="!props.draft.destination_primary_residence && !props.draft.destination_secondary_residence">—</span>
                            </td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Projet agrivoltaïque</td>
                            <td class="p-2">{{ ynu(props.draft.agrivoltaic_project) }}</td>
                        </tr>
                        <tr v-if="props.draft.electrical_power_text" class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Puissance électrique</td>
                            <td class="p-2">{{ props.draft.electrical_power_text }}</td>
                        </tr>
                        <tr v-if="props.draft.peak_power_text" class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Puissance crête</td>
                            <td class="p-2">{{ props.draft.peak_power_text }}</td>
                        </tr>
                        <tr v-if="props.draft.energy_destination" class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Destination de l'énergie</td>
                            <td class="p-2">{{ props.draft.energy_destination }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 5. Périmètres de protection -->
        <div class="mb-4">
            <div class="text-sm font-semibold text-zinc-700 mb-2">5. Périmètres de protection</div>
            <div class="overflow-hidden rounded-md border border-zinc-200">
                <table class="w-full text-sm border-collapse">
                    <tbody>
                        <tr class="odd:bg-zinc-50">
                            <td class="w-[45%] p-2 text-gray-600">Site patrimonial</td>
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

        <!-- 8. Engagement du déclarant -->
        <!-- <div class="mb-4">
            <div class="text-sm font-semibold text-zinc-700 mb-2">8. Engagement du déclarant</div>
            <div class="overflow-hidden rounded-md border border-zinc-200">
                <table class="w-full text-sm border-collapse">
                    <tbody>
                        <tr class="odd:bg-zinc-50">
                            <td class="w-[45%] p-2 text-gray-600">Ville</td>
                            <td class="p-2">{{ props.draft.engagement_city || '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Date</td>
                            <td class="p-2">{{ props.draft.engagement_date || '—' }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div> -->

        <!-- Pièces jointes DPC -->
        <div class="mb-4">
            <div class="text-sm font-semibold text-zinc-700 mb-2">Pièces jointes (DPC)</div>
            <div class="overflow-hidden rounded-md border border-zinc-200">
                <table class="w-full text-sm border-collapse">
                    <tbody>
                        <tr class="odd:bg-zinc-50">
                            <td class="w-[45%] p-2 text-gray-600">DPC1 - Plan de masse</td>
                            <td class="p-2">
                                <span v-if="props.draft.dpc1" class="text-gray-500">{{ getFileName(props.draft.dpc1) }}</span>
                                <span v-else class="text-gray-400">—</span>
                            </td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">DPC2 - Plan en coupe</td>
                            <td class="p-2">
                                <span v-if="props.draft.dpc2" class="text-gray-500">{{ getFileName(props.draft.dpc2) }}</span>
                                <span v-else class="text-gray-400">—</span>
                            </td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">DPC3 - Notice descriptive</td>
                            <td class="p-2">
                                <span v-if="props.draft.dpc3" class="text-gray-500">{{ getFileName(props.draft.dpc3) }}</span>
                                <span v-else class="text-gray-400">—</span>
                            </td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">DPC4 - Façades et toitures</td>
                            <td class="p-2">
                                <span v-if="props.draft.dpc4" class="text-gray-500">{{ getFileName(props.draft.dpc4) }}</span>
                                <span v-else class="text-gray-400">—</span>
                            </td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">DPC5 - Document graphique</td>
                            <td class="p-2">
                                <span v-if="props.draft.dpc5" class="text-gray-500">{{ getFileName(props.draft.dpc5) }}</span>
                                <span v-else class="text-gray-400">—</span>
                            </td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">DPC6 - Photo terrain</td>
                            <td class="p-2">
                                <span v-if="props.draft.dpc6" class="text-gray-500">{{ getFileName(props.draft.dpc6) }}</span>
                                <span v-else class="text-gray-400">—</span>
                            </td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">DPC7 - Photo terrain</td>
                            <td class="p-2">
                                <span v-if="props.draft.dpc7" class="text-gray-500">{{ getFileName(props.draft.dpc7) }}</span>
                                <span v-else class="text-gray-400">—</span>
                            </td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">DPC8 - Photo terrain</td>
                            <td class="p-2">
                                <span v-if="props.draft.dpc8" class="text-gray-500">{{ getFileName(props.draft.dpc8) }}</span>
                                <span v-else class="text-gray-400">—</span>
                            </td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">DPC11 - Notice matériaux</td>
                            <td class="p-2">
                                <span v-if="props.draft.dpc11" class="text-gray-500">{{ getFileName(props.draft.dpc11) }}</span>
                                <span v-else class="text-gray-400">—</span>
                            </td>
                        </tr>
                        <tr v-if="props.draft.dpc11_notice_materiaux" class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Notice matériaux (texte)</td>
                            <td class="p-2 whitespace-pre-line">{{ props.draft.dpc11_notice_materiaux }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Signature -->
        <div class="mt-8">
            <div class="mb-3 text-sm font-semibold text-zinc-700">Signature</div>
            <div class="flex justify-center">
                <div class="w-full max-w-md">
                    <div class="border rounded-md p-3 inline-flex w-full min-h-[120px] items-center justify-center bg-white">
                        <template v-if="props.draft.declarant_signature_image_url || props.draft.declarant_signature?.dataUrl">
                            <img :src="props.draft.declarant_signature_image_url || props.draft.declarant_signature?.dataUrl" alt="Signature déclarant"
                                class="h-20 object-contain" />
                        </template>
                        <template v-else>
                            <div class="text-gray-500 italic">Pas encore signée</div>
                        </template>
                    </div>
                    <div class="mt-2 text-gray-700">
                        À <span class="font-semibold">{{ props.draft.engagement_city || '—' }}</span>
                        <span v-if="props.draft.engagement_date"> • le {{ new Date(props.draft.engagement_date).toLocaleString('fr-FR', { year: 'numeric', month: 'numeric', day: 'numeric' }) }}</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Pièces jointes DPC -->
        <div class="mt-8">
            <div class="mb-3 text-sm font-semibold text-zinc-700">Pièces jointes (DPC)</div>
            
            <!-- DPC1 -->
            <div v-if="draft.dpc1_url" class="mb-6">
                <div class="page-break-before"></div>
                <div class="text-sm font-semibold text-zinc-700 mb-2">DPC1 - Plan de masse des constructions à édifier</div>
                <div class="rounded-md p-4 bg-white">
                    <div class="text-center">
                        <img :src="draft.dpc1_url" alt="Photo DPC1" 
                             class="max-w-full h-auto max-h-96 mx-auto border rounded" />
                    </div>
                </div>
            </div>

            <!-- DPC2 -->
            <div v-if="draft.dpc2_url" class="mb-6">
                <div class="page-break-before"></div>
                <div class="text-sm font-semibold text-zinc-700 mb-2">DPC2 - Plan en coupe du terrain et des constructions</div>
                <div class="rounded-md p-4 bg-white">
                    <div class="text-center">
                        <img :src="draft.dpc2_url" alt="Photo DPC2" 
                             class="max-w-full h-auto max-h-96 mx-auto border rounded" />
                    </div>
                </div>
            </div>

            <!-- DPC3 -->
            <div v-if="draft.dpc3_url" class="mb-6">
                <div class="page-break-before"></div>
                <div class="text-sm font-semibold text-zinc-700 mb-2">DPC3 - Notice descriptive</div>
                <div class="rounded-md p-4 bg-white">
                    <div class="text-center">
                        <img :src="draft.dpc3_url" alt="Photo DPC3" 
                             class="max-w-full h-auto max-h-96 mx-auto border rounded" />
                    </div>
                </div>
            </div>

            <!-- DPC4 -->
            <div v-if="draft.dpc4_url" class="mb-6">
                <div class="page-break-before"></div>
                <div class="text-sm font-semibold text-zinc-700 mb-2">DPC4 - Plan des façades et des toitures</div>
                <div class="rounded-md p-4 bg-white">
                    <div class="text-center">
                        <img :src="draft.dpc4_url" alt="Photo DPC4" 
                             class="max-w-full h-auto max-h-96 mx-auto border rounded" />
                    </div>
                </div>
            </div>

            <!-- DPC5 -->
            <div v-if="draft.dpc5_url" class="mb-6">
                <div class="page-break-before"></div>
                <div class="text-sm font-semibold text-zinc-700 mb-2">DPC5 - Document graphique du terrain</div>
                <div class="rounded-md p-4 bg-white">
                    <div class="text-center">
                        <img :src="draft.dpc5_url" alt="Photo DPC5" 
                             class="max-w-full h-auto max-h-96 mx-auto border rounded" />
                    </div>
                </div>
            </div>

            <!-- DPC6 -->
            <div v-if="draft.dpc6_url" class="mb-6">
                <div class="page-break-before"></div>
                <div class="text-sm font-semibold text-zinc-700 mb-2">DPC6 - Photographie du terrain nu et de son environnement</div>
                <div class="rounded-md p-4 bg-white">
                    <div class="text-center">
                        <img :src="draft.dpc6_url" alt="Photo DPC6" 
                             class="max-w-full h-auto max-h-96 mx-auto border rounded" />
                    </div>
                </div>
            </div>

            <!-- DPC7 -->
            <div v-if="draft.dpc7_url" class="mb-6">
                <div class="page-break-before"></div>
                <div class="text-sm font-semibold text-zinc-700 mb-2">DPC7 - Photographie du terrain nu et de son environnement</div>
                <div class="rounded-md p-4 bg-white">
                    <div class="text-center">
                        <img :src="draft.dpc7_url" alt="Photo DPC7" 
                             class="max-w-full h-auto max-h-96 mx-auto border rounded" />
                    </div>
                </div>
            </div>

            <!-- DPC8 -->
            <div v-if="draft.dpc8_url" class="mb-6">
                <div class="page-break-before"></div>
                <div class="text-sm font-semibold text-zinc-700 mb-2">DPC8 - Photographie du terrain nu et de son environnement</div>
                <div class="rounded-md p-4 bg-white">
                    <div class="text-center">
                        <img :src="draft.dpc8_url" alt="Photo DPC8" 
                             class="max-w-full h-auto max-h-96 mx-auto border rounded" />
                    </div>
                </div>
            </div>

            <!-- DPC11 -->
            <div v-if="draft.dpc11_url" class="mb-6">
                <div class="page-break-before"></div>
                <div class="text-sm font-semibold text-zinc-700 mb-2">DPC11 - Notice descriptive des matériaux</div>
                <div class="rounded-md p-4 bg-white">
                    <div class="text-center">
                        <img :src="draft.dpc11_url" alt="Photo DPC11" 
                             class="max-w-full h-auto max-h-96 mx-auto border rounded" />
                    </div>
                </div>
            </div>

            <div v-else-if="!draft.dpc1_url">
                Les pièces jointes DPC seront affichées après la soumission.
            </div>
        </div>
    </div>
</template>

<style scoped>
.page-break-before {
    page-break-before: always;
    break-before: page;
}

@media print {
    .page-break-before {
        page-break-before: always;
        break-before: page;
    }
}
</style>