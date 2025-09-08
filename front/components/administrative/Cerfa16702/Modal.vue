<script setup lang="ts">
import type { DeclarantType, InstallationForm } from '~/types/installations'

const model = defineModel({ type: Boolean })

const props = defineProps<{
    form?: InstallationForm | null
    cerfa16702?: InstallationForm['cerfa16702'] | null
    formId?: string
}>()

const emit = defineEmits<{ (e: 'submit'): void }>()

// État partagé du brouillon du mandat
const draft = reactive({
    // Identité du déclarant
    declarant_type: 'individual' as DeclarantType,
    last_name: '',
    first_name: '',
    birth_date: '',
    birth_place: '',
    birth_department: '',
    birth_country: '',
    company_denomination: '',
    company_reason: '',
    company_siret: '',
    company_type: '',

    // Coordonnées du déclarant
    address_street: '',
    address_number: '',
    address_lieu_dit: '',
    address_locality: '',
    address_postal_code: '',
    address_bp: '',
    address_cedex: '',
    phone_country_code: '',
    phone: '',
    email: '',
    email_consent: false,

    // Terrain
    land_street: '',
    land_number: '',
    land_lieu_dit: '',
    land_locality: '',
    land_postal_code: '',

    cadastral_prefix: '',
    cadastral_section: '',
    cadastral_number: '',
    cadastral_surface_m2: null,
    cadastral_prefix_p2: '',
    cadastral_section_p2: '',
    cadastral_number_p2: '',
    cadastral_surface_m2_p2: null,
    cadastral_prefix_p3: '',
    cadastral_section_p3: '',
    cadastral_number_p3: '',
    cadastral_surface_m2_p3: null,

    // Projet
    project_new_construction: false,
    project_existing_works: false,
    project_description: '',
    destination_primary_residence: false,
    destination_secondary_residence: false,
    agrivoltaic_project: false,
    electrical_power_text: '',
    peak_power_text: '',
    energy_destination: '',

    // Périmètres de protection
    protection_site_patrimonial: false,
    protection_site_classe_or_instance: false,
    protection_monument_abords: false,

    // Engagement du déclarant
    engagement_city: '',
    engagement_date: '',
    declarant_signature: { signer_name: '', method: 'draw' as 'draw' | 'upload', dataUrl: '', file: null as File | null },
    declarant_signature_image_url: null as string | null,
    declarant_signature_signed_at: null as string | null,
})

// Hydrate le brouillon depuis le CERFA 16702 existant + la fiche
watch(
    () => props.cerfa16702,
    (cf: any) => {
        if (!cf) return
        // Les valeurs backend sont probablement 'mme' | 'mr'
        draft.declarant_type = cf.declarant_type || ''
        draft.last_name = cf.last_name || ''
        draft.first_name = cf.first_name || ''
        draft.birth_date = cf.birth_date || ''
        draft.birth_place = cf.birth_place || ''
        draft.birth_department = cf.birth_department || ''
        draft.birth_country = cf.birth_country || ''
        draft.company_denomination = cf.company_denomination || ''
        draft.company_reason = cf.company_reason || ''
        draft.company_siret = cf.company_siret || ''
        draft.company_type = cf.company_type || ''

        draft.address_street = cf.address_street || ''
        draft.address_number = cf.address_number || ''
        draft.address_lieu_dit = cf.address_lieu_dit || ''
        draft.address_locality = cf.address_locality || ''
        draft.address_postal_code = cf.address_postal_code || ''
        draft.address_bp = cf.address_bp || ''
        draft.address_cedex = cf.address_cedex || ''
        draft.phone_country_code = cf.phone_country_code || ''
        draft.phone = cf.phone || ''
        draft.email = cf.email || ''
        draft.email_consent = cf.email_consent || false

        draft.land_street = cf.land_street || ''
        draft.land_number = cf.land_number || ''
        draft.land_lieu_dit = cf.land_lieu_dit || ''
        draft.land_locality = cf.land_locality || ''
        draft.land_postal_code = cf.land_postal_code || ''

        draft.cadastral_prefix = cf.cadastral_prefix || ''
        draft.cadastral_section = cf.cadastral_section || ''
        draft.cadastral_number = cf.cadastral_number || ''
        draft.cadastral_surface_m2 = cf.cadastral_surface_m2 || null
        draft.cadastral_prefix_p2 = cf.cadastral_prefix_p2 || ''
        draft.cadastral_section_p2 = cf.cadastral_section_p2 || ''
        draft.cadastral_number_p2 = cf.cadastral_number_p2 || ''
        draft.cadastral_surface_m2_p2 = cf.cadastral_surface_m2_p2 || null
        draft.cadastral_prefix_p3 = cf.cadastral_prefix_p3 || ''
        draft.cadastral_section_p3 = cf.cadastral_section_p3 || ''
        draft.cadastral_number_p3 = cf.cadastral_number_p3 || ''
        draft.cadastral_surface_m2_p3 = cf.cadastral_surface_m2_p3 || null

        draft.project_new_construction = cf.project_new_construction || false
        draft.project_existing_works = cf.project_existing_works || false
        draft.project_description = cf.project_description || ''
        draft.destination_primary_residence = cf.destination_primary_residence || false
        draft.destination_secondary_residence = cf.destination_secondary_residence || false
        draft.agrivoltaic_project = cf.agrivoltaic_project || false
        draft.electrical_power_text = cf.electrical_power_text || ''
        draft.peak_power_text = cf.peak_power_text || ''
        draft.energy_destination = cf.energy_destination || ''

        draft.protection_site_patrimonial = cf.protection_site_patrimonial || false
        draft.protection_site_classe_or_instance = cf.protection_site_classe_or_instance || false
        draft.protection_monument_abords = cf.protection_monument_abords || false

        draft.engagement_city = cf.engagement_city || ''
        draft.engagement_date = cf.engagement_date || ''
        const ds = cf.declarant_signature
        if (ds) {
            draft.declarant_signature.signer_name = ds.signer_name || ''
            draft.declarant_signature_image_url = ds.signature_image || (typeof ds.signature_data === 'string' && ds.signature_data.startsWith('data:image/') ? ds.signature_data : null)
            draft.declarant_signature_signed_at = ds.signed_at || null
        }
    },
    { immediate: true }
)

const onSubmit = () => {
    emit('submit')
    model.value = false
}
</script>

<template>
    <UModal v-model:open="model" title="CERFA 16702" fullscreen>
        <template #body>
            <div class="flex flex-col xl:flex-row gap-4">
                <AdministrativeCerfa16702Form class="xl:basis-1/2" :draft="draft" :form="props.form"
                    :cerfa16702="props.cerfa16702" :form-id="props.formId" @submit="onSubmit" />
                <AdministrativeCerfa16702Preview class="xl:basis-1/2 sticky top-0 shadow-md rounded-lg" mode="edit" :draft="draft" :form="form" />
            </div>
        </template>
    </UModal>
</template>
