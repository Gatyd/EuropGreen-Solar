<script setup lang="ts">
import type { InstallationForm } from '~/types/installations'

const model = defineModel({ type: Boolean })

const props = defineProps<{
    form?: InstallationForm | null
    formId?: string
}>()

const emit = defineEmits<{ (e: 'submit'): void }>()

// Brouillon minimal; le contenu précis sera géré par les sous-formulaires
const draft = reactive<any>({
    model: 'SC-144A',
    y_offset_mm: 8,
    client_name: "",
    site_address_line1: "",
    site_address_line2: "",
    client_postal_code: "",
    client_city: "",
    client_phone: "",
    connect_grid_by_consumption_install: false,
    connect_grid_at_delivery_point: false,
    other_dc_sources_no: false,
    other_dc_sources_yes: false,
    other_dc_sources_details: "",
    other_ac_sources_no: false,
    other_ac_sources_yes: false,
    other_ac_sources_details: "",
    modified_installation_no: false,
    modified_installation_yes: false,
    reference_date: "",
    permit_application: false,
    preliminary_declaration: false,
    contract_signature: false,
    order_acknowledgement: false,
    installer_company_name: "",
    installer_email: "",
    installer_address: "",
    installer_postal_code: "",
    installer_city: "",
    installer_phone: "",
    installer_fax: "",
    existing_install_energization_date: "",
    initial_pv_power: "",
    dc_overcurrent_protection_yes: false,
    dc_overcurrent_protection_no: false,
    modified_dc_only: false,
    modified_ac_only: false,
    modified_dc_ac: false,
    pv_power_without_existing: "",
    inverter_added_no: false,
    inverter_added_yes: false,
    inverter_added_count: "",
    inverter_replaced_no: false,
    inverter_replaced_yes: false,
    inverter_replaced_count: "",
    inverter_kept_no: false,
    inverter_kept_yes: false,
    inverter_kept_count: "",
    pv_module_string_count: "",
    pv_iscmax: "",
    pv_uocmax: "",
    pv_main_cable_section: "",
    pv_main_cable_voltage: "",
    pv_main_cable_temp_rating: "",
    dc_isolator_un: "",
    dc_isolator_in: "",
    dc_isolator_not_applicable: false,
    dc_polarity_to_earth_no: false,
    dc_polarity_to_earth_yes: false,
    inverter_identical_generator_count: "",
    inverter_brand_model: "",
    inverter_ext_decoupling: false,
    inverter_int_decoupling: false,
    connection_power_limited: false,
    connection_power_monitored: false,
    // installer_name: "",
    // installer_signature: "",
    // signature_date: "",
    // installer_stamp: ""
})

const onSubmit = () => {
    emit('submit')
    model.value = false
}
</script>

<template>
    <UModal v-model:open="model" title="Consuel" fullscreen>
        <template #body>
            <div class="flex flex-col xl:flex-row gap-4 h-full overflow-hidden">
                <!-- Colonne formulaire -->
                <div class="xl:basis-1/2 min-h-0 overflow-auto">
                    <AdministrativeConsuelForm class="w-full" :draft="draft" :form="props.form" :form-id="props.formId"
                        @submit="onSubmit" />
                </div>

                <!-- Colonne aperçu -->
                <div class="xl:basis-1/2 min-h-0 overflow-auto">
                    <AdministrativeConsuelPreview mode="edit" :draft="draft" />
                </div>
            </div>
        </template>
    </UModal>

</template>
