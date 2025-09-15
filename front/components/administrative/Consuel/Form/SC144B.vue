<script setup lang="ts">

const props = defineProps<{
    draft: sc144aDraft
    loading: boolean
}>()
const emit = defineEmits<{
    (e: 'submit'): void
}>()

type sc144aDraft = {
    client_name: string,
    site_address: string,
    // site_address_line2: string,
    client_postal_code: string,
    client_city: string,
    client_phone: string,
    connect_grid_by_consumption_install: boolean,
    connect_grid_at_delivery_point: boolean,
    other_dc_sources_no: boolean,
    other_dc_sources_yes: boolean,
    other_dc_sources_details: string,
    other_ac_sources_no: boolean,
    other_ac_sources_yes: boolean,
    other_ac_sources_details: string,
    modified_installation_no: boolean,
    modified_installation_yes: boolean,
    reference_date: string,
    permit_application: boolean,
    preliminary_declaration: boolean,
    contract_signature: boolean,
    order_acknowledgement: boolean,
    installer_company_name: string,
    installer_email: string,
    installer_address: string,
    installer_postal_code: string,
    installer_city: string,
    installer_phone: string,
    installer_fax: string,
    existing_install_energization_date: string,
    initial_pv_power: string,
    dc_overcurrent_protection_yes: boolean,
    dc_overcurrent_protection_no: boolean,
    modified_dc_only: boolean,
    modified_ac_only: boolean,
    modified_dc_ac: boolean,
    pv_power_without_existing: string,
    inverter_added_no: boolean,
    inverter_added_yes: boolean,
    inverter_added_count: string,
    inverter_replaced_no: boolean,
    inverter_replaced_yes: boolean,
    inverter_replaced_count: string,
    inverter_kept_no: boolean,
    inverter_kept_yes: boolean,
    inverter_kept_count: string,
    pv_module_string_count: string,
    pv_iscmax: string,
    pv_uocmax: string,
    pv_main_cable_section: string,
    pv_main_cable_voltage: string,
    pv_main_cable_temp_rating: string,
    dc_isolator_un: string,
    dc_isolator_in: string,
    dc_isolator_not_applicable: boolean,
    dc_polarity_to_earth_no: boolean,
    dc_polarity_to_earth_yes: boolean,
    inverter_identical_generator_count: string,
    inverter_brand_model: string,
    inverter_ext_decoupling: boolean,
    inverter_int_decoupling: boolean,
    connection_power_limited: boolean,
    connection_power_limited_details: string,
    connection_power_monitored: boolean,
    installer_name: string,
    installer_signature: any,
    signature_date: string,
    installer_stamp: any
    a_number_of_strings_1: string; a_number_of_strings_2: string; a_number_of_strings_3: string; a_number_of_strings_4: string; a_number_of_strings_5: string;
    b_iscmax_module_1: string; b_iscmax_module_2: string; b_iscmax_module_3: string; b_iscmax_module_4: string; b_iscmax_module_5: string;
    c_irm_modules_1: string; c_irm_modules_2: string; c_irm_modules_3: string; c_irm_modules_4: string; c_irm_modules_5: string;
    d_courant_admissible_cable_chaine_1: string; d_courant_admissible_cable_chaine_2: string; d_courant_admissible_cable_chaine_3: string; d_courant_admissible_cable_chaine_4: string; d_courant_admissible_cable_chaine_5: string;
    e_type_courant_protection_chaine_1: string; e_type_courant_protection_chaine_2: string; e_type_courant_protection_chaine_3: string; e_type_courant_protection_chaine_4: string; e_type_courant_protection_chaine_5: string;
    f_courant_admissible_cable_groupe_1: string; f_courant_admissible_cable_groupe_2: string; f_courant_admissible_cable_groupe_3: string; f_courant_admissible_cable_groupe_4: string; f_courant_admissible_cable_groupe_5: string;
    g_iscmax_groupe_1: string; g_iscmax_groupe_2: string; g_iscmax_groupe_3: string; g_iscmax_groupe_4: string; g_iscmax_groupe_5: string;
    h_type_courant_protection_groupe_1: string; h_type_courant_protection_groupe_2: string; h_type_courant_protection_groupe_3: string; h_type_courant_protection_groupe_4: string; h_type_courant_protection_groupe_5: string;
}

