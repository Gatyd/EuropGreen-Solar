<script setup lang="ts">
import type { Civility, ClientType, ConnectionNature, InstallationForm, MandateType } from '~/types/installations'

const model = defineModel({ type: Boolean })

const props = defineProps<{
    form: InstallationForm | null
    representationMandate?: InstallationForm['representation_mandate'] | null
    enedisMandate?: InstallationForm['enedis_mandate'] | null
    formId?: string
    action?: 'full' | 'signature' | 'preview'
}>()

const emit = defineEmits<{ (e: 'submit'): void }>()

// État partagé du brouillon du mandat
const draft = reactive({
    // Client
    client_type: 'individual' as ClientType,
    client_civility: '' as Civility,
    client_name: '',
    client_address: '',
    // Société / Collectivité
    client_company_name: '',
    client_company_siret: '',
    client_company_represented_by_name: '',
    client_company_represented_by_role: '',

    // Entreprise en charge
    contractor_type: 'company' as ClientType,
    contractor_civility: '' as Civility,
    contractor_name: '',
    contractor_address: '',
    contractor_company_name: '',
    contractor_company_siret: '',
    contractor_company_represented_by_name: '',
    contractor_company_represented_by_role: '',

    // Mandat
    mandate_type: 'simple' as MandateType,
    authorize_signature: false,
    authorize_payment: false,
    authorize_l342: false,
    authorize_network_access: false,

    // Localisation
    geographic_area: '',
    connection_nature: '' as ConnectionNature,
    client_location: '',
    installer_location: '',

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
    () => props.enedisMandate,
    (em: any) => {
        if (!em) return

        draft.client_type = em.client_type || ''
        draft.client_civility = em.client_civility || '' as Civility
        draft.client_address = em.client_address || ''
        draft.client_company_name = em.client_company_name || ''
        draft.client_company_siret = em.client_company_siret || ''
        draft.client_company_represented_by_name = em.client_company_represented_by_name || ''
        draft.client_company_represented_by_role = em.client_company_represented_by_role || ''

        draft.contractor_type = em.contractor_type || ''
        draft.contractor_civility = em.contractor_civility || '' as Civility
        draft.contractor_address = em.contractor_address || ''
        draft.contractor_company_name = em.contractor_company_name || ''
        draft.contractor_company_siret = em.contractor_company_siret || ''
        draft.contractor_company_represented_by_name = em.contractor_company_represented_by_name || ''
        draft.contractor_company_represented_by_role = em.contractor_company_represented_by_role || ''

        draft.mandate_type = em.mandate_type || 'simple'
        draft.authorize_signature = em.authorize_signature || false
        draft.authorize_payment = em.authorize_payment || false
        draft.authorize_l342 = em.authorize_l342 || false
        draft.authorize_network_access = em.authorize_network_access || false

        draft.geographic_area = em.geographic_area || ''
        draft.connection_nature = em.connection_nature || '' as ConnectionNature
        draft.client_location = em.client_location || ''
        draft.installer_location = em.installer_location || ''

        const cs = em.client_signature
        if (cs) {
            draft.client_signature.signer_name = cs.signer_name || ''
            draft.client_signature_image_url = cs.signature_image || null
            draft.client_signature_signed_at = cs.signed_at || null
        }
        const is = em.installer_signature
        if (is) {
            draft.installer_signature.signer_name = is.signer_name || ''
            draft.installer_signature_image_url = is.signature_image || null
            draft.installer_signature_signed_at = is.signed_at || null
        }
    },
    { immediate: true }
)

// Pré-remplissage des informations depuis form et documents existants
watch(() => props.form, (f) => {
    if (!f || props.enedisMandate) return // Ne pas pré-remplir si mandat ENEDIS existe déjà
    
    const client = f.client
    const mandate = props.representationMandate || f.representation_mandate
    const cerfa = f.cerfa16702
    
    // === INFORMATIONS CLIENT ===
    // Nom client - priorité: client > offer (form.client a first_name/last_name)
    if (!draft.client_name) {
        if (client) {
            draft.client_name = `${client.first_name} ${client.last_name}`.trim()
        } else if (f.offer) {
            draft.client_name = `${f.offer.first_name} ${f.offer.last_name}`.trim()
        }
    }
    
    // Adresse client - priorité: mandate > cerfa > form.client_address > offer
    if (!draft.client_address) {
        if (mandate && mandate.client_address) {
            draft.client_address = mandate.client_address
        } else if (cerfa && cerfa.address_street) {
            draft.client_address = cerfa.address_street
        } else if (f.client_address) {
            draft.client_address = f.client_address
        } else if (f.offer && f.offer.address) {
            draft.client_address = f.offer.address
        }
    }
    
    // Civilité client depuis mandate
    if (!draft.client_civility && mandate && mandate.client_civility) {
        draft.client_civility = mandate.client_civility
    }
    
    // === INFORMATIONS INSTALLATEUR (ENTREPRISE EN CHARGE) ===
    // Priorité: mandate > cerfa
    if (mandate) {
        if (!draft.contractor_company_name) draft.contractor_company_name = mandate.company_name || ''
        if (!draft.contractor_company_siret) draft.contractor_company_siret = mandate.company_siret || ''
        if (!draft.contractor_company_represented_by_name) draft.contractor_company_represented_by_name = mandate.represented_by || ''
        if (!draft.contractor_company_represented_by_role) draft.contractor_company_represented_by_role = mandate.representative_role || ''
        if (!draft.contractor_address) draft.contractor_address = mandate.company_head_office_address || ''
    } else if (cerfa && cerfa.declarant_type === 'company') {
        // Si pas de mandat mais CERFA avec type entreprise
        if (!draft.contractor_company_name) draft.contractor_company_name = cerfa.company_denomination || ''
        if (!draft.contractor_company_siret) draft.contractor_company_siret = cerfa.company_siret || ''
        if (!draft.contractor_address) draft.contractor_address = cerfa.address_street || ''
    }
}, { immediate: true })

// Si la fiche change (pré-remplissage adresse client) - ANCIEN CODE CONSERVÉ POUR COMPATIBILITÉ
watch(() => props.representationMandate, (rm) => {
    if (!rm) return
    if (!draft.client_civility) draft.client_civility = rm.client_civility || '' as Civility
    if (!draft.client_address) draft.client_address = rm.client_address || ''
    if (!draft.contractor_company_name) draft.contractor_company_name = rm.company_name || ''
    if (!draft.contractor_company_siret) draft.contractor_company_siret = rm.company_siret || ''
    if (!draft.contractor_company_represented_by_name) draft.contractor_company_represented_by_name = rm.represented_by || ''
    if (!draft.contractor_company_represented_by_role) draft.contractor_company_represented_by_role = rm.representative_role || ''
}, { immediate: true })

const onSubmit = () => {
    emit('submit')
    model.value = false
}
</script>

<template>
    <UModal v-model:open="model"
        :title="action === 'signature' ? 'Signature – Mandat Enedis' : action === 'full' ? 'Mandat Enedis' : 'Aperçu - Mandat Enedis'"
        :fullscreen="action !== 'preview'" :ui="{ content: action !== 'preview' ? 'max-w-screen' : 'max-w-5xl' }">
        <template #body>
            <div :class="action !== 'preview' ? 'flex flex-col xl:flex-row gap-4 h-full xl:overflow-hidden' : ''">
                <AdministrativeEnedisMandateForm v-if="action !== 'preview'" class="xl:basis-1/2 xl:min-h-0 xl:overflow-auto"
                    :draft="draft" :enedis-mandate="props.enedisMandate" :form-id="props.formId"
                    :action="props.action ?? 'full'" @submit="onSubmit" />
                <div class="xl:min-h-0 xl:overflow-auto" :class="action !== 'preview' ? 'xl:basis-1/2' : ''">
                    <AdministrativeEnedisMandatePreview :form="form" :form-id="formId" :mode="action !== 'preview' ? 'edit' : 'preview'" :draft="draft" />
                </div>
            </div>
        </template>
    </UModal>

</template>
