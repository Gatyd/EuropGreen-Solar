<script setup lang="ts">
import AdministrativeCerfa16702Preview from '~/components/administrative/Cerfa16702/Preview.vue'

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
	title: 'CERFA 16702 - Déclaration préalable',
})

onMounted(async () => {
	try {
		const f = await $fetch(`/api/installations/forms/${id}/`)
		form.value = f
	} catch (e: any) {
		error.value = e?.message || 'Erreur lors du chargement de la fiche installation'
	} finally {
		pending.value = false
	}
})

const draft = computed(() => {
	const cf = form.value?.cerfa16702
	if (!cf) return null

	return {
		declarant_type: cf.declarant_type || '',
		last_name: cf.last_name || '',
		first_name: cf.first_name || '',
		birth_date: cf.birth_date || '',
		birth_place: cf.birth_place || '',
		birth_department: cf.birth_department || '',
		birth_country: cf.birth_country || '',
		company_denomination: cf.company_denomination || '',
		company_reason: cf.company_reason || '',
		company_siret: cf.company_siret || '',
		company_type: cf.company_type || '',
		address_street: cf.address_street || '',
		address_number: cf.address_number || '',
		address_lieu_dit: cf.address_lieu_dit || '',
		address_locality: cf.address_locality || '',
		address_postal_code: cf.address_postal_code || '',
		address_bp: cf.address_bp || '',
		address_cedex: cf.address_cedex || '',
		phone_country_code: cf.phone_country_code || '',
		phone: cf.phone || '',
		email: cf.email || '',
		email_consent: cf.email_consent || false,
		land_street: cf.land_street || '',
		land_number: cf.land_number || '',
		land_lieu_dit: cf.land_lieu_dit || '',
		land_locality: cf.land_locality || '',
		land_postal_code: cf.land_postal_code || '',
		cadastral_prefix: cf.cadastral_prefix || '',
		cadastral_section: cf.cadastral_section || '',
		cadastral_number: cf.cadastral_number || '',
		cadastral_surface_m2: cf.cadastral_surface_m2 || null,
		project_new_construction: cf.project_new_construction || false,
		project_existing_works: cf.project_existing_works || false,
		project_description: cf.project_description || '',
		destination_primary_residence: cf.destination_primary_residence || false,
		destination_secondary_residence: cf.destination_secondary_residence || false,
		agrivoltaic_project: cf.agrivoltaic_project || false,
		electrical_power_text: cf.electrical_power_text || '',
		peak_power_text: cf.peak_power_text || '',
		energy_destination: cf.energy_destination || '',
		protection_site_patrimonial: cf.protection_site_patrimonial || false,
		protection_site_classe_or_instance: cf.protection_site_classe_or_instance || false,
		protection_monument_abords: cf.protection_monument_abords || false,
		engagement_city: cf.engagement_city || '',
		engagement_date: cf.engagement_date || '',
		declarant_signature: { signer_name: cf.declarant_signature?.signer_name || '' },
		declarant_signature_image_url: cf.declarant_signature?.signature_image || null,
		declarant_signature_signed_at: cf.declarant_signature?.signed_at || null,
		dpc1: null,
        dpc1_url: cf.dpc1 || null,
        dpc2: null,
        dpc2_url: cf.dpc2 || null,
        dpc3: null,
        dpc3_url: cf.dpc3 || null,
        dpc4: null,
        dpc4_url: cf.dpc4 || null,
        dpc5: null,
        dpc5_url: cf.dpc5 || null,
        dpc6: null,
        dpc6_url: cf.dpc6 || null,
        dpc7: null,
        dpc7_url: cf.dpc7 || null,
        dpc8: null,
        dpc8_url: cf.dpc8 || null,
        dpc11: null,
        dpc11_url: cf.dpc11 || null,
		dpc11_notice_materiaux: cf.dpc11_notice_materiaux || '',
		generated_at: cf.updated_at || cf.created_at || new Date().toISOString(),
	}
})
</script>

<template>
	<div class="min-h-screen">
		<div v-if="pending" class="text-center text-gray-500">Chargement…</div>
		<div v-else-if="error" class="text-center text-red-600">{{ error }}</div>
		<AdministrativeCerfa16702Preview
			v-else-if="form?.cerfa16702 && draft"
			:draft="draft"
			:form="form"
			class="mx-auto"
		/>
	</div>
</template>

<style>
@page {
	size: A4;
	margin: 0;
}
html, body { margin: 0; padding: 0; }
@media print {
	body { background: white; }
}
</style>