const state = toRef(props, 'draft')

const formSections = [
    {
        value: 'installer_info',
        label: 'Informations de l\'installateur',
        slot: 'installer_info'
    },
    {
        value: 'installation_info',
        label: 'Informations de l\'installation',
        slot: 'installation_info'
    },
    {
        value: 'a1_a2_a3',
        label: '(A1), (A2) et (A3)',
        slot: 'a1_a2_a3'
    },
    {
        value: 'cote_continu',
        label: 'COTE CONTINU',
        slot: 'cote_continu'
    },
    {
        value: 'tableau_cc',
        label: 'Tableau des caractéristiques de chaque groupe / chaîne PV',
        slot: 'tableau_cc'
    },
    {
        value: 'ac',
        label: 'AC',
        slot: 'ac'
    },
    {
        value: 'signature_stamp',
        label: 'Signature et Cachet',
        slot: 'signature_stamp'
    },
]

</script>

<template>
    <UForm :state="draft" class="space-y-3" @submit="emit('submit')">
        <UPageAccordion :default-value="['installer_info']" :items="formSections" type="multiple">
            <template #installer_info>
                <div class="grid grid-cols-12 gap-3 px-5 pb-4">
                    <UFormField label="Nom ou raison sociale" class="col-span-6">
                        <UInput v-model="state.installer_company_name" class="w-full" />
                    </UFormField>
                    <UFormField label="Email" class="col-span-6">
                        <UInput v-model="state.installer_email" class="w-full" />
                    </UFormField>
                    <UFormField label="Adresse" class="col-span-12">
                        <UInput v-model="state.installer_address" class="w-full" />
                    </UFormField>
                    <UFormField label="Code postal" class="col-span-6 md:col-span-2">
                        <UInput v-model="state.installer_postal_code" class="w-full" />
                    </UFormField>
                    <UFormField label="Commune" class="col-span-6 md:col-span-4">
                        <UInput v-model="state.installer_city" class="w-full" />
                    </UFormField>
                    <UFormField label="Téléphone" class="col-span-6 md:col-span-4">
                        <UInput v-model="state.installer_phone" class="w-full" />
                    </UFormField>
                    <UFormField label="Fax" class="col-span-6 md:col-span-2">
                        <UInput v-model="state.installer_fax" class="w-full" />
                    </UFormField>
                </div>
            </template>
            <template #installation_info>
                <div class="grid grid-cols-12 gap-3 px-5 pb-4">
                    <UFormField label="Nom du client" class="col-span-12">
                        <UInput v-model="state.client_name" class="w-full" />
                    </UFormField>
                    <UFormField label="Adresse" class="col-span-12">
                        <UInput v-model="state.site_address" class="w-full" />
                    </UFormField>
                    <UFormField label="Code postal" class="col-span-4 md:col-span-2">
                        <UInput v-model="state.client_postal_code" class="w-full" />
                    </UFormField>
                    <UFormField label="Commune" class="col-span-8 md:col-span-6">
                        <UInput v-model="state.client_city" class="w-full" />
                    </UFormField>
                    <UFormField label="Téléphone" class="col-span-12 md:col-span-4">
                        <UInput v-model="state.client_phone" class="w-full" />
                    </UFormField>
                </div>
            </template>
            <template #a1_a2_a3>
                <div class="grid grid-cols-12 gap-3 px-5 pb-4">
                    <UCheckbox v-model="state.connect_grid_by_consumption_install" class="col-span-12"
                        label="Raccordement au réseau public de distribution par l’installation de consommation" />
                    <UCheckbox v-model="state.connect_grid_at_delivery_point" class="col-span-12"
                        label="Raccordement au réseau public de distribution directement au point de livraison" />
                    <UFormField label="Autres sources d’alimentation DC :"
                        class="col-span-12 md:flex items-center gap-4" required>
                        <div class="grid grid-cols-6 items-center gap-5">
                            <UCheckbox v-model="state.other_dc_sources_no" label="Non" class="col-span-1" />
                            <UCheckbox v-model="state.other_dc_sources_yes" label="Oui" class="col-span-1" />
                            <UInput v-if="state.other_dc_sources_yes" v-model="state.other_dc_sources_details"
                                placeholder="Préciser" class="col-span-4" />
                        </div>
                    </UFormField>
                    <UFormField label="Autres sources d’alimentation AC :"
                        class="col-span-12 md:flex items-center gap-4" required>
                        <div class="grid grid-cols-6 items-center gap-5">
                            <UCheckbox v-model="state.other_ac_sources_no" label="Non" class="col-span-1" />
                            <UCheckbox v-model="state.other_ac_sources_yes" label="Oui" class="col-span-1" />
                            <UInput v-if="state.other_ac_sources_yes" v-model="state.other_ac_sources_details"
                                placeholder="Préciser" class="col-span-4" />
                        </div>
                    </UFormField>
                    <UFormField label="(A2) Modification de l’installation photovoltaïque :"
                        class="col-span-12 flex items-center gap-4" required>
                        <div class="flex items-center gap-4">
                            <UCheckbox v-model="state.modified_installation_no" label="Non" class="w-full" />
                            <UCheckbox v-model="state.modified_installation_yes" label="Oui" class="w-full" />
                        </div>
                    </UFormField>
                    <div v-if="state.modified_installation_yes" class="col-span-12 grid grid-cols-12 gap-2">
                        <p class="col-span-12 font-medium underline">A. Installation existante</p>
                        <UFormField class="col-span-12 flex items-center gap-4"
                            label="Date de la mise sous tension de l’installation de production existante :">
                            <UInput v-model="state.existing_install_energization_date" class="w-full" />
                        </UFormField>
                        <UFormField class="col-span-12 flex items-center gap-4"
                            label="Puissance initiale de production PV (en kVA) :">
                            <UInput v-model="state.initial_pv_power" type="number" class="w-full" />
                        </UFormField>
                        <UFormField label="Présence de dispositifs de protection contre les surintensités côté DC :"
                            class="col-span-12 flex items-center gap-4" required>
                            <div class="flex items-center gap-4">
                                <UCheckbox v-model="state.dc_overcurrent_protection_yes" label="Oui" class="w-full" />
                                <UCheckbox v-model="state.dc_overcurrent_protection_no" label="Non" class="w-full" />
                            </div>
                        </UFormField>
                        <UFormField label="Installation modifiée :" class="col-span-12 flex items-center gap-4"
                            required>
                            <div class="grid items-center grid-cols-12 gap-4">
                                <UCheckbox v-model="state.modified_dc_only" label="Uniquement côté DC"
                                    class="col-span-4" />
                                <UCheckbox v-model="state.modified_ac_only" label="Uniquement côté AC"
                                    class="col-span-4" />
                                <UCheckbox v-model="state.modified_dc_ac" label="Côté DC et AC" class="col-span-4" />
                            </div>
                        </UFormField>
                        <p class="col-span-12 font-medium underline">B. Partie nouvelle de l'installation</p>
                        <UFormField class="col-span-12 flex items-center gap-4"
                            label="Puissance de production PV (sans la partie existante) :">
                            <UInput v-model="state.pv_power_without_existing" type="number" class="w-full" />
                        </UFormField>
                        <UFormField label="Onduleur(s) ajoutés :" class="col-span-12 md:flex items-center gap-4"
                            required>
                            <div class="grid grid-cols-4 items-center gap-5">
                                <UCheckbox v-model="state.inverter_added_no" label="Non" class="col-span-1" />
                                <UCheckbox v-model="state.inverter_added_yes" label="Oui" class="col-span-1" />
                                <UInput v-if="state.inverter_added_yes" v-model="state.inverter_added_count"
                                    placeholder="Nombre" type="number" class="col-span-2" />
                            </div>
                        </UFormField>
                        <UFormField label="Onduleur(s) remplacé(s) :" class="col-span-12 md:flex items-center gap-4"
                            required>
                            <div class="grid grid-cols-4 items-center gap-5">
                                <UCheckbox v-model="state.inverter_replaced_no" label="Non" class="col-span-1" />
                                <UCheckbox v-model="state.inverter_replaced_yes" label="Oui" class="col-span-1" />
                                <UInput v-if="state.inverter_replaced_yes" v-model="state.inverter_replaced_count"
                                    placeholder="Nombre" type="number" class="col-span-2" />
                            </div>
                        </UFormField>
                        <UFormField label="Onduleur(s) conservé(s) :" class="col-span-12 md:flex items-center gap-4"
                            required>
                            <div class="grid grid-cols-4 items-center gap-5">
                                <UCheckbox v-model="state.inverter_kept_no" label="Non" class="col-span-1" />
                                <UCheckbox v-model="state.inverter_kept_yes" label="Oui" class="col-span-1" />
                                <UInput v-if="state.inverter_kept_yes" v-model="state.inverter_kept_count"
                                    placeholder="Nombre" type="number" class="col-span-2" />
                            </div>
                        </UFormField>
                    </div>
                    <UFormField label="(A3) Date de référence :" class="col-span-12 flex items-center gap-4" required>
                        <UInput type="date" v-model="state.reference_date" class="w-full" />
                    </UFormField>
                    <UCheckbox v-model="state.permit_application" label="Dépôt de demande de permis de construire"
                        class="col-span-12 md:col-span-6" />
                    <UCheckbox v-model="state.preliminary_declaration" label="Déclaration préalable de construction"
                        class="col-span-12 md:col-span-6" />
                    <UCheckbox v-model="state.contract_signature" label="Signature de marché"
                        class="col-span-12 md:col-span-6" />
                    <UCheckbox v-model="state.order_acknowledgement" label="Accusé de réception de commande"
                        class="col-span-12 md:col-span-6" />
                </div>
            </template>
            <template #cote_continu>
                <div class="grid grid-cols-12 gap-3 px-5 pb-4">
                    <p class="col-span-12 font-bold"><span class="text-sky-500">(1)</span> Module PV :</p>
                    <UFormField label="Nombre de chaines" class="col-span-12 md:col-span-6 flex items-center gap-4">
                        <UInput v-model="state.pv_module_string_count" type="number" class="w-full" />
                    </UFormField>
                    <UFormField label="U ocmax en V" class="col-span-12 md:col-span-6 flex items-center gap-4">
                        <UInput v-model="state.pv_uocmax" type="number" class="w-full" />
                    </UFormField>
                    <UFormField label="I scmax-générateur (ou optimiseur) PV"
                        class="col-span-12 flex items-center gap-4">
                        <UInput v-model="state.pv_iscmax" type="number" class="w-full" />
                    </UFormField>
                    <p class="col-span-12 font-bold"><span class="text-sky-500">(2)</span> Câble principal PV :</p>
                    <UFormField label="Section (en mm²)" class="col-span-12 md:col-span-6 flex items-center gap-4">
                        <UInput v-model="state.pv_main_cable_section" type="number" class="w-full" />
                    </UFormField>
                    <UFormField label="U" class="col-span-12 md:col-span-6 flex items-center gap-4">
                        <UInput v-model="state.pv_main_cable_voltage" type="number" class="w-full">
                            <template #trailing>
                                <UKbd variant="outline" value="V (en courant continu)" />
                            </template>
                        </UInput>
                    </UFormField>
                    <UFormField label="Température admissible sur l’âme (en °C)"
                        class="col-span-12 flex items-center gap-4">
                        <UInput v-model="state.pv_main_cable_temp_rating" type="number" class="w-full" />
                    </UFormField>
                    <p class="col-span-12 font-bold"><span class="text-sky-500">(3)</span> Interrupteur-Sectionneur
                        général DC :</p>
                    <UFormField label="U n (en V)" class="col-span-12 md:col-span-6 flex items-center gap-4">
                        <UInput v-model="state.dc_isolator_un" type="number" class="w-full" />
                    </UFormField>
                    <UFormField label="I n (en A)" class="col-span-12 md:col-span-6 flex items-center gap-4">
                        <UInput v-model="state.dc_isolator_in" type="number" class="w-full" />
                    </UFormField>
                    <UCheckbox v-model="state.dc_isolator_not_applicable" class="col-span-12"
                        label="Sans objet (ex : onduleur avec sectionneur intégré)" />
                    <div class="col-span-12 grid grid-cols-2 md:grid-cols-3 items-center gap-4">
                        <p class="col-span-2 md:col-span-1 font-bold"><span class="text-sky-500">(4)</span> Polarité à
                            la terre* :</p>
                        <UCheckbox v-model="state.dc_polarity_to_earth_no" label="Non" class="w-full" />
                        <UCheckbox v-model="state.dc_polarity_to_earth_yes" label="Oui" class="w-full" />
                    </div>
                    <p class="col-span-12 font-bold"><span class="text-sky-500">(5)</span> Onduleur :</p>
                    <UFormField label="Nombre d’onduleurs identiques au(x) générateur(s) PV"
                        class="col-span-12 flex items-center gap-4">
                        <UInput v-model="state.inverter_identical_generator_count" type="number" class="w-full" />
                    </UFormField>
                    <UFormField label="Marque et modèle" class="col-span-12 flex items-center gap-4">
                        <UInput v-model="state.inverter_brand_model" class="w-full" />
                    </UFormField>
                    <UFormField label="Sys. Découplage" required class="col-span-12 flex items-center gap-4">
                        <div class="grid grid-cols-2 items-center gap-4">
                            <UCheckbox v-model="state.inverter_ext_decoupling" label="externe" class="w-full" />
                            <UCheckbox v-model="state.inverter_int_decoupling" label="intégré à l'onduleur"
                                class="w-full" />
                        </div>
                    </UFormField>
                </div>
            </template>
            <template #tableau_cc>
                <div class="px-3 md:px-5 pb-4 space-y-4">
                    <div class="overflow-auto">
                        <table class="min-w-full border border-gray-300 text-xs">
                            <thead>
                                <tr class="bg-gray-100">
                                    <th class="border border-gray-300 p-1 text-left w-40">Paramètre</th>
                                    <th v-for="i in 5" :key="'col-head-' + i"
                                        class="border border-gray-300 p-1 w-16 text-center">{{ i }}</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td class="border border-gray-300 p-1">A. Nombre de chaînes</td>
                                    <td v-for="i in 5" :key="'a_' + i" class="border border-gray-300 p-0">
                                        <UInput v-model="(state as any)['a_number_of_strings_' + i]"
                                            :ui="{ base: 'rounded-none border-0 focus:ring-0' }" size="sm" />
                                    </td>
                                </tr>
                                <tr>
                                    <td class="border border-gray-300 p-1">B. Iscmax module</td>
                                    <td v-for="i in 5" :key="'b_' + i" class="border border-gray-300 p-0">
                                        <UInput v-model="(state as any)['b_iscmax_module_' + i]"
                                            :ui="{ base: 'rounded-none border-0 focus:ring-0' }" size="sm" />
                                    </td>
                                </tr>
                                <tr>
                                    <td class="border border-gray-300 p-1">C. IRM modules</td>
                                    <td v-for="i in 5" :key="'c_' + i" class="border border-gray-300 p-0">
                                        <UInput v-model="(state as any)['c_irm_modules_' + i]"
                                            :ui="{ base: 'rounded-none border-0 focus:ring-0' }" size="sm" />
                                    </td>
                                </tr>
                                <tr>
                                    <td class="border border-gray-300 p-1">D. Courant admissible câble chaîne</td>
                                    <td v-for="i in 5" :key="'d_' + i" class="border border-gray-300 p-0">
                                        <UInput v-model="(state as any)['d_courant_admissible_cable_chaine_' + i]"
                                            :ui="{ base: 'rounded-none border-0 focus:ring-0' }" size="sm" />
                                    </td>
                                </tr>
                                <tr>
                                    <td class="border border-gray-300 p-1">E. Type & courant protection chaîne</td>
                                    <td v-for="i in 5" :key="'e_' + i" class="border border-gray-300 p-0">
                                        <UInput v-model="(state as any)['e_type_courant_protection_chaine_' + i]"
                                            :ui="{ base: 'rounded-none border-0 focus:ring-0' }" size="sm" />
                                    </td>
                                </tr>
                                <tr>
                                    <td class="border border-gray-300 p-1">F. Courant admissible câble groupe</td>
                                    <td v-for="i in 5" :key="'f_' + i" class="border border-gray-300 p-0">
                                        <UInput v-model="(state as any)['f_courant_admissible_cable_groupe_' + i]"
                                            :ui="{ base: 'rounded-none border-0 focus:ring-0' }" size="sm" />
                                    </td>
                                </tr>
                                <tr>
                                    <td class="border border-gray-300 p-1">G. Iscmax groupe</td>
                                    <td v-for="i in 5" :key="'g_' + i" class="border border-gray-300 p-0">
                                        <UInput v-model="(state as any)['g_iscmax_groupe_' + i]"
                                            :ui="{ base: 'rounded-none border-0 focus:ring-0' }" size="sm" />
                                    </td>
                                </tr>
                                <tr>
                                    <td class="border border-gray-300 p-1">H. Type & courant protection groupe</td>
                                    <td v-for="i in 5" :key="'h_' + i" class="border border-gray-300 p-0">
                                        <UInput v-model="(state as any)['h_type_courant_protection_groupe_' + i]"
                                            :ui="{ base: 'rounded-none border-0 focus:ring-0' }" size="sm" />
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </template>
            <template #ac>
                <div class="grid grid-cols-12 px-5 pb-4">
                    <div class="col-span-12 grid grid-cols-2 md:grid-cols-4 items-center gap-4">
                        <p class="col-span-2 md:col-span-1 font-bold"><span class="text-sky-500">(6)</span> Branchement*:</p>
                        <UCheckbox v-model="state.connection_power_limited" label="Puissance limitée" class="w-full" />
                        <UCheckbox v-model="state.connection_power_monitored" label="Puissance surveillée"
                            class="w-full" />
                        <UInput v-if="state.connection_power_limited" v-model="state.connection_power_limited_details"
                            placeholder="Préciser" />
                    </div>
                </div>
            </template>
            <template #signature_stamp>
                <div class="grid grid-cols-12 gap-3 px-5 pb-4">
                    <CommonSignatureField v-model="state.installer_signature" label="Nom de l'installateur" required
                        class="col-span-12" />
                    <UFormField label="Cachet de l’installateur" class="col-span-12" required>
                        <UFileUpload v-model="state.installer_stamp" class="w-full" accept="image/png,image/jpeg"
                            :multiple="false" />
                    </UFormField>
                </div>
            </template>
        </UPageAccordion>
        <div class="flex items-center justify-end px-5 pb-4">
            <UButton type="submit" :loading="loading" label="Enregistrer" />
        </div>
    </UForm>
</template>
