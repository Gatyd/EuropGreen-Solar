<script setup lang="ts">

const props = defineProps<{
    draft: sc144aDraft
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
    connection_power_monitored: boolean,
    installer_name: string,
    installer_signature: string,
    signature_date: string,
    installer_stamp: string
}

const state = toRef(props, 'draft')

const formSections = [
    {
        value: 'installer_info',
        label: 'Informations de l\'installateur',
        slot: 'installer_info'
    },
    // {
    //     value: 'client_info',
    //     label: 'Informations du client',
    //     slot: 'client_info'
    // },
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
        value: 'part1',
        label: 'Module PV',
        slot: 'part1'
    },
    {
        value: 'part2',
        label: 'Câble principal PV',
        slot: 'part2'
    },
    {
        value: 'part3',
        label: 'Interrupteur-Sectionneur général DC',
        slot: 'part3'
    },
    {
        value: 'part4',
        label: 'Polarité à la terre',
        slot: 'part4'
    },
    {
        value: 'part5',
        label: 'Onduleur',
        slot: 'part5'
    },
    {
        value: 'part6',
        label: 'Branchement*',
        slot: 'part6'
    },
    {
        value: 'part7',
        label: 'Signature et Cachet',
        slot: 'part7'
    },
]

</script>

<template>
    <UForm :state="draft" class="space-y-3">
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
                    <UFormField label="Nom" class="col-span-12">
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
            </template>
            <template #part1>
            </template>
            <template #part2>
            </template>
            <template #part3>
            </template>
            <template #part4>
            </template>
            <template #part5>
            </template>
            <template #part6>
            </template>
            <template #part7>
            </template>
        </UPageAccordion>
    </UForm>
</template>
