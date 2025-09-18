<script setup lang="ts">
import { AdministrativeConsuelFormSC144CCaracteristiques } from '#components';


const props = defineProps<{
    draft: sc144cDraft
    loading: boolean
}>()
const emit = defineEmits<{
    (e: 'submit'): void
}>()

type sc144cDraft = {
    client_name: string,
    site_address: string,
    // site_address_line2: string,
    client_postal_code: string,
    client_city: string,
    client_phone: string,
    connect_grid_by_consumption_install: boolean,
    connect_grid_at_delivery_point: boolean,
    no_connect_grid: boolean,
    dc_bus_photovoltaic_yes: boolean,
    dc_bus_photovoltaic_no: boolean,
    ac_bus_photovoltaic_yes: boolean,
    ac_bus_photovoltaic_no: boolean,
    other_dc_sources_no: boolean,
    other_dc_sources_yes: boolean,
    other_dc_sources_details: string,
    other_ac_sources_no: boolean,
    other_ac_sources_yes: boolean,
    other_ac_sources_details: string,
    stand_alone_installation_yes: boolean,
    stand_alone_installation_no: boolean,
    modified_installation_no: boolean,
    modified_installation_yes: boolean,
    adding_batteries_yes: boolean,
    adding_batteries_no: boolean,
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
    dc_battery_isolator_un: string,
    dc_battery_isolator_in: string,
    dc_battery_isolator_not_applicable: boolean,
    dc_battery_isolator_integrated_yes: boolean,
    dc_battery_isolator_integrated_no: boolean,
    dc_other_isolator_yes: boolean,
    dc_other_isolator_no: boolean,
    dc_other_isolator_un: string,
    dc_other_isolator_in: string,
    dc_circuit_isolator_yes: boolean,
    dc_circuit_isolator_no: boolean,
    dc_circuit_isolator_un: string,
    dc_circuit_isolator_in: string,
    ac_isolator_yes: boolean,
    ac_isolator_no: boolean,
    ac_isolator_un: string,
    ac_isolator_in: string,
    dc_polarity_to_earth_no: boolean,
    dc_polarity_to_earth_yes: boolean,
    inverter_identical_generator_count: string,
    inverter_brand_model: string,
    inverter_na_decoupling: boolean,
    inverter_ext_decoupling: boolean,
    inverter_int_decoupling: boolean,
    connection_power_limited: boolean,
    connection_power_limited_details: string,
    connection_power_monitored: boolean,
    installer_name: string,
    installer_signature: any,
    signature_date: string,
    installer_stamp: any
    // (5b) Inverter-charger
    inverter_charger_brand_model: string
    inverter_charger_reference: string
    battery_converter_subset_reference: string
    inverter_charger_decoupling_na: boolean
    inverter_charger_decoupling_external: boolean
    inverter_charger_decoupling_integrated: boolean
    // (5c)
    decoupling_protection_verified_commitment: boolean
    // (6a) DC distribution indirect contact protection
    dc_indirect_contact_by_slt: boolean
    dc_indirect_contact_slt_tt: boolean
    dc_indirect_contact_slt_it: boolean
    dc_indirect_contact_slt_commitment_441: boolean
    dc_indirect_contact_tt_no_galvanic_separation_commitment: boolean
    dc_indirect_contact_it_with_galvanic_separation_commitment: boolean
    dc_indirect_contact_cpi_integrated_yes: boolean
    dc_indirect_contact_cpi_integrated_no: boolean
    dc_indirect_contact_tbts_tbtp: boolean
    dc_indirect_contact_tbts_tbtp_galvanic_separation_commitment: boolean
    dc_indirect_contact_electrical_separation: boolean
    dc_indirect_contact_electrical_separation_charge_regulator_branch: boolean
    dc_indirect_contact_electrical_separation_galvanic_on_battery_input: boolean
    dc_indirect_contact_electrical_separation_galvanic_regulator_commitment: boolean
    dc_indirect_contact_electrical_separation_article_413_commitment: boolean
    dc_indirect_contact_intrinsic_microinverter_battery_subset: boolean
    // (6b) SLT autonomous mode
    autonomous_mode_slt_description: string
    autonomous_mode_neutral_contactor_management_commitment: boolean
    // (7a) DC distribution or battery
    udc_voltage: string
    // (7b) Lead battery
    lead_battery_cxu_le_1000: boolean
    lead_battery_cxu_gt_1000: boolean
    lead_battery_ventilation_natural: boolean
    lead_battery_ventilation_forced: boolean
    lead_battery_ventilation_none: boolean
    // (7c) Li-ion battery
    li_ion_battery_count: string
    li_ion_battery_room_yes_commitment: boolean
    li_ion_battery_room_no_commitment: boolean
    li_ion_battery_outside_room_energy_le_15kwh: boolean
    li_ion_battery_outside_room_energy_gt_15kwh: boolean
    // (7d) Other battery
    other_battery_description: string
    other_battery_norm_and_installation_commitment: boolean
    // A. Nombre de chaînes (colonnes 1..5)
    a_number_of_strings_1: string
    a_number_of_strings_2: string
    a_number_of_strings_3: string
    a_number_of_strings_4: string
    a_number_of_strings_5: string
    // B. Type & courant assigné protection sur une chaîne (colonnes 1..5)
    b_chain_protection_type_in_1: string
    b_chain_protection_type_in_2: string
    b_chain_protection_type_in_3: string
    b_chain_protection_type_in_4: string
    b_chain_protection_type_in_5: string
    // C. Type & courant assigné protection de groupes (colonnes 1..5)
    c_group_protection_type_in_1: string
    c_group_protection_type_in_2: string
    c_group_protection_type_in_3: string
    c_group_protection_type_in_4: string
    c_group_protection_type_in_5: string
    // D. Courant assigné protection câble principal PV
    d_main_pv_cable_not_applicable: boolean
    d_main_pv_cable_yes: boolean
    d_main_pv_cable_in: string
    d_main_pv_cable_assured_by: string
    // E. Courant assigné protection câble batterie
    e_battery_cable_in: string
    e_battery_cable_integrated_enclosure: boolean
    // F. Courant assigné protection câble régulateur
    f_regulator_cable_not_applicable: boolean
    f_regulator_cable_yes: boolean
    f_regulator_cable_in: string
    // G. Courant assigné protection câble utilisation DC
    g_dc_usage_cable_not_applicable: boolean
    g_dc_usage_cable_yes: boolean
    g_dc_usage_cable_in: string
    // H. Courant assigné protection câble DC onduleur
    h_inverter_dc_cable_not_applicable: boolean
    h_inverter_dc_cable_yes: boolean
    h_inverter_dc_cable_in: string
    // I. Courant assigné protection coffret distribution DC
    i_dc_distribution_box_not_applicable: boolean
    i_dc_distribution_box_yes: boolean
    i_dc_distribution_box_in: string
    // J. Courant assigné protection câble DC autre source AC
    j_other_ac_source_dc_cable_not_applicable: boolean
    j_other_ac_source_dc_cable_yes: boolean
    j_other_ac_source_dc_cable_in: string
}

