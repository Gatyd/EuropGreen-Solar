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
    template: '144a',
    // y_offset_mm: 8,
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
    connection_power_limited_details: "",
    connection_power_monitored: false,
    installer_name: "",
    installer_signature: null,
    signature_date: "",
    installer_stamp: null,
    // Tableau caractéristique groupes / chaînes (SC-144B)
    a_number_of_strings_1: "", a_number_of_strings_2: "", a_number_of_strings_3: "", a_number_of_strings_4: "", a_number_of_strings_5: "",
    b_iscmax_module_1: "", b_iscmax_module_2: "", b_iscmax_module_3: "", b_iscmax_module_4: "", b_iscmax_module_5: "",
    c_irm_modules_1: "", c_irm_modules_2: "", c_irm_modules_3: "", c_irm_modules_4: "", c_irm_modules_5: "",
    d_courant_admissible_cable_chaine_1: "", d_courant_admissible_cable_chaine_2: "", d_courant_admissible_cable_chaine_3: "", d_courant_admissible_cable_chaine_4: "", d_courant_admissible_cable_chaine_5: "",
    e_type_courant_protection_chaine_1: "", e_type_courant_protection_chaine_2: "", e_type_courant_protection_chaine_3: "", e_type_courant_protection_chaine_4: "", e_type_courant_protection_chaine_5: "",
    f_courant_admissible_cable_groupe_1: "", f_courant_admissible_cable_groupe_2: "", f_courant_admissible_cable_groupe_3: "", f_courant_admissible_cable_groupe_4: "", f_courant_admissible_cable_groupe_5: "",
    g_iscmax_groupe_1: "", g_iscmax_groupe_2: "", g_iscmax_groupe_3: "", g_iscmax_groupe_4: "", g_iscmax_groupe_5: "",
    h_type_courant_protection_groupe_1: "", h_type_courant_protection_groupe_2: "", h_type_courant_protection_groupe_3: "", h_type_courant_protection_groupe_4: "", h_type_courant_protection_groupe_5: ""
})

// Pré-remplissage des informations depuis form et documents existants
watch(() => props.form, (f) => {
    if (!f) return

    const client = f.client
    const mandate = f.representation_mandate
    const cerfa = f.cerfa16702

    // === INFORMATIONS CLIENT ===
    // Nom du client - priorité: client > offer
    if (!draft.client_name) {
        if (client) {
            draft.client_name = `${client.first_name} ${client.last_name}`.trim()
        } else if (f.offer) {
            draft.client_name = `${f.offer.first_name} ${f.offer.last_name}`.trim()
        }
    }

    // Téléphone client - priorité: client > offer
    if (!draft.client_phone) {
        if (client && client.phone_number) {
            draft.client_phone = client.phone_number
        } else if (f.offer && f.offer.phone) {
            draft.client_phone = f.offer.phone
        }
    }

    // Adresse du site - priorité: mandate > cerfa > form.client_address > offer
    if (!draft.site_address) {
        if (mandate && mandate.client_address) {
            draft.site_address = mandate.client_address
        } else if (f.client_address) {
            draft.site_address = f.client_address
        } else if (f.offer && f.offer.address) {
            draft.site_address = f.offer.address
        }
        if (cerfa) {
            if (!draft.site_address) draft.site_address = cerfa.address_street || ''
            if (!draft.client_postal_code) draft.client_postal_code = cerfa.land_postal_code || ''
            if (!draft.client_city) draft.client_city = cerfa.land_locality || ''
        }
    }

    // === INFORMATIONS INSTALLATEUR ===
    // Priorité: mandate > cerfa
    if (mandate) {
        if (!draft.installer_company_name) draft.installer_company_name = mandate.represented_by || ''
        if (!draft.installer_address) draft.installer_address = mandate.company_head_office_address || ''
        if (!draft.installer_name) draft.installer_name = mandate.represented_by || ''
        // Note: Le mandat n'a pas d'email ni de téléphone installateur
    }
    if (cerfa) {
        if (cerfa.declarant_type === 'company' && !draft.installer_company_name) draft.installer_company_name = cerfa.company_denomination || ''
        if (!draft.installer_address) draft.installer_address = cerfa.address_street || ''
        if (!draft.installer_email) draft.installer_email = cerfa.email || ''
        if (!draft.installer_phone) draft.installer_phone = cerfa.phone || ''
        if (!draft.installer_postal_code) draft.installer_postal_code = cerfa.address_postal_code || ''
        if (!draft.installer_city) draft.installer_city = cerfa.address_locality || ''
    }
}, { immediate: true })

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
