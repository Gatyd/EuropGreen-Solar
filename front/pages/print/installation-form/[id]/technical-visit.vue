<script setup lang="ts">
import InstallationTechnicalVisitPreview from '~/components/installation/technicalVisit/Preview.vue'

definePageMeta({
	layout: false,
	middleware: []
})

const route = useRoute()
const id = route.params.id as string

const form = ref<any | null>(null)
const pending = ref(true)
const error = ref<string | null>(null)

useSeoMeta({
	title: 'Visite technique',
})

onMounted(async () => {
	try {
		const f = await $fetch(`/api/installations/forms/${id}/`)
		form.value = f
	} catch (e: any) {
		error.value = e?.message || 'Erreur lors du chargement de la fiche technique'
	} finally {
		pending.value = false
	}
})

const draft = computed(() => {
	const tv = form.value?.technical_visit
	const mapRoofType: Record<string, string> = { tile: 'Tuile', scale_tile: 'Tuile écaille', slate: 'Ardoise', steel: 'Bac acier', fibrocement: 'Fibrociment', flat_terrace: 'Toit terrasse' }
	const mapRoofShape: Record<string, string> = { one_slope: '1 pan', multi_slope: 'Multipan', flat: 'Toit plat terrasse' }
	const mapRoofAccess: Record<string, string> = { R: 'R', R1: 'R1', R2: 'R2', other: 'Autre' }
	const mapMeterType: Record<string, string> = { linky: 'Linky', other: 'Autre' }
	const mapCurrentType: Record<string, string> = { mono: 'Monophasé', tri: 'Triphasé' }
	const mapMeterPos: Record<string, string> = { indoor: 'Intérieur', outdoor: 'Extérieur', unknown: 'Inconnu' }
	// Construit un draft minimal compatible avec Preview; les mappings UI sont faits côté Modal si besoin
	return {
		visit_date: tv?.visit_date || '',
		expected_installation_date: tv?.expected_installation_date || '',
		roof_cover: tv?.roof_type ? (mapRoofType[tv.roof_type] || tv.roof_type) : '',
		spare_tiles: !!tv?.tiles_spare_provided,
		roof_shape: tv?.roof_shape ? (mapRoofShape[tv.roof_shape] || tv.roof_shape) : '',
		roof_access: tv?.roof_access ? (mapRoofAccess[tv.roof_access] || tv.roof_access) : '',
		roof_access_other: tv?.roof_access_other || '',
		nacelle_needed: tv?.nacelle_needed || 'unknown',
		truck_access: tv?.truck_access || 'unknown',
		truck_access_note: tv?.truck_access_comment || '',
		meter_type: tv?.meter_type ? (mapMeterType[tv.meter_type] || tv.meter_type) : '',
		meter_type_other: tv?.meter_type_other || '',
		current_type: tv?.current_type ? (mapCurrentType[tv.current_type] || tv.current_type) : '',
		reuse_existing_connection: !!tv?.existing_grid_connection,
		meter_position: tv?.meter_position ? (mapMeterPos[tv.meter_position] || tv.meter_position) : '',
		panel_to_board_distance_m: tv?.panels_to_board_distance_m ?? null,
		meter_location_photo: null,
		meter_location_photo_url: tv?.meter_location_photo || null,
		extra_required: !!tv?.additional_equipment_needed,
		extra_materials: tv?.additional_equipment_details || '',
		client_signature: { signer_name: tv?.client_signature?.signer_name || '' },
		installer_signature: { signer_name: tv?.installer_signature?.signer_name || '' },
		client_signature_image_url: tv?.client_signature?.signature_image || (typeof tv?.client_signature?.signature_data === 'string' && tv?.client_signature?.signature_data.startsWith('data:image/') ? tv?.client_signature?.signature_data : null),
		client_signature_signed_at: tv?.client_signature?.signed_at || null,
		installer_signature_image_url: tv?.installer_signature?.signature_image || (typeof tv?.installer_signature?.signature_data === 'string' && tv?.installer_signature?.signature_data.startsWith('data:image/') ? tv?.installer_signature?.signature_data : null),
		installer_signature_signed_at: tv?.installer_signature?.signed_at || null,
		generated_at: tv?.updated_at || tv?.created_at || new Date().toISOString(),
	}
})
</script>

<template>
	<div class="min-h-screen">
		<div v-if="pending" class="text-center text-gray-500">Chargement…</div>
		<div v-else-if="error" class="text-center text-red-600">{{ error }}</div>
		<InstallationTechnicalVisitPreview v-else-if="form?.technical_visit" :draft="draft" class="mx-auto" />
	</div>
</template>

<style>
@media print {
	body { background: white; }
}
</style>
