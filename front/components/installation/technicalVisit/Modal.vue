<script setup lang="ts">
const model = defineModel({ type: Boolean })

const props = defineProps<{
    // On peut recevoir éventuellement des valeurs initiales plus tard
    initial?: Partial<{
        visit_date: string
        expected_installation_date: string
    }>
    formId?: string
    action?: 'full' | 'signature' | 'preview'
    // Visite technique existante pour pré-remplir le brouillon
    technicalVisit?: any
}>()
const emit = defineEmits<{
    (e: 'submit'): void
}>()

// État partagé du brouillon de visite technique
const draft = reactive({
    visit_date: (props.initial?.visit_date ?? new Date().toISOString().slice(0, 10)) as string,
    expected_installation_date: (props.initial?.expected_installation_date ?? '') as string,
    roof_cover: '' as '' | 'Tuile' | 'Tuile écaille' | 'Ardoise' | 'Bac acier' | 'Fibrociment' | 'Toit terrasse',
    spare_tiles: false,
    roof_shape: '' as '' | '1 pan' | 'Multipan' | 'Toit plat terrasse',
    roof_access: '' as '' | 'R' | 'R1' | 'R2' | 'Autre',
    roof_access_other: '',
    nacelle_needed: 'unknown' as 'yes' | 'no' | 'unknown',
    truck_access: 'unknown' as 'yes' | 'no' | 'unknown',
    truck_access_note: '',
    meter_type: '' as '' | 'Linky' | 'Autre',
    meter_type_other: '',
    current_type: '' as '' | 'Monophasé' | 'Triphasé',
    reuse_existing_connection: false,
    meter_position: '' as '' | 'Intérieur' | 'Extérieur' | 'Inconnu',
    panel_to_board_distance_m: null as number | null,
    meter_location_photo: null as File | null,
    // URL pour l'aperçu si la photo existe côté serveur
    meter_location_photo_url: null as string | null,
    extra_required: false,
    extra_materials: '',
    client_signature: { signer_name: '', method: 'draw' as 'draw' | 'upload', dataUrl: '', file: null as File | null },
    installer_signature: { signer_name: '', method: 'draw' as 'draw' | 'upload', dataUrl: '', file: null as File | null },
    // Métadonnées pour l'aperçu
    generated_at: new Date().toISOString(),
    client_signature_image_url: null as string | null,
    client_signature_signed_at: null as string | null,
    installer_signature_image_url: null as string | null,
    installer_signature_signed_at: null as string | null,
})

// Mapping codes API -> libellés UI
const mapRoofType: Record<string, typeof draft.roof_cover> = {
    tile: 'Tuile',
    scale_tile: 'Tuile écaille',
    slate: 'Ardoise',
    steel: 'Bac acier',
    fibrocement: 'Fibrociment',
    flat_terrace: 'Toit terrasse',
}
const mapRoofShape: Record<string, typeof draft.roof_shape> = {
    one_slope: '1 pan',
    multi_slope: 'Multipan',
    flat: 'Toit plat terrasse',
}
const mapRoofAccess: Record<string, typeof draft.roof_access> = {
    R: 'R', R1: 'R1', R2: 'R2', other: 'Autre',
}
const mapMeterType: Record<string, typeof draft.meter_type> = { linky: 'Linky', other: 'Autre' }
const mapCurrentType: Record<string, typeof draft.current_type> = { mono: 'Monophasé', tri: 'Triphasé' }
const mapMeterPos: Record<string, typeof draft.meter_position> = { indoor: 'Intérieur', outdoor: 'Extérieur', unknown: 'Inconnu' }

// Hydrate le brouillon si une visite technique est fournie
watch(
    () => props.technicalVisit,
    (tv: any) => {
        if (!tv) return
        // Dates
        draft.visit_date = tv.visit_date || draft.visit_date
        draft.expected_installation_date = tv.expected_installation_date || draft.expected_installation_date
        // Types & choix
        if (tv.roof_type && mapRoofType[tv.roof_type]) draft.roof_cover = mapRoofType[tv.roof_type]
        if (typeof tv.tiles_spare_provided === 'boolean') draft.spare_tiles = !!tv.tiles_spare_provided
        if (tv.roof_shape && mapRoofShape[tv.roof_shape]) draft.roof_shape = mapRoofShape[tv.roof_shape]
        if (tv.roof_access && mapRoofAccess[tv.roof_access]) draft.roof_access = mapRoofAccess[tv.roof_access]
        draft.roof_access_other = tv.roof_access_other || ''
        if (tv.nacelle_needed) draft.nacelle_needed = tv.nacelle_needed
        if (tv.truck_access) draft.truck_access = tv.truck_access
        draft.truck_access_note = tv.truck_access_comment || ''
        if (tv.meter_type && mapMeterType[tv.meter_type]) draft.meter_type = mapMeterType[tv.meter_type]
        draft.meter_type_other = tv.meter_type_other || ''
        if (tv.current_type && mapCurrentType[tv.current_type]) draft.current_type = mapCurrentType[tv.current_type]
        if (typeof tv.existing_grid_connection === 'boolean') draft.reuse_existing_connection = !!tv.existing_grid_connection
        if (tv.meter_position && mapMeterPos[tv.meter_position]) draft.meter_position = mapMeterPos[tv.meter_position]
        if (typeof tv.panels_to_board_distance_m !== 'undefined' && tv.panels_to_board_distance_m !== null) {
            draft.panel_to_board_distance_m = Number(tv.panels_to_board_distance_m)
        }
        draft.meter_location_photo_url = tv.meter_location_photo || null
        if (typeof tv.additional_equipment_needed === 'boolean') draft.extra_required = !!tv.additional_equipment_needed
        draft.extra_materials = tv.additional_equipment_details || ''

        // Métadonnées
        draft.generated_at = tv.updated_at || tv.created_at || new Date().toISOString()

        // Signatures (client)
        const cs = tv.client_signature
        if (cs) {
            draft.client_signature.signer_name = cs.signer_name || ''
            draft.client_signature_image_url = cs.signature_image || (typeof cs.signature_data === 'string' && cs.signature_data.startsWith('data:image/') ? cs.signature_data : null)
            draft.client_signature_signed_at = cs.signed_at || null
        }
        // Signatures (installateur)
        const is = tv.installer_signature
        if (is) {
            draft.installer_signature.signer_name = is.signer_name || ''
            draft.installer_signature_image_url = is.signature_image || (typeof is.signature_data === 'string' && is.signature_data.startsWith('data:image/') ? is.signature_data : null)
            draft.installer_signature_signed_at = is.signed_at || null
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
    <UModal v-model:open="model"
        :title="action === 'signature' ? 'Signature – Visite technique' : action === 'full' ? 'Visite technique' : 'Aperçu - Rapport Visite technique'"
        :fullscreen="action !== 'preview'" :ui="{ content: action !== 'preview' ? 'max-w-screen' : 'max-w-5xl' }">
        <template #body>
            <div :class="action !== 'preview' ? 'flex flex-col xl:flex-row gap-4' : ''">
                <InstallationTechnicalVisitForm v-if="action !== 'preview'" class="xl:basis-1/2" :draft="draft"
                    :form-id="props.formId" @submit="onSubmit" :action="props.action ?? 'full'" />
                <InstallationTechnicalVisitPreview :class="action !== 'preview' ? 'xl:basis-1/2 shadow-md rounded-lg' : ''" :draft="draft" />
            </div>
        </template>
    </UModal>
</template>
