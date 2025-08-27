<script setup lang="ts">
import SignatureField from '~/components/common/SignatureField.vue'
import { useAuthStore } from '~/store/auth'
import type { InstallationForm, RepresentationMandate } from '~/types/installations'

type Civility = '' | 'Madame' | 'Monsieur'

type MandateDraft = {
    // Mandant (client)
    client_civility: Civility
    client_birth_date: string
    client_birth_place: string
    client_address: string
    // Mandataire (installateur)
    company_name: string
    company_rcs_city: string
    company_siret: string
    company_head_office_address: string
    represented_by: string
    representative_role: string
    // Signatures
    client_signature: { signer_name: string; method: 'draw' | 'upload'; dataUrl: string; file: File | null }
    installer_signature: { signer_name: string; method: 'draw' | 'upload'; dataUrl: string; file: File | null }
}

const props = defineProps<{
    draft: MandateDraft
    action?: 'full' | 'signature' | 'preview'
    form?: InstallationForm | null
    mandate?: RepresentationMandate | null
    formId?: string
}>()

const emit = defineEmits<{ (e: 'submit'): void }>()
const auth = useAuthStore()

const state = toRef(props, 'draft')
const loading = ref(false)

// Items UI
const civilityItems = ['Madame', 'Monsieur'].map(v => ({ label: v, value: v }))

// Validation minimale (on ne bloque pas les signatures en mode full pour rester flexible)
const validate = (s: MandateDraft) => {
    const errors: { name: string; message: string }[] = []
    if (!s.client_civility) errors.push({ name: 'client_civility', message: 'Civilité requise.' })
    if (!s.client_birth_date) errors.push({ name: 'client_birth_date', message: 'Date de naissance requise.' })
    if (!s.client_birth_place.trim()) errors.push({ name: 'client_birth_place', message: 'Lieu de naissance requis.' })
    if (!s.client_address.trim()) errors.push({ name: 'client_address', message: 'Adresse requise.' })
    if (!s.company_name.trim()) errors.push({ name: 'company_name', message: 'Nom de la société requis.' })
    if (!s.company_rcs_city.trim()) errors.push({ name: 'company_rcs_city', message: 'Ville RCS requise.' })
    if (!s.company_siret.trim()) errors.push({ name: 'company_siret', message: 'Numéro SIRET requis.' })
    if (!s.company_head_office_address.trim()) errors.push({ name: 'company_head_office_address', message: 'Adresse du siège social requise.' })
    if (!s.represented_by.trim()) errors.push({ name: 'represented_by', message: 'Représentant requis.' })

    if (props.action === 'signature') {
        // Si on est en mode signature, on exige au moins le nom du signataire courant
        // Ici on ne distingue pas le rôle; la page pilotera l’action spécifique plus tard
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
        if (!props.formId) {
            toast.add({ title: 'Formulaire manquant', description: 'Impossible de soumettre sans ID de fiche.', color: 'error' })
            return
        }

        if (props.action === 'signature') {
            // Signature générique du mandat
            const role = auth.user?.is_staff ? 'installer' : 'client'
            const sig = role === 'installer' ? state.value.installer_signature : state.value.client_signature
            const fd = new FormData()
            fd.append('document', 'representation_mandate')
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
        const civMap: Record<string, string> = { 'Madame': 'mme', 'Monsieur': 'mr' }
        const payload: any = {
            client_civility: s.client_civility ? civMap[s.client_civility] : undefined,
            client_birth_date: s.client_birth_date,
            client_birth_place: s.client_birth_place,
            client_address: s.client_address,
            company_name: s.company_name,
            company_rcs_city: s.company_rcs_city,
            company_siret: s.company_siret,
            company_head_office_address: s.company_head_office_address,
            represented_by: s.represented_by,
            representative_role: s.representative_role,
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
            await $fetch(`/api/installations/forms/${props.formId}/representation-mandate/`, {
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
    <UForm :state="state" :validate="validate" class="space-y-4" @submit.prevent="onSubmit">
        <div v-if="action === 'full'" class="space-y-3">
            <!-- Mandant (Client) -->
            <UCard>
                <template #header>
                    <div class="font-medium">Informations du mandant (client)</div>
                </template>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <UFormField label="Civilité" name="client_civility" required>
                        <USelect v-model="state.client_civility" class="w-full" :items="civilityItems"
                            placeholder="Sélectionnez" />
                    </UFormField>
                    <UFormField label="Date de naissance" name="client_birth_date" required>
                        <UInput v-model="state.client_birth_date" class="w-full" type="date" />
                    </UFormField>
                    <UFormField label="Lieu de naissance" name="client_birth_place" required>
                        <UInput v-model="state.client_birth_place" class="w-full" placeholder="Ville, pays" />
                    </UFormField>
                    <UFormField class="md:col-span-3" label="Adresse complète" name="client_address" required>
                        <UTextarea v-model="state.client_address" class="w-full" :rows="3"
                            placeholder="Adresse complète du client" />
                    </UFormField>
                </div>
            </UCard>

            <!-- Mandataire (Installateur) -->
            <UCard>
                <template #header>
                    <div class="font-medium">Informations du mandataire (installateur)</div>
                </template>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <UFormField label="Nom de la société" name="company_name" required>
                        <UInput v-model="state.company_name" class="w-full" placeholder="Nom de la société" />
                    </UFormField>
                    <UFormField label="Immatriculation au RCS de" name="company_rcs_city" required>
                        <UInput v-model="state.company_rcs_city" class="w-full" placeholder="Ex: Paris" />
                    </UFormField>
                    <UFormField label="Numéro SIRET" name="company_siret" required>
                        <UInput v-model="state.company_siret" class="w-full" placeholder="Ex: 123 456 789 00012" />
                    </UFormField>
                    <div class="col-span-3 grid grid-cols-1 md:grid-cols-2 gap-3">
                        <UFormField label="Représenté par" name="represented_by" required>
                            <UInput v-model="state.represented_by" class="w-full" placeholder="Nom et prénom" />
                        </UFormField>
                        <UFormField label="En qualité de" name="representative_role" required>
                            <UInput v-model="state.representative_role" class="w-full" />
                        </UFormField>
                    </div>
                    <UFormField class="md:col-span-3" label="Adresse du siège social" name="company_head_office_address"
                        required>
                        <UTextarea v-model="state.company_head_office_address" class="w-full" :rows="2"
                            placeholder="Adresse du siège social" />
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
                    <SignatureField v-model="state.installer_signature" :required="true" label="Nom du signataire" />
                </div>
                <div v-else>
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