const state = toRef(props, 'draft')

const formSections = [
    {
        value: 'installer_info',
        label: 'INSTALLATEUR',
        slot: 'installer_info'
    },
    {
        value: 'installation_info',
        label: 'INSTALLATION-SITE',
        slot: 'installation_info'
    },
    {
        value: 'a1_a2_a3',
        label: '(A1), (A2) et (A3)',
        slot: 'a1_a2_a3'
    },
    {
        value: 'modification_installation',
        label: 'INSTALLATION AVEC MODIFICATION DE PUISSANCE OU RENOVEE',
        slot: 'modification_installation'
    },
    {
        value: 'caracteristiques_techniques',
        label: 'CARACTERISTIQUES TECHNIQUES',
        slot: 'caracteristiques_techniques'
    },
    {
        value: 'tableau_ct',
        label: 'TABLEAU DES CARACTERISTIQUES DE CHAQUE GROUPE / CHAINE PV',
        slot: 'tableau_ct'
    },
    {
        value: 'ac',
        label: 'RACCORDEMENT COTE AC',
        slot: 'ac'
    },
    {
        value: 'signature_stamp',
        label: 'SIGNATURE ET CACHET',
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
                    <UCheckbox v-model="state.no_connect_grid" class="col-span-12"
                        label="Non raccordée au réseau public de distribution (installation autonome)" />
                    <p class="col-span-12 md:col-span-6 font-medium">Photovoltaïque sur bus à courant continu :</p>
                    <UCheckbox v-model="state.dc_bus_photovoltaic_yes" class="col-span-6 md:col-span-1" label="Oui" />
                    <UCheckbox v-model="state.dc_bus_photovoltaic_no" class="col-span-6 md:col-span-1" label="Non" />
                    <p class="col-span-12 md:col-span-6 font-medium">Photovoltaïque sur bus à courant alternatif :</p>
                    <UCheckbox v-model="state.ac_bus_photovoltaic_yes" class="col-span-6 md:col-span-1" label="Oui" />
                    <UCheckbox v-model="state.ac_bus_photovoltaic_no" class="col-span-6 md:col-span-1" label="Non" />
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
                    <p class="col-span-12 md:col-span-8 font-medium">Installation autonome ou installation raccordée au réseau :</p>
                    <UCheckbox v-model="state.stand_alone_installation_no" class="col-span-6 md:col-span-2" label="Non" />
                    <UCheckbox v-model="state.stand_alone_installation_yes" class="col-span-6 md:col-span-2" label="Oui" />
                    <UFormField label="(A2) Modification de l’installation photovoltaïque :"
                        class="col-span-12 flex items-center gap-4" required>
                        <div class="flex items-center gap-4">
                            <UCheckbox v-model="state.modified_installation_no" label="Non" class="w-full" />
                            <UCheckbox v-model="state.modified_installation_yes" label="Oui" class="w-full" />
                        </div>
                    </UFormField>
                    <p class="col-span-12 md:col-span-4 font-medium">Ajout de battéries :</p>
                    <UCheckbox v-model="state.adding_batteries_no" class="col-span-6 md:col-span-2" label="Non" />
                    <UCheckbox v-model="state.adding_batteries_yes" class="col-span-6 md:col-span-2" label="Oui" />
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
            <template #modification_installation>
                    <div class="col-span-12 grid grid-cols-12 gap-2 pb-4">
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
            </template>
            <template #caracteristiques_techniques>
                <AdministrativeConsuelFormSC144CCaracteristiques :state="state" />
            </template>
            <template #tableau_ct>
                <AdministrativeConsuelFormSC144CTable :state="state" />
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
