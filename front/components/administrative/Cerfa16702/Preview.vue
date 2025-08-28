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

const props = defineProps<{ draft: Cerfa16702Draft & {
    generated_at?: string
    declarant_signature_image_url?: string | null
    declarant_signature_signed_at?: string | null
} }>()

const yn = (v: boolean) => (v ? 'Oui' : 'Non')
const ynu = (v: boolean) => (v ? 'Oui' : 'Non')
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
                <p class="text-[11px] text-gray-500">Généré le {{
                    props.draft.generated_at ? new Date(props.draft.generated_at).toLocaleDateString('fr-FR') : new Date().toLocaleDateString('fr-FR')
                }}</p>
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
                            <td class="w-[45%] p-2 text-gray-600">Adresse</td>
                            <td class="p-2">
                                {{ props.draft.address_street || '—' }}
                                <span v-if="props.draft.address_number">, {{ props.draft.address_number }}</span>
                                <span v-if="props.draft.address_lieu_dit">, {{ props.draft.address_lieu_dit }}</span>
                                <span v-if="props.draft.address_locality">, {{ props.draft.address_locality }}</span>
                                <span v-if="props.draft.address_postal_code">, {{ props.draft.address_postal_code }}</span>
                                <span v-if="props.draft.address_bp">, BP {{ props.draft.address_bp }}</span>
                                <span v-if="props.draft.address_cedex">, CEDEX {{ props.draft.address_cedex }}</span>
                            </td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Téléphone</td>
                            <td class="p-2">
                                <span v-if="props.draft.phone_country_code">{{ props.draft.phone_country_code }} </span>
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
                            <td class="w-[45%] p-2 text-gray-600">Adresse du terrain</td>
                            <td class="p-2">
                                {{ props.draft.land_street || '—' }}
                                <span v-if="props.draft.land_number">, {{ props.draft.land_number }}</span>
                                <span v-if="props.draft.land_lieu_dit">, {{ props.draft.land_lieu_dit }}</span>
                                <span v-if="props.draft.land_locality">, {{ props.draft.land_locality }}</span>
                                <span v-if="props.draft.land_postal_code">, {{ props.draft.land_postal_code }}</span>
                            </td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Références cadastrales</td>
                            <td class="p-2">
                                <span v-if="props.draft.cadastral_prefix">{{ props.draft.cadastral_prefix }}</span>
                                <span v-if="props.draft.cadastral_section">, Section {{ props.draft.cadastral_section }}</span>
                                <span v-if="props.draft.cadastral_number">, N° {{ props.draft.cadastral_number }}</span>
                                <span v-if="props.draft.cadastral_surface_m2">, {{ props.draft.cadastral_surface_m2 }} m²</span>
                            </td>
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
        <div class="mb-4">
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
        </div>

        <!-- Pièces jointes DPC -->
        <div class="mb-4">
            <div class="text-sm font-semibold text-zinc-700 mb-2">Pièces jointes (DPC)</div>
            <div class="overflow-hidden rounded-md border border-zinc-200">
                <table class="w-full text-sm border-collapse">
                    <tbody>
                        <tr class="odd:bg-zinc-50">
                            <td class="w-[45%] p-2 text-gray-600">DPC1 - Plan de masse</td>
                            <td class="p-2">{{ props.draft.dpc1 ? 'Document importé' : '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">DPC2 - Plan en coupe</td>
                            <td class="p-2">{{ props.draft.dpc2 ? 'Document importé' : '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">DPC3 - Notice descriptive</td>
                            <td class="p-2">{{ props.draft.dpc3 ? 'Document importé' : '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">DPC4 - Façades et toitures</td>
                            <td class="p-2">{{ props.draft.dpc4 ? 'Document importé' : '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">DPC5 - Document graphique</td>
                            <td class="p-2">{{ props.draft.dpc5 ? 'Document importé' : '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">DPC6 - Photo terrain</td>
                            <td class="p-2">{{ props.draft.dpc6 ? 'Document importé' : '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">DPC7 - Photo terrain</td>
                            <td class="p-2">{{ props.draft.dpc7 ? 'Document importé' : '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">DPC8 - Photo terrain</td>
                            <td class="p-2">{{ props.draft.dpc8 ? 'Document importé' : '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">DPC11 - Notice matériaux</td>
                            <td class="p-2">{{ props.draft.dpc11 ? 'Document importé' : '—' }}</td>
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
                    <div class="text-xs text-gray-600 mb-1">Lu et approuvé – Signature du déclarant</div>
                    <div class="border rounded-md p-3 inline-flex w-full min-h-[120px] items-center justify-center bg-white">
                        <template v-if="props.draft.declarant_signature_image_url || props.draft.declarant_signature?.dataUrl">
                            <img :src="props.draft.declarant_signature_image_url || props.draft.declarant_signature?.dataUrl" alt="Signature déclarant"
                                class="h-20 object-contain" />
                        </template>
                        <template v-else>
                            <div class="text-gray-500 italic">Pas encore signée</div>
                        </template>
                    </div>
                    <div class="mt-2 text-[11px] text-gray-700">
                        Signé par <span class="font-semibold">{{ props.draft.declarant_signature?.signer_name || '—' }}</span>
                        <span v-if="props.draft.declarant_signature_signed_at"> • le {{ new Date(props.draft.declarant_signature_signed_at).toLocaleString('fr-FR') }}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>