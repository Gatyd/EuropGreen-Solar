<script setup lang="ts">
import SignatureField from '~/components/common/SignatureField.vue'
import { useAuthStore } from '~/store/auth'
import type { ClientType, ConnectionNature, EnedisMandate, InstallationForm, MandateType, RepresentationMandate } from '~/types/installations'

type Civility = '' | 'Madame' | 'Monsieur'

type MandateDraft = {
    // Mandant (client)
    client_name: string
    client_type: ClientType
    client_civility: Civility | string
    client_address: string
    client_company_name: string
    client_company_siret: string
    client_company_represented_by_name: string
    client_company_represented_by_role: string
    // Entreprise en charge
    contractor_name: string
    contractor_type: ClientType
    contractor_civility: Civility | string
    contractor_address: string
    contractor_company_name: string
    contractor_company_siret: string
    contractor_company_represented_by_name: string
    contractor_company_represented_by_role: string
    //Mandat
    mandate_type: MandateType
    authorize_signature: boolean
    authorize_payment: boolean
    authorize_l342: boolean
    authorize_network_access: boolean
    // Localisation
    geographic_area: string
    connection_nature: ConnectionNature
    // Signatures
    client_signature: { signer_name: string; method: 'draw' | 'upload'; dataUrl: string; file: File | null }
    client_location?: string
    installer_signature: { signer_name: string; method: 'draw' | 'upload'; dataUrl: string; file: File | null }
    installer_location?: string
}

const props = defineProps<{
    draft: MandateDraft
    action?: 'full' | 'signature' | 'preview'
    enedisMandate?: EnedisMandate | null
    formId?: string
}>()

const emit = defineEmits<{ (e: 'submit'): void }>()
const auth = useAuthStore()

const state = toRef(props, 'draft')
const loading = ref(false)

// Items UI
const clientTypeItems = [
    { value: 'individual', label: 'Particulier' },
    { value: 'company', label: 'Société' },
    { value: 'collectivity', label: 'Collectivité' }
]
const civilityItems = [
    { value: 'mr', label: 'Monsieur' },
    { value: 'mme', label: 'Madame' },
]
const mandateItems = [
    { value: 'simple', label: 'Simple' },
    { value: 'special', label: 'Spécial' },
]
const connectionNatureItems = [
    { value: 'indiv_or_group_housing', label: 'Raccordement de logements individuels ou groupés' },
    { value: 'commercial_or_production', label: 'Locaux commerciaux/professionnels ou installation de production' },
    { value: 'branch_modification', label: 'Modification de branchement' },
    { value: 'power_change_or_ev', label: 'Modification de la puissance de raccordement / IRVE' },
]

// Validation minimale (on ne bloque pas les signatures en mode full pour rester flexible)
const validate = (s: MandateDraft) => {
    const errors: { name: string; message: string }[] = []
    if (s.client_type === 'individual') {
        if (!s.client_type) errors.push({ name: 'client_type', message: 'Type de client requis.' })
        if (!s.client_civility) errors.push({ name: 'client_civility', message: 'Civilité requise.' })
        if (!s.client_address.trim()) errors.push({ name: 'client_address', message: 'Adresse requise.' })
    } else {
        if (!s.client_company_name.trim()) errors.push({ name: 'client_company_name', message: 'Nom de la société requis.' })
        if (!s.client_company_siret.trim()) errors.push({ name: 'client_company_siret', message: 'Numéro SIRET requis.' })
        if (!s.client_company_represented_by_name.trim()) errors.push({ name: 'client_company_represented_by_name', message: 'Représentant requis.' })
    }
    if (s.contractor_type === 'individual') {
        if (!s.contractor_type) errors.push({ name: 'contractor_type', message: 'Type de client requis.' })
        if (!s.contractor_civility) errors.push({ name: 'contractor_civility', message: 'Civilité requise.' })
        if (!s.contractor_address.trim()) errors.push({ name: 'contractor_address', message: 'Adresse requise.' })
    } else {
        if (!s.contractor_company_name.trim()) errors.push({ name: 'contractor_company_name', message: 'Nom de la société requis.' })
        if (!s.contractor_company_siret.trim()) errors.push({ name: 'contractor_company_siret', message: 'Numéro SIRET requis.' })
        if (!s.contractor_company_represented_by_name.trim()) errors.push({ name: 'contractor_company_represented_by_name', message: 'Représentant requis.' })
    }
    if (!s.mandate_type) errors.push({ name: 'mandate_type', message: 'Type de mandat requis.' })
    if (!s.geographic_area.trim()) errors.push({ name: 'geographic_area', message: 'Zone géographique requise.' })
    if (!s.connection_nature) errors.push({ name: 'connection_nature', message: 'Nature du raccordement requis.' })

    if (props.action === 'signature') {
        if (!s.client_signature.signer_name.trim() && !s.installer_signature.signer_name.trim()) {
            errors.push({ name: 'signature.signer_name', message: 'Nom du signataire requis.' })
        }
    }
    return errors
}

