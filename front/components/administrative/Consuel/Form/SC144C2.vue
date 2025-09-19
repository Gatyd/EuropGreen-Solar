<script setup lang="ts">
const props = defineProps<{
    draft: sc144cDraft
    loading: boolean
}>()
const emit = defineEmits<{
    (e: 'submit'): void
}>()

type sc144cDraft = {
    // --- PARTIE 1 (champs existants conservés) ---
    client_name: string
    client_email: string
    site_address: string
    client_postal_code: string
    client_city: string
    client_phone: string
    connect_grid_by_consumption_install: boolean
    connect_grid_at_delivery_point: boolean
    connect_grid_at_delivery_point_conductors_section: string
    no_connect_grid: boolean
    pv_installed_roof: boolean
    pv_installed_ground: boolean
    battery_storage_yes: boolean
    battery_storage_no: boolean
    other_ac_sources_no: boolean
    other_ac_sources_yes: boolean
    other_ac_sources_details: string
    stand_alone_installation_yes: boolean
    stand_alone_installation_no: boolean
    modified_installation_no: boolean
    modified_installation_yes: boolean
    reference_date: string
    permit_application: boolean
    preliminary_declaration: boolean
    contract_signature: boolean
    order_acknowledgement: boolean
    installer_company_name: string
    installer_full_name: string
    existing_install_energization_date: string
    initial_pv_power: string
    dc_overcurrent_protection_yes: boolean
    dc_overcurrent_protection_no: boolean
    pv_power_without_existing: string
    inverter_added_no: boolean
    inverter_added_yes: boolean
    inverter_added_count: string
    inverter_replaced_no: boolean
    inverter_replaced_yes: boolean
    inverter_replaced_count: string
    inverter_kept_no: boolean
    inverter_kept_yes: boolean
    inverter_kept_count: string
    subassembly_inverter_battery_added: boolean
    subassembly_inverter_battery_added_count: string
    subassembly_inverter_battery_kept: boolean
    subassembly_inverter_battery_kept_count: string
    subassembly_inverter_battery_replaced: boolean
    subassembly_inverter_battery_replaced_count: string

    // --- PARTIE 2 : Générateur PV ---
    pv_iscmax: string
    pv_uocmax: string
    pv_main_cable_section: string
    pv_main_cable_voltage: string
    pv_main_cable_temp_90: boolean
    pv_main_cable_temp_ge_120: boolean

    // (3) Micro-onduleur PV
    micro_inverter_identical_count: string
    micro_inverter_monophase: boolean
    micro_inverter_triphase: boolean
    micro_inverter_brand_model_line1: string
    micro_inverter_brand_model_line2: string
    micro_inverter_decoupling_integrated: boolean
    micro_inverter_decoupling_external: boolean

    // --- PARTIE 3 : Raccordement AC ---
    connection_power_limited: boolean
    connection_power_monitored: boolean
    connection_board_principal: boolean
    connection_board_divisionnaire: boolean
    connection_case_1: boolean
    connection_case_2: boolean
    connection_case_3: boolean
    connection_case_4: boolean

    // --- PARTIE 4 : Stockage micro-onduleur / chargeur batterie ---
    storage_micro_inverter_monophase: boolean
    storage_micro_inverter_triphase: boolean
    storage_micro_inverter_charger_battery_reference: string
    storage_micro_inverter_decoupling_integrated: boolean
    storage_micro_inverter_decoupling_external: boolean

    // (5b) Protection contacts indirects DC batterie
    storage_battery_dc_with_galvanic_isolation: boolean
    storage_battery_dc_it_monitor_integrated: boolean
    storage_battery_dc_it_cpi_external: boolean
    storage_battery_dc_without_galvanic_isolation: boolean

    // --- PARTIE 4 suite / (6a)(6b)(6c) Batteries ---
    battery_udc_voltage: string
    battery_lithium_subset_count: string
    battery_lithium_unit_energy_kwh: string
    battery_lithium_room: boolean
    battery_lithium_outside_room: boolean
    battery_lithium_outside_energy_le_15kwh: boolean
    battery_lithium_outside_energy_gt_15kwh: boolean
    battery_other_description: string
    battery_other_norm_installation_compliance: boolean

    // --- PARTIE 5 : Mode autonome ---
    autonomous_mode_slt_tns: boolean
    autonomous_mode_slt_tt: boolean

    // --- PARTIE 6 : Autres sources AC ---
    other_ac_source_switch_voltage_vac: string
    other_ac_source_switch_current_in: string

    // --- Signature ---
    technical_contact_phone: string
    installer_name: string
    installer_signature: any
    signature_date: string
    installer_stamp: any
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
        label: 'PARTIE 1 : INSTALLATION AVEC MODIFICATION DE PUISSANCE OU RENOVEE',
        slot: 'modification_installation'
    },
    {
        value: 'caracteristiques_techniques',
        label: 'PARTIE 2 : CARACTERISTIQUES TECHNIQUES GENERATEUR PV',
        slot: 'caracteristiques_techniques'
    },
    {
        value: 'raccordement_ac',
        label: 'PARTIE 3 : RACCORDEMENT COTE AC',
        slot: 'raccordement_ac'
    },
    {
        value: 'part_4',
        label: 'PARTIE 4 : PRÉSENCE D’UN ENSEMBLE DE STOCKAGE PAR MICRO-ONDULEUR - CHARGEUR BATTERIE',
        slot: 'part_4'
    },
    {
        value: 'part_5',
        label: 'PARTIE 5 : RÉALIMENTATION EN MODE AUTONOME',
        slot: 'part_5'
    },
    {
        value: 'part_6',
        label: 'PARTIE 6 : AUTRES SOURCES D’ALIMENTATION AC QUE LE GENERATEUR PV ET LA BATTERIE',
        slot: 'part_6'
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
                <div class="grid grid-cols-1 gap-3 px-5 pb-4">
                    <UFormField label="Nom de l'installateur" class="col-span-6">
                        <UInput v-model="state.installer_full_name" class="w-full" />
                    </UFormField>
                    <UFormField label="Entreprise" class="col-span-6">
                        <UInput v-model="state.installer_company_name" class="w-full" />
                    </UFormField>
                </div>
            </template>
            <template #installation_info>
                <div class="grid grid-cols-12 gap-3 px-5 pb-4">
                    <UFormField label="Nom du client" class="col-span-6">
                        <UInput v-model="state.client_name" class="w-full" />
                    </UFormField>
                    <UFormField label="Email" class="col-span-6">
                        <UInput v-model="state.client_email" class="w-full" />
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
                <div class="grid grid-cols-12 items-center gap-3 px-5 pb-4">
                    <UCheckbox v-model="state.connect_grid_by_consumption_install" class="col-span-12"
                        label="Raccordement au réseau public de distribution par l’installation de consommation" />
                    <UCheckbox v-model="state.connect_grid_at_delivery_point" class="col-span-10"
                        label="Raccordement au réseau public de distribution directement au point de livraison" />
                    <UInput placeholder="Section(mm²)" class="col-span-2 w-full"
                        v-model="state.connect_grid_at_delivery_point_conductors_section" />
                    <UCheckbox v-model="state.no_connect_grid" class="col-span-12"
                        label="Non raccordée au réseau public de distribution (installation autonome)" />
                    <p class="col-span-12 md:col-span-6 font-medium">Position du champ PV :</p>
                    <UCheckbox v-model="state.pv_installed_roof" class="col-span-6 md:col-span-3"
                        label="Installé en toiture" />
                    <UCheckbox v-model="state.pv_installed_ground" class="col-span-6 md:col-span-3"
                        label="Installé au sol" />
                    <p class="col-span-12 md:col-span-6 font-medium">Présence d'un stockage par batterie :</p>
                    <UCheckbox v-model="state.battery_storage_yes" class="col-span-6 md:col-span-1" label="Oui" />
                    <UCheckbox v-model="state.battery_storage_no" class="col-span-6 md:col-span-1" label="Non" />
                    <UFormField label="Autres sources d’alimentation AC :"
                        class="col-span-12 md:flex items-center gap-4" required>
                        <div class="grid grid-cols-6 items-center gap-5">
                            <UCheckbox v-model="state.other_ac_sources_no" label="Non" class="col-span-1" />
                            <UCheckbox v-model="state.other_ac_sources_yes" label="Oui" class="col-span-1" />
                            <UInput v-if="state.other_ac_sources_yes" v-model="state.other_ac_sources_details"
                                placeholder="Préciser" class="col-span-4" />
                        </div>
                    </UFormField>
                    <p class="col-span-12 md:col-span-8 font-medium">Fonctionnement possible de l’installation en mode
                        autonome</p>
                    <UCheckbox v-model="state.stand_alone_installation_no" class="col-span-6 md:col-span-2"
                        label="Non" />
                    <UCheckbox v-model="state.stand_alone_installation_yes" class="col-span-6 md:col-span-2"
                        label="Oui" />
                    <UFormField label="(A2) Modification de l’installation photovoltaïque :"
                        class="col-span-12 flex items-center gap-4" required>
                        <div class="flex items-center gap-4">
                            <UCheckbox v-model="state.modified_installation_no" label="Non" class="w-full" />
                            <UCheckbox v-model="state.modified_installation_yes" label="Oui" class="w-full" />
                        </div>
                    </UFormField>
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
                    <p class="col-span-12 font-medium underline">B. Partie nouvelle de l'installation</p>
                    <UFormField class="col-span-12 flex items-center gap-4"
                        label="Puissance de production PV (sans la partie existante) :">
                        <UInput v-model="state.pv_power_without_existing" type="number" class="w-full" />
                    </UFormField>
                    <UFormField label="Onduleur(s) ajoutés :" class="col-span-12 md:flex items-center gap-4" required>
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
                    <p class="col-span-12 font-medium">Sous-ensemble micro-onduleur(s) + batterie :</p>
                    <div class="col-span-12 md:col-span-4 grid items-center grid-cols-2">
                        <UCheckbox v-model="state.subassembly_inverter_battery_added" label="Ajouté(s)" />
                        <UInput v-if="state.subassembly_inverter_battery_added"
                            v-model="state.subassembly_inverter_battery_added_count" placeholder="Nombre"
                            type="number" />
                    </div>
                    <div class="col-span-12 md:col-span-4 grid items-center grid-cols-2">
                        <UCheckbox v-model="state.subassembly_inverter_battery_kept" label="Conservé(s)" />
                        <UInput v-if="state.subassembly_inverter_battery_kept"
                            v-model="state.subassembly_inverter_battery_kept_count" placeholder="Nombre"
                            type="number" />
                    </div>
                    <div class="col-span-12 md:col-span-4 grid items-center grid-cols-2">
                        <UCheckbox v-model="state.subassembly_inverter_battery_replaced" label="Remplacé(s)" />
                        <UInput v-if="state.subassembly_inverter_battery_replaced"
                            v-model="state.subassembly_inverter_battery_replaced_count" placeholder="Nombre"
                            type="number" />
                    </div>
                </div>
            </template>
            <template #caracteristiques_techniques>
                <div class="grid grid-cols-12 gap-3 px-5 pb-4">
                    <p class="col-span-12 font-semibold"><span class="text-sky-500">(1)</span> Modules PV :</p>
                    <UFormField label="Iscmax générateur (A)" class="col-span-12 md:col-span-6 flex items-center gap-4">
                        <UInput v-model="state.pv_iscmax" type="number" class="w-full" />
                    </UFormField>
                    <UFormField label="Uocmax générateur (Vdc)"
                        class="col-span-12 md:col-span-6 flex items-center gap-4">
                        <UInput v-model="state.pv_uocmax" type="number" class="w-full" />
                    </UFormField>
                    <p class="col-span-12 font-semibold"><span class="text-sky-500">(2)</span> Câble DC - PV :</p>
                    <UFormField label="Section (mm²)" class="col-span-12 md:col-span-6 flex items-center gap-4">
                        <UInput v-model="state.pv_main_cable_section" type="number" class="w-full" />
                    </UFormField>
                    <UFormField label="Tension U (Vdc)" class="col-span-12 md:col-span-6 flex items-center gap-4">
                        <UInput v-model="state.pv_main_cable_voltage" type="number" class="w-full" />
                    </UFormField>
                    <div class="col-span-12 flex items-center gap-4">
                        <p class="font-medium">Température admissible sur l’âme :</p>
                        <UCheckbox v-model="state.pv_main_cable_temp_90" label="90°C" />
                        <UCheckbox v-model="state.pv_main_cable_temp_ge_120" label="≥120°C" />
                    </div>
                    <p class="col-span-12 font-semibold"><span class="text-sky-500">(3)</span> Micro-onduleur PV :</p>
                    <UFormField label="Nombre micro-onduleurs identiques"
                        class="col-span-12 md:col-span-8 flex items-center gap-4">
                        <UInput v-model="state.micro_inverter_identical_count" type="number" class="w-full" />
                    </UFormField>
                    <div class="col-span-12 md:col-span-4 flex items-center gap-4">
                        <UCheckbox v-model="state.micro_inverter_monophase" label="Monophasé" />
                        <UCheckbox v-model="state.micro_inverter_triphase" label="Triphasé" />
                    </div>
                    <UFormField label="Marque et Modèle (ligne 1)" class="col-span-12">
                        <UInput v-model="state.micro_inverter_brand_model_line1" class="w-full" />
                    </UFormField>
                    <UFormField label="Marque et Modèle (ligne 2)" class="col-span-12">
                        <UInput v-model="state.micro_inverter_brand_model_line2" class="w-full" />
                    </UFormField>
                    <div class="col-span-12 grid grid-cols-2 md:grid-cols-4 gap-4">
                        <p class="col-span-2 md:col-span-1 font-medium">Sys. Découplage* :</p>
                        <UCheckbox v-model="state.micro_inverter_decoupling_integrated" label="intégré" />
                        <UCheckbox v-model="state.micro_inverter_decoupling_external" label="externe" />
                    </div>
                </div>
            </template>
            <template #raccordement_ac>
                <div class="grid grid-cols-12 gap-3 px-5 pb-4">
                    <p class="col-span-12 font-semibold"><span class="text-sky-500">(4a)</span> Branchement* :</p>
                    <UCheckbox v-model="state.connection_power_limited" class="col-span-6 md:col-span-3"
                        label="Puissance limitée" />
                    <UCheckbox v-model="state.connection_power_monitored" class="col-span-6 md:col-span-3"
                        label="Puissance surveillée" />
                    <p class="col-span-12 font-semibold"><span class="text-sky-500">(4b)</span> Raccordement via
                        installation de consommation :</p>
                    <div class="col-span-12 grid grid-cols-6 gap-4 items-center">
                        <p class="col-span-4 font-medium">Raccordement de l’installation de production à un tableau :</p>
                        <UCheckbox v-model="state.connection_board_principal" label="Principal" />
                        <UCheckbox v-model="state.connection_board_divisionnaire" label="Divisionnaire" />
                    </div>
                    <p class="col-span-12 font-medium">Mise en oeuvre réalisée selon l’un des cas suivants :</p>
                    <div class="col-span-12 grid grid-cols-12 gap-2">
                        <UCheckbox v-model="state.connection_case_1" class="col-span-12"
                            label="Cas 1 : Protection amont en dehors du tableau consommation (In ≤ Ir AGCP)" />
                        <UCheckbox v-model="state.connection_case_2" class="col-span-12"
                            label="Cas 2 : Protection amont dans le tableau de consommation (In ≤ Ir AGCP)" />
                        <UCheckbox v-model="state.connection_case_3" class="col-span-12"
                            label="Cas 3 : Sans protection supplémentaire en amont des circuits" />
                        <UCheckbox v-model="state.connection_case_4" class="col-span-12"
                            label="Cas 4 : Autres cas de raccordement" />
                    </div>
                </div>
            </template>
            <template #part_4>
                <div class="grid grid-cols-12 items-center gap-3 px-5 pb-4">
                    <p class="col-span-12 font-semibold"><span class="text-sky-500">(5a)</span> Micro-onduleur - chargeur de
                        batterie* :</p>
                    <div class="col-span-12 md:col-span-4 flex items-center gap-4">
                        <UCheckbox v-model="state.storage_micro_inverter_monophase" label="Monophasé" />
                        <UCheckbox v-model="state.storage_micro_inverter_triphase" label="Triphasé" />
                    </div>
                    <UFormField label="Référence ensemble" class="col-span-12 md:col-span-8 flex items-center gap-4">
                        <UInput v-model="state.storage_micro_inverter_charger_battery_reference" class="w-full" />
                    </UFormField>
                    <div class="col-span-12 grid grid-cols-2 md:grid-cols-4 gap-4">
                        <p class="col-span-2 md:col-span-1 font-medium">Sys. Découplage* :</p>
                        <UCheckbox v-model="state.storage_micro_inverter_decoupling_integrated" label="intégré" />
                        <UCheckbox v-model="state.storage_micro_inverter_decoupling_external" label="externe" />
                    </div>
                    <p class="col-span-12 font-semibold"><span class="text-sky-500">(5b)</span> Protection contacts
                        indirects DC batterie :</p>
                    <div class="col-span-12 grid grid-cols-12 gap-2">
                        <UCheckbox v-model="state.storage_battery_dc_with_galvanic_isolation" class="col-span-12"
                            label="Avec isolation galvanique AC/DC" />
                        <div v-if="state.storage_battery_dc_with_galvanic_isolation"
                            class="col-span-12 grid grid-cols-12 gap-2 pl-4">
                            <UCheckbox v-model="state.storage_battery_dc_it_monitor_integrated" class="col-span-12"
                                label="Disposition de contrôle de l’isolement en DC intégrée à l’onduleur" />
                            <UCheckbox v-model="state.storage_battery_dc_it_cpi_external" class="col-span-12"
                                label="Contrôleur Permanent d’Isolement (CPI) externe à l’onduleur" />
                        </div>
                        <UCheckbox v-model="state.storage_battery_dc_without_galvanic_isolation" class="col-span-12"
                            label="Sans isolation galvanique AC/DC" />
                    </div>
                    <p class="col-span-12 font-semibold"><span class="text-sky-500">(6a)</span> Tension DC batterie :</p>
                    <UFormField label="Udc (Vdc)" class="col-span-12 md:col-span-6 flex items-center gap-4">
                        <UInput v-model="state.battery_udc_voltage" type="number" class="w-full" />
                    </UFormField>
                    <p class="col-span-12 font-semibold"><span class="text-sky-500">(6b)</span> Batterie famille Lithium* :
                    </p>
                    <UFormField label="Nb sous-ensembles" class="col-span-6 md:col-span-3">
                        <UInput v-model="state.battery_lithium_subset_count" type="number" class="w-full" />
                    </UFormField>
                    <UFormField label="Énergie unitaire (kWh)" class="col-span-6 md:col-span-3">
                        <UInput v-model="state.battery_lithium_unit_energy_kwh" type="number" class="w-full" />
                    </UFormField>
                    <div class="col-span-12 md:col-span-6 flex items-center gap-4">
                        <UCheckbox v-model="state.battery_lithium_room" label="Local batterie" />
                        <UCheckbox v-model="state.battery_lithium_outside_room" label="Hors local batterie" />
                    </div>
                    <div v-if="state.battery_lithium_outside_room"
                        class="col-span-12 md:col-span-6 flex items-center gap-4 pl-2">
                        <UCheckbox v-model="state.battery_lithium_outside_energy_le_15kwh" label="≤ 15kWh" />
                        <UCheckbox v-model="state.battery_lithium_outside_energy_gt_15kwh" label="> 15kWh" />
                    </div>
                    <p class="col-span-12 font-semibold"><span class="text-sky-500">(6c)</span> Autre type de batterie :</p>
                    <UFormField label="Description" class="col-span-12 md:col-span-6 flex items-center gap-4">
                        <UInput v-model="state.battery_other_description" class="w-full" />
                    </UFormField>
                    <UCheckbox v-model="state.battery_other_norm_installation_compliance" class="col-span-12"
                        label="Conforme norme sécurité & mise en oeuvre (NF C 15-100-1 part 5-57)" />
                </div>
            </template>
            <template #part_5>
                <div class="grid grid-cols-12 gap-3 px-5 pb-4">
                    <p class="col-span-12 font-semibold"><span class="text-sky-500">(7a)</span> Réalimentation mode autonome
                        :</p>
                    <p class="col-span-12 font-semibold"><span class="text-sky-500">(7b)</span> Schéma des Liaisons à la
                        Terre (mode autonome) :</p>
                    <div class="col-span-12 md:col-span-6 flex items-center gap-4">
                        <UCheckbox v-model="state.autonomous_mode_slt_tns" label="TN-S" />
                        <UCheckbox v-model="state.autonomous_mode_slt_tt" label="TT (si non raccordé réseau)" />
                    </div>
                </div>
            </template>
            <template #part_6>
                <div class="grid grid-cols-12 gap-3 px-5 pb-4">
                    <p class="col-span-12 font-semibold"><span class="text-sky-500">(8)</span> Autres sources AC :</p>
                    <UFormField label="Interrupteur-sectionneur U (Vac)"
                        class="col-span-12 md:col-span-6 flex items-center gap-4">
                        <UInput v-model="state.other_ac_source_switch_voltage_vac" type="number" class="w-full" />
                    </UFormField>
                    <UFormField label="Interrupteur-sectionneur In (A)"
                        class="col-span-12 md:col-span-6 flex items-center gap-4">
                        <UInput v-model="state.other_ac_source_switch_current_in" type="number" class="w-full" />
                    </UFormField>
                </div>
            </template>
            <template #signature_stamp>
                <div class="grid grid-cols-12 gap-3 px-5 pb-4">
                    <UFormField label="Téléphone de l'interlocuteur technique" class="col-span-12">
                        <UInput v-model="state.technical_contact_phone" class="w-full" />
                    </UFormField>
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
