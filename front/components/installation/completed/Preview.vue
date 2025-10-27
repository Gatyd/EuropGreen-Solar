<script setup lang="ts">
import Logo from '~/components/Logo.vue'

type YesNoUnknown = 'yes' | 'no' | 'unknown'

type TechnicalVisitDraft = {
    modules_installed: boolean
    inverters_installed: boolean
    dc_ac_box_installed: boolean
    battery_installed: boolean
    photo_modules: File | null
    photo_inverter: File | null
    client_signature?: { signer_name: string; dataUrl?: string }
    installer_signature?: { signer_name: string; dataUrl?: string }
}

const props = defineProps<{
    draft: TechnicalVisitDraft & {
        generated_at?: string
        photo_inverter_url?: string | null
        photo_modules_url?: string | null
        client_signature_image_url?: string | null
        client_signature_signed_at?: string | null
        installer_signature_image_url?: string | null
        installer_signature_signed_at?: string | null
    }
}>()

</script>

<template>
    <div class="inline-block w-full xl:min-h-[1122.66px] xl:mx-auto bg-white text-xs px-6 py-6">
        <!-- En-tête -->
        <div class="flex justify-between items-center mb-6">
            <div>
                <Logo size="md" />
            </div>
            <div class="text-right">
                <p class="text-2xl text-black font-normal mb-1">RAPPORT D'INSTALLATION</p>
                <!-- <p class="text-[11px] text-gray-500">Généré le {{
                    props.draft.generated_at ? new Date(props.draft.generated_at).toLocaleDateString('fr-FR') : new
                        Date().toLocaleDateString('fr-FR')
                }}</p> -->
                <p>18 rue de Berlin, 68000 Colmar GES, France</p>
                <p class="mb-1">N° SIREN: 932 121 536 <span class="mx-2">|</span> N° TVA: FR23932121536</p>
                <p>Numéro de téléphone: (+33) 09 70 70 26 56</p>
            </div>
        </div>

        <!-- Détails de la visite -->
        <!-- <div class="mb-4 text-sm font-semibold text-zinc-700">Détails</div> -->
        <div class="mb-4">
            <div class="text-sm font-semibold text-zinc-700 mb-2">1. Eléments installés</div>
            <div class="overflow-hidden rounded-md border border-zinc-200">
                <table class="w-full text-sm border-collapse">
                    <tbody>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Modules solaires</td>
                            <td class="p-2">{{ props.draft.modules_installed ? 'Oui' : 'Non' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Onduleurs / micro-onduleurs</td>
                            <td class="p-2">{{ props.draft.inverters_installed ? 'Oui' : 'Non' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Coffret DC/AC</td>
                            <td class="p-2">{{ props.draft.dc_ac_box_installed ? 'Oui' : 'Non' }}</td>
                        </tr>
                        <tr v-if="props.draft.battery_installed" class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Batterie</td>
                            <td class="p-2">{{ props.draft.battery_installed ? 'Oui' : 'Non' }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div class="mb-4">
            <div class="text-sm font-semibold text-zinc-700 mb-2">2. Photo des éléments installés</div>
            <div class="overflow-hidden rounded-md border border-zinc-200">
                <table class="w-full text-sm border-collapse">
                    <tbody>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-lg text-gray-600">Modules solaires</td>
                            <td class="p-2">
                                <template v-if="props.draft.photo_modules_url">
                                    <img :src="props.draft.photo_modules_url" alt="Photo modules solaires"
                                        class="max-h-56 rounded" />
                                </template>
                                <template v-else-if="props.draft.photo_modules">
                                    <span class="text-gray-500">Sera affichée après la soumission</span>
                                </template>
                                <template v-else>
                                    <span class="text-gray-500">Pas encore importée</span>
                                </template>
                            </td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-lg text-gray-600">Onduleurs / micro-onduleurs</td>
                            <td class="p-2">
                                <template v-if="props.draft.photo_inverter_url">
                                    <img :src="props.draft.photo_inverter_url" alt="Photo onduleurs"
                                        class="max-h-56 rounded" />
                                </template>
                                <template v-else-if="props.draft.photo_inverter">
                                    <span class="text-gray-500">Sera affichée après la soumission</span>
                                </template>
                                <template v-else>
                                    <span class="text-gray-500">Pas encore importée</span>
                                </template>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
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
                        <template
                            v-if="props.draft.client_signature_image_url || props.draft.client_signature?.dataUrl">
                            <img :src="props.draft.client_signature_image_url || props.draft.client_signature?.dataUrl"
                                alt="Signature client" class="h-20 object-contain" />
                        </template>
                        <template v-else>
                            <div class="text-gray-500 italic">Pas encore signée</div>
                        </template>
                    </div>
                    <div class="mt-2 text-[11px] text-gray-700">
                        Signé par <span class="font-semibold">{{ props.draft.client_signature?.signer_name || '—'
                        }}</span>
                        <span v-if="props.draft.client_signature_signed_at"> • le {{ new
                            Date(props.draft.client_signature_signed_at).toLocaleString('fr-FR') }}</span>
                    </div>
                </div>

                <!-- Installateur -->
                <div>
                    <div class="text-xs text-gray-600 mb-1">Signature de l'installateur</div>
                    <div
                        class="border rounded-md p-3 inline-flex w-full min-h-[120px] items-center justify-center bg-white">
                        <template
                            v-if="props.draft.installer_signature_image_url || props.draft.installer_signature?.dataUrl">
                            <img :src="props.draft.installer_signature_image_url || props.draft.installer_signature?.dataUrl"
                                alt="Signature installateur" class="h-20 object-contain" />
                        </template>
                        <template v-else>
                            <div class="text-gray-500 italic">Pas encore signée</div>
                        </template>
                    </div>
                    <div class="mt-2 text-[11px] text-gray-700">
                        Signé par <span class="font-semibold">{{ props.draft.installer_signature?.signer_name || '—'
                        }}</span>
                        <span v-if="props.draft.installer_signature_signed_at"> • le {{ new
                            Date(props.draft.installer_signature_signed_at).toLocaleString('fr-FR') }}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