async function onSubmit() {
    const toast = useToast()
    loading.value = true
    try {
        if (props.action === 'signature') {
            // Signature générique du mandat
            const role = auth.user?.is_staff ? 'installer' : 'client'
            const sig = role === 'installer' ? state.value.installer_signature : state.value.client_signature
            const fd = new FormData()
            fd.append('document', 'enedis_mandate')
            fd.append('role', role)
            fd.append('signer_name', sig.signer_name)
            if (sig.file) fd.append('signature_file', sig.file)
            else if (sig.dataUrl) fd.append('signature_data', sig.dataUrl)

            await $fetch(`/api/installations/forms/${props.formId}/sign/`, {
                method: 'POST',
                credentials: 'include',
                body: fd,
            })
            toast.add({ title: 'Signature enregistrée', color: 'success', icon: 'i-heroicons-check-circle' })
            emit('submit')
            return
        }

        // Création / mise à jour mandat
        const s = state.value
        // JSON simple si pas de fichier signature à la création
        const payload: any = {
            client_name: s.client_name,
            client_type: s.client_type,
            client_civility: s.client_civility,
            client_address: s.client_address,
            client_company_name: s.client_company_name,
            client_company_siret: s.client_company_siret,
            client_company_represented_by_name: s.client_company_represented_by_name,
            contractor_name: s.contractor_name,
            contractor_type: s.contractor_type,
            contractor_civility: s.contractor_civility,
            contractor_address: s.contractor_address,
            contractor_company_name: s.contractor_company_name,
            contractor_company_siret: s.contractor_company_siret,
            contractor_company_represented_by_name: s.contractor_company_represented_by_name,
            contractor_company_represented_by_role: s.contractor_company_represented_by_role,
            mandate_type: s.mandate_type,
            authorize_signature: s.authorize_signature,
            authorize_payment: s.authorize_payment,
            authorize_l342: s.authorize_l342,
            authorize_network_access: s.authorize_network_access,
            geographic_area: s.geographic_area,
            connection_nature: s.connection_nature
        }
        // Ajouter signature installateur si fournie
        if (s.installer_signature.signer_name && (s.installer_signature.file || s.installer_signature.dataUrl)) {
            const hasFile = !!s.installer_signature.file
            if (!hasFile) {
                payload.installer_signer_name = s.installer_signature.signer_name
                payload.installer_signature_data = s.installer_signature.dataUrl
            }
        }

        const hasFile = !!s.installer_signature.file
        if (!hasFile) {
            await $fetch(`/api/installations/forms/${props.formId}/enedis-mandate/`, {
                method: 'POST',
                credentials: 'include',
                body: payload,
            })
        } else {
            const fd = new FormData()
            Object.entries(payload).forEach(([k, v]) => { if (v !== undefined && v !== null) fd.append(k, String(v)) })
            fd.append('installer_signer_name', s.installer_signature.signer_name)
            if (s.installer_signature.file) fd.append('installer_signature_file', s.installer_signature.file)
            await $fetch(`/api/installations/forms/${props.formId}/representation-mandate/`, {
                method: 'POST',
                credentials: 'include',
                body: fd,
            })
        }
        toast.add({ title: 'Mandat enregistré', color: 'success', icon: 'i-heroicons-check-circle' })
        emit('submit')
    } catch (e: any) {
        toast.add({ title: 'Erreur', description: e?.data?.detail || e?.message || 'Échec de soumission', color: 'error' })
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <UForm :state="state" :validate="validate" class="space-y-4 p-3" @submit.prevent="onSubmit">
        <div v-if="action === 'full'" class="space-y-3">
            <UCard>
                <template #header>
                    <div class="font-medium">Informations du client</div>
                </template>
                <div>
                    <UFormField label="Type de client" name="client_type" required>
                        <USelect v-model="state.client_type" class="w-full" :items="clientTypeItems"
                            placeholder="Sélectionnez" />
                    </UFormField>
                </div>
                <div v-if="state.client_type === 'individual'" class="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3">
                    <UFormField label="Civilité" name="client_civility" required>
                        <URadioGroup v-model="state.client_civility" :items="civilityItems" orientation="horizontal" />
                    </UFormField>
                    <UFormField label="Nom et Prénom" name="client_name" required>
                        <UInput v-model="state.client_name" class="w-full" placeholder="Nom et prénom du client" />
                    </UFormField>
                    <UFormField class="md:col-span-2" label="Adresse complète" name="client_address" required>
                        <UTextarea v-model="state.client_address" class="w-full" :rows="2"
                            placeholder="Adresse complète du client" />
                    </UFormField>
                </div>
                <div v-else class="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3">
                    <UFormField label="Nom de l'entreprise" name="client_company_name" required>
                        <UInput v-model="state.client_company_name" class="w-full" placeholder="Nom de l'entreprise" />
                    </UFormField>
                    <UFormField label="SIRET" name="client_company_siret" required>
                        <UInput v-model="state.client_company_siret" class="w-full"
                            placeholder="N° SIRET l'entreprise" />
                    </UFormField>
                    <UFormField label="Représenté par" name="client_company_represented_by_name" required>
                        <UInput v-model="state.client_company_represented_by_name" class="w-full"
                            placeholder="Nom et prénom du représentant" />
                    </UFormField>
                    <UFormField label="En qualité de" name="client_company_represented_by_role" required>
                        <UInput v-model="state.client_company_represented_by_role" class="w-full"
                            placeholder="Fonction du représentant" />
                    </UFormField>
                </div>
            </UCard>

            <UCard>
                <template #header>
                    <div class="font-medium">Entreprise qui prend en charge</div>
                </template>
                <div>
                    <UFormField label="Type" name="contractor_type" required>
                        <USelect v-model="state.contractor_type" class="w-full" :items="clientTypeItems"
                            placeholder="Sélectionnez" />
                    </UFormField>
                </div>
                <div v-if="state.contractor_type === 'individual'" class="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3">
                    <UFormField label="Civilité" name="contractor_civility" required>
                        <URadioGroup v-model="state.contractor_civility" :items="civilityItems" orientation="horizontal" />
                    </UFormField>
                    <UFormField label="Nom et Prénom" name="contractor_name" required>
                        <UInput v-model="state.contractor_name" class="w-full" placeholder="Nom et prénom de l'entrepreneur" />
                    </UFormField>
                    <UFormField class="md:col-span-2" label="Adresse complète" name="contractor_address" required>
                        <UTextarea v-model="state.contractor_address" class="w-full" :rows="2"
                            placeholder="Adresse complète de l'entreprise" />
                    </UFormField>
                </div>
                <div v-else class="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3">
                    <UFormField label="Nom de la société" name="contractor_company_name" required>
                        <UInput v-model="state.contractor_company_name" class="w-full"
                            placeholder="Nom de la société" />
                    </UFormField>
                    <UFormField label="Numéro SIRET" name="contractor_company_siret" required>
                        <UInput v-model="state.contractor_company_siret" class="w-full"
                            placeholder="Ex: 123 456 789 00012" />
                    </UFormField>
                    <div class="col-span-2 grid grid-cols-1 md:grid-cols-2 gap-3">
                        <UFormField label="Représenté par" name="contractor_company_represented_by_name" required>
                            <UInput v-model="state.contractor_company_represented_by_name" class="w-full"
                                placeholder="Nom et prénom" />
                        </UFormField>
                        <UFormField label="En qualité de" name="contractor_company_represented_by_role" required>
                            <UInput v-model="state.contractor_company_represented_by_role" class="w-full" />
                        </UFormField>
                    </div>
                </div>
            </UCard>

            <UCard>
                <template #header>
                    <div class="font-medium">Le mandat</div>
                </template>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <UFormField label="Type de mandat" name="mandate_type" required>
                        <URadioGroup v-model="state.mandate_type" :items="mandateItems" orientation="horizontal" />
                    </UFormField>
                    <div class="space-y-1">
                        <UCheckbox v-model="state.authorize_signature" label="Signature du client" />
                        <UCheckbox v-model="state.authorize_payment" label="Paiement du client" />
                    </div>
                    <div class="space-y-1">
                        <UCheckbox v-model="state.authorize_l342" label="L342" />
                        <UCheckbox v-model="state.authorize_network_access" label="Accès réseau" />
                    </div>
                </div>
            </UCard>

            <UCard>
                <template #header>
                    <div class="font-medium">Localisation</div>
                </template>
                <div class="grid grid-cols-1 gap-3">
                    <UFormField label="Nature du raccordement" name="connection_nature" required>
                        <USelect v-model="state.connection_nature" :items="connectionNatureItems" class="w-full" />
                    </UFormField>
                    <UFormField label="Zone géographique" name="geographic_area" required>
                        <UTextarea v-model="state.geographic_area" :rows="3" class="w-full" />
                    </UFormField>
                </div>
            </UCard>
        </div>

        <!-- Signatures -->
        <UCard>
            <template #header>
                <div class="font-semibold">Signature {{ auth.user?.is_staff ? 'installateur' : 'client' }}</div>
            </template>
            <div class="space-y-6">
                <div v-if="auth.user?.is_staff">
                    <UFormField label="Lieu" name="installer_location" required>
                        <UInput v-model="state.installer_location" class="w-full mb-3" />
                    </UFormField>
                    <SignatureField v-model="state.installer_signature" :required="true" label="Nom du signataire" />
                </div>
                <div v-else>
                    <UFormField label="Lieu" name="client_location" required>
                        <UInput v-model="state.client_location" class="w-full mb-3" />
                    </UFormField>
                    <SignatureField v-model="state.client_signature" :required="true" label="Nom du signataire" />
                </div>
            </div>
        </UCard>

        <div class="flex justify-end pt-2">
            <UButton v-if="props.action === 'signature'" :loading="loading" color="primary"
                icon="i-heroicons-pencil-square" type="submit" label="Signer" />
            <UButton v-else color="primary" :loading="loading" icon="i-heroicons-check-circle" type="submit"
                label="Enregistrer" />
        </div>
    </UForm>
</template>
