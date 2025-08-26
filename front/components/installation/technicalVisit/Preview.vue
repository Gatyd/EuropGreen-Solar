<script setup lang="ts">
import Logo from '~/components/Logo.vue'

type YesNoUnknown = 'yes' | 'no' | 'unknown'

type TechnicalVisitDraft = {
    visit_date: string
    expected_installation_date: string
    roof_cover: string
    spare_tiles: boolean
    roof_shape: string
    roof_access: string
    roof_access_other: string
    nacelle_needed: YesNoUnknown
    truck_access: YesNoUnknown
    truck_access_note: string
    meter_type: string
    meter_type_other: string
    current_type: string
    reuse_existing_connection: boolean
    meter_position: string
    panel_to_board_distance_m: number | null
    meter_location_photo: File | null
    extra_required: boolean
    extra_materials: string
    client_signature?: { signer_name: string; dataUrl?: string }
    installer_signature?: { signer_name: string; dataUrl?: string }
}

const props = defineProps<{ draft: TechnicalVisitDraft }>()

const yn = (v: boolean) => (v ? 'Oui' : 'Non')
const ynu = (v: YesNoUnknown) => (v === 'yes' ? 'Oui' : v === 'no' ? 'Non' : 'Inconnu')
</script>

<template>
    <div class="inline-block w-full xl:min-h-[1122.66px] xl:mx-auto bg-white text-xs px-6 py-4">
        <!-- En-tête -->
        <div class="flex justify-between items-center mb-6">
            <div>
                <Logo size="sm" />
            </div>
            <div class="text-right">
                <p class="text-2xl text-black font-normal mb-1">RAPPORT DE VISITE TECHNIQUE</p>
                <p class="text-[11px] text-gray-500">Généré le {{ new Date().toLocaleDateString('fr-FR') }}</p>
            </div>
        </div>

        <!-- Détails de la visite -->
        <!-- <div class="mb-4 text-sm font-semibold text-zinc-700">Détails</div> -->
        <div class="overflow-hidden rounded-md border border-zinc-200">
            <table class="w-full text-sm border-collapse">
                <tbody>
                    <tr class="odd:bg-zinc-50">
                        <td class="w-[45%] p-2 text-gray-600">Date de la visite</td>
                        <td class="p-2">{{ props.draft.visit_date || '—' }}</td>
                    </tr>
                    <tr class="odd:bg-zinc-50">
                        <td class="p-2 text-gray-600">Date installation prévisionnelle</td>
                        <td class="p-2">{{ props.draft.expected_installation_date || '—' }}</td>
                    </tr>
                    <tr class="odd:bg-zinc-50">
                        <td class="p-2 text-gray-600">Type de couverture</td>
                        <td class="p-2">{{ props.draft.roof_cover || '—' }}</td>
                    </tr>
                    <tr class="odd:bg-zinc-50">
                        <td class="p-2 text-gray-600">Tuiles de rechange</td>
                        <td class="p-2">{{ yn(props.draft.spare_tiles) }}</td>
                    </tr>
                    <tr class="odd:bg-zinc-50">
                        <td class="p-2 text-gray-600">Forme du toit</td>
                        <td class="p-2">{{ props.draft.roof_shape || '—' }}</td>
                    </tr>
                    <tr class="odd:bg-zinc-50">
                        <td class="p-2 text-gray-600">Accès toiture</td>
                        <td class="p-2">
                            {{ props.draft.roof_access }}
                            <span v-if="props.draft.roof_access === 'Autre' && props.draft.roof_access_other"
                                class="text-gray-500">— {{ props.draft.roof_access_other }}</span>
                        </td>
                    </tr>
                    <tr class="odd:bg-zinc-50">
                        <td class="p-2 text-gray-600">Nacelle nécessaire</td>
                        <td class="p-2">{{ ynu(props.draft.nacelle_needed as any) }}</td>
                    </tr>
                    <tr class="odd:bg-zinc-50">
                        <td class="p-2 text-gray-600">Accès camion</td>
                        <td class="p-2">
                            {{ ynu(props.draft.truck_access as any) }}
                            <span v-if="props.draft.truck_access === 'no' && props.draft.truck_access_note"
                                class="text-gray-500">— {{ props.draft.truck_access_note }}</span>
                        </td>
                    </tr>
                    <tr class="odd:bg-zinc-50">
                        <td class="p-2 text-gray-600">Type de compteur</td>
                        <td class="p-2">
                            {{ props.draft.meter_type }}
                            <span v-if="props.draft.meter_type === 'Autre' && props.draft.meter_type_other"
                                class="text-gray-500">— {{ props.draft.meter_type_other }}</span>
                        </td>
                    </tr>
                    <tr class="odd:bg-zinc-50">
                        <td class="p-2 text-gray-600">Type de courant</td>
                        <td class="p-2">{{ props.draft.current_type || '—' }}</td>
                    </tr>
                    <tr class="odd:bg-zinc-50">
                        <td class="p-2 text-gray-600">Raccordement existant</td>
                        <td class="p-2">{{ yn(props.draft.reuse_existing_connection) }}</td>
                    </tr>
                    <tr class="odd:bg-zinc-50">
                        <td class="p-2 text-gray-600">Position du compteur</td>
                        <td class="p-2">{{ props.draft.meter_position || '—' }}</td>
                    </tr>
                    <tr class="odd:bg-zinc-50">
                        <td class="p-2 text-gray-600">Distance panneaux → tableau (m)</td>
                        <td class="p-2">{{ props.draft.panel_to_board_distance_m ?? '—' }}</td>
                    </tr>
                    <tr class="odd:bg-zinc-50">
                        <td class="p-2 text-gray-600">Photo localisation du compteur</td>
                        <td class="p-2">
                            <span v-if="!props.draft.meter_location_photo" class="text-gray-500">Pas encore
                                importée</span>
                            <span v-else class="text-gray-500">Sera affichée après la soumission</span>
                        </td>
                    </tr>
                    <tr class="odd:bg-zinc-50">
                        <td class="p-2 text-gray-600">Matériel supplémentaire nécessaire</td>
                        <td class="p-2">{{ yn(props.draft.extra_required) }}</td>
                    </tr>
                    <tr v-if="props.draft.extra_required" class="odd:bg-zinc-50">
                        <td class="p-2 text-gray-600">Détails matériel</td>
                        <td class="p-2 whitespace-pre-line">{{ props.draft.extra_materials || '—' }}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Signatures -->
        <div class="mt-8">
            <div class="mb-3 text-sm font-semibold text-zinc-700">Signatures</div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Client -->
                <div>
                    <div class="text-xs text-gray-600 mb-1">Signature du client</div>
                    <div
                        class="border rounded-md p-3 inline-flex w-full min-h-[120px] items-center justify-center bg-white">
                        <template v-if="props.draft.client_signature?.dataUrl">
                            <img :src="props.draft.client_signature?.dataUrl" alt="Signature client"
                                class="h-20 object-contain" />
                        </template>
                        <template v-else>
                            <div class="text-gray-500 italic">Pas encore signée</div>
                        </template>
                    </div>
                    <div class="mt-2 text-[11px] text-gray-700">
                        Signé par <span class="font-semibold">{{ props.draft.client_signature?.signer_name || '—'
                            }}</span>
                    </div>
                </div>

                <!-- Installateur -->
                <div>
                    <div class="text-xs text-gray-600 mb-1">Signature de l'installateur</div>
                    <div
                        class="border rounded-md p-3 inline-flex w-full min-h-[120px] items-center justify-center bg-white">
                        <template v-if="props.draft.installer_signature?.dataUrl">
                            <img :src="props.draft.installer_signature?.dataUrl" alt="Signature installateur"
                                class="h-20 object-contain" />
                        </template>
                        <template v-else>
                            <div class="text-gray-500 italic">Pas encore signée</div>
                        </template>
                    </div>
                    <div class="mt-2 text-[11px] text-gray-700">
                        Signé par <span class="font-semibold">{{ props.draft.installer_signature?.signer_name || '—'
                            }}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
