<script setup lang="ts">

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
    title: 'Rapport d\'installation',
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
    const ic = form.value?.installation_completed
    return {
        modules_installed: ic.modules_installed,
        inverters_installed: ic.inverters_installed,
        dc_ac_box_installed: ic.dc_ac_box_installed,
        battery_installed: ic.battery_installed,
        // Photos
        photo_inverter: null,
        photo_modules: null,
        photo_inverter_url: ic.photo_inverter || null,
        photo_modules_url: ic.photo_modules || null,

        // Métadonnées
        generated_at: ic.updated_at || ic.created_at || new Date().toISOString(),

        // Signatures
        client_signature: { signer_name: ic?.client_signature?.signer_name || '' },
        installer_signature: { signer_name: ic?.installer_signature?.signer_name || '' },
        client_signature_image_url: ic?.client_signature?.signature_image || null,
        client_signature_signed_at: ic?.client_signature?.signed_at || null,
        installer_signature_image_url: ic?.installer_signature?.signature_image || null,
        installer_signature_signed_at: ic?.installer_signature?.signed_at || null,
    }
})
</script>

<template>
    <div class="min-h-screen">
        <div v-if="pending" class="text-center text-gray-500">Chargement…</div>
        <div v-else-if="error" class="text-center text-red-600">{{ error }}</div>
        <InstallationCompletedPreview v-else-if="form?.representation_mandate" :form="form" :draft="draft"
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