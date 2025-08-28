<script setup lang="ts">
import InstallationRepresentationMandatePreview from '~/components/installation/representationMandate/Preview.vue'

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
	title: 'Mandat de représentation',
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
	const rm = form.value?.representation_mandate
	const mapCiv: Record<string, string> = { mme: 'Madame', mr: 'Monsieur' }
		return {
			client_civility: (rm?.client_civility ? (mapCiv[rm.client_civility] || '') : '') as '' | 'Madame' | 'Monsieur',
		client_birth_date: rm?.client_birth_date || '',
		client_birth_place: rm?.client_birth_place || '',
		client_address: rm?.client_address || (form.value?.client_address || ''),
		company_name: rm?.company_name || '',
		company_rcs_city: rm?.company_rcs_city || '',
		company_siret: rm?.company_siret || '',
		company_head_office_address: rm?.company_head_office_address || '',
		represented_by: rm?.represented_by || '',
		representative_role: rm?.representative_role || '',
		client_signature: { signer_name: rm?.client_signature?.signer_name || '' },
		installer_signature: { signer_name: rm?.installer_signature?.signer_name || '' },
		client_signature_image_url: rm?.client_signature?.signature_image || null,
		client_signature_signed_at: rm?.client_signature?.signed_at || null,
		installer_signature_image_url: rm?.installer_signature?.signature_image || null,
		installer_signature_signed_at: rm?.installer_signature?.signed_at || null,
		generated_at: rm?.updated_at || rm?.created_at || new Date().toISOString(),
	}
})
</script>

<template>
	<div class="min-h-screen">
		<div v-if="pending" class="text-center text-gray-500">Chargement…</div>
		<div v-else-if="error" class="text-center text-red-600">{{ error }}</div>
		<InstallationRepresentationMandatePreview
			v-else-if="form?.representation_mandate"
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