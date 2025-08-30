<script setup lang="ts">
import InstallationRepresentationMandatePreview from '~/components/installation/representationMandate/Preview.vue'
import type { Civility, ConnectionNature } from '~/types/installations'

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
    title: 'Mandat ENEDIS',
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
    const em = form.value?.enedis_mandate
    return {
        client_type: em.client_type || '',
        client_civility: em.client_civility || '' as Civility,
        client_address: em.client_address || '',
        client_company_name: em.client_company_name || '',
        client_company_siret: em.client_company_siret || '',
        client_company_represented_by: em.client_company_represented_by || '',

        contractor_company_name: em.contractor_company_name || '',
        contractor_company_siret: em.contractor_company_siret || '',
        contractor_represented_by_name: em.contractor_represented_by_name || '',
        contractor_represented_by_role: em.contractor_represented_by_role || '',

        mandate_type: em.mandate_type || 'simple',
        authorize_signature: em.authorize_signature || false,
        authorize_payment: em.authorize_payment || false,
        authorize_l342: em.authorize_l342 || false,
        authorize_network_access: em.authorize_network_access || false,

        geographic_area: em.geographic_area || '',
        connection_nature: em.connection_nature || '' as ConnectionNature,
        client_signature: { signer_name: em?.client_signature?.signer_name || '' },
        installer_signature: { signer_name: em?.installer_signature?.signer_name || '' },
        client_signature_image_url: em?.client_signature?.signature_image || null,
        client_signature_signed_at: em?.client_signature?.signed_at || null,
        installer_signature_image_url: em?.installer_signature?.signature_image || null,
        installer_signature_signed_at: em?.installer_signature?.signed_at || null,
        generated_at: em?.updated_at || em?.created_at || new Date().toISOString(),
    }
})
</script>

<template>
    <div class="min-h-screen">
        <div v-if="pending" class="text-center text-gray-500">Chargement…</div>
        <div v-else-if="error" class="text-center text-red-600">{{ error }}</div>
        <AdministrativeEnedisMandatePreview v-else-if="form?.representation_mandate" :form="form" :draft="draft"
            class="mx-auto" mode="print" />
    </div>

</template>

<style>
@page {
    size: A4;
    margin: 0;
}

html,
body {
    margin: 0;
    padding: 0 24px;
}

@media print {
    body {
        background: white;
    }
}
</style>