<script setup lang="ts">
const model = defineModel({ type: Boolean })

const props = defineProps<{
    formId?: string
    action?: 'full' | 'signature' | 'preview'
    // Visite technique existante pour pré-remplir le brouillon
    installation_completed?: any
}>()
const emit = defineEmits<{
    (e: 'submit'): void
}>()

// État partagé du brouillon de visite technique
const draft = reactive({
    modules_installed: false,
    inverters_installed: false,
    dc_ac_box_installed: false,
    battery_installed: false,

    photo_modules: null as File | null,
    photo_inverter: null as File | null,
    // URL pour l'aperçu si les photos existent côté serveur
    photo_modules_url: null as string | null,
    photo_inverter_url: null as string | null,

    client_signature: { signer_name: '', method: 'draw' as 'draw' | 'upload', dataUrl: '', file: null as File | null },
    installer_signature: { signer_name: '', method: 'draw' as 'draw' | 'upload', dataUrl: '', file: null as File | null },
    // Métadonnées pour l'aperçu
    generated_at: new Date().toISOString(),
    client_signature_image_url: null as string | null,
    client_signature_signed_at: null as string | null,
    installer_signature_image_url: null as string | null,
    installer_signature_signed_at: null as string | null,
})

// Hydrate le brouillon si une visite technique est fournie
watch(
    () => props.installation_completed,
    (ic: any) => {
        if (!ic) return
        draft.modules_installed = ic.modules_installed
        draft.inverters_installed = ic.inverters_installed
        draft.dc_ac_box_installed = ic.dc_ac_box_installed
        draft.battery_installed = ic.battery_installed
        // Photos
        draft.photo_inverter_url = ic.photo_inverter_url || null
        draft.photo_modules_url = ic.photo_modules_url || null

        // Métadonnées
        draft.generated_at = ic.updated_at || ic.created_at || new Date().toISOString()

        // Signatures (client)
        const cs = ic.client_signature
        if (cs) {
            draft.client_signature.signer_name = cs.signer_name || ''
            draft.client_signature_image_url = cs.signature_image || (typeof cs.signature_data === 'string' && cs.signature_data.startsWith('data:image/') ? cs.signature_data : null)
            draft.client_signature_signed_at = cs.signed_at || null
        }
        // Signatures (installateur)
        const is = ic.installer_signature
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
        :title="action === 'signature' ? 'Signature – Installation effectuée' : action === 'full' ? 'Installation effectuée' : 'Aperçu - Rapport Installation effectuée'"
        :fullscreen="action !== 'preview'" :ui="{ content: action !== 'preview' ? 'max-w-screen' : 'max-w-5xl' }">
        <template #body>
            <div :class="action !== 'preview' ? 'flex flex-col xl:flex-row gap-4' : ''">
                <InstallationCompletedForm v-if="action !== 'preview'" class="xl:basis-1/2" :draft="draft"
                    :form-id="props.formId" @submit="onSubmit" :action="props.action ?? 'full'" />
                <InstallationCompletedPreview :class="action !== 'preview' ? 'xl:basis-1/2 shadow-md rounded-lg' : ''" :draft="draft" />
            </div>
        </template>
    </UModal>
</template>
