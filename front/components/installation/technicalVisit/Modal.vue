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
    extra_required: false,
    extra_materials: '',
    client_signature: { signer_name: '', method: 'draw' as 'draw' | 'upload', dataUrl: '', file: null as File | null },
    installer_signature: { signer_name: '', method: 'draw' as 'draw' | 'upload', dataUrl: '', file: null as File | null },
})

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
