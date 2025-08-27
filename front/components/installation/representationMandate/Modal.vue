<script setup lang="ts">
import type { InstallationForm } from '~/types/installations'

const model = defineModel({ type: Boolean })

const props = defineProps<{
  form?: InstallationForm | null
  mandate?: InstallationForm['representation_mandate'] | null
  formId?: string
  action?: 'full' | 'signature' | 'preview'
}>()

const emit = defineEmits<{ (e: 'submit'): void }>()

// État partagé du brouillon du mandat
const draft = reactive({
  // Client
  client_civility: '' as '' | 'Madame' | 'Monsieur',
  client_birth_date: '',
  client_birth_place: '',
  client_address: props.form?.client_address || '',
  // Société (installateur)
  company_name: '',
  company_rcs_city: '',
  company_siret: '',
  company_head_office_address: '',
  represented_by: '',
  representative_role: '',
  // Signatures
  client_signature: { signer_name: '', method: 'draw' as 'draw' | 'upload', dataUrl: '', file: null as File | null },
  installer_signature: { signer_name: '', method: 'draw' as 'draw' | 'upload', dataUrl: '', file: null as File | null },
  // Métadonnées pour preview
  generated_at: new Date().toISOString(),
  client_signature_image_url: null as string | null,
  client_signature_signed_at: null as string | null,
  installer_signature_image_url: null as string | null,
  installer_signature_signed_at: null as string | null,
})

// Hydrate le brouillon depuis le mandat existant + la fiche
watch(
  () => props.mandate,
  (rm: any) => {
    if (!rm) return
  // Les valeurs backend sont probablement 'mme' | 'mr'
  draft.client_civility = (rm.client_civility === 'mr' ? 'Monsieur' : rm.client_civility === 'mme' ? 'Madame' : '') as any
    draft.client_birth_date = rm.client_birth_date || ''
    draft.client_birth_place = rm.client_birth_place || ''
    draft.client_address = rm.client_address || (props.form?.client_address || '')

    draft.company_name = rm.company_name || ''
    draft.company_rcs_city = rm.company_rcs_city || ''
    draft.company_siret = rm.company_siret || ''
    draft.company_head_office_address = rm.company_head_office_address || ''
    draft.represented_by = rm.represented_by || ''

    draft.generated_at = rm.updated_at || rm.created_at || new Date().toISOString()

    const cs = rm.client_signature
    if (cs) {
      draft.client_signature.signer_name = cs.signer_name || ''
      draft.client_signature_image_url = cs.signature_image || null
      draft.client_signature_signed_at = cs.signed_at || null
    }
    const is = rm.installer_signature
    if (is) {
      draft.installer_signature.signer_name = is.signer_name || ''
      draft.installer_signature_image_url = is.signature_image || null
      draft.installer_signature_signed_at = is.signed_at || null
    }
  },
  { immediate: true }
)

// Si la fiche change (pré-remplissage adresse client)
watch(() => props.form, (f) => {
  if (!f) return
  if (!draft.client_address) draft.client_address = f.client_address || ''
}, { immediate: true })

const onSubmit = () => {
  emit('submit')
  model.value = false
}
</script>

<template>
  <UModal v-model:open="model"
          :title="action === 'signature' ? 'Signature – Mandat de représentation' : action === 'full' ? 'Mandat de représentation' : 'Aperçu - Mandat de représentation'"
          :fullscreen="action !== 'preview'" :ui="{ content: action !== 'preview' ? 'max-w-screen' : 'max-w-5xl' }">
    <template #body>
      <div :class="action !== 'preview' ? 'flex flex-col xl:flex-row gap-4' : ''">
        <InstallationRepresentationMandateForm v-if="action !== 'preview'" class="xl:basis-1/2"
          :draft="draft" :form="props.form" :mandate="props.mandate" :form-id="props.formId" :action="props.action ?? 'full'"
          @submit="onSubmit" />
        <InstallationRepresentationMandatePreview :class="action !== 'preview' ? 'xl:basis-1/2 shadow-md rounded-lg' : ''" :draft="draft" :form="form" />
      </div>
    </template>
  </UModal>
  
</template>
