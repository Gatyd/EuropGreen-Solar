<script setup lang="ts">
import { useAuthStore } from '~/store/auth'
import SignatureField from '~/components/common/SignatureField.vue'

type YesNoUnknown = 'yes' | 'no' | 'unknown'

type TechnicalVisitDraft = {
    modules_installed: boolean
    inverters_installed: boolean
    dc_ac_box_installed: boolean
    battery_installed: boolean
    photo_modules: File | null
    photo_inverter: File | null
    client_signature: { signer_name: string; method: 'draw' | 'upload'; dataUrl: string; file: File | null }
    installer_signature: { signer_name: string; method: 'draw' | 'upload'; dataUrl: string; file: File | null }
}

const props = defineProps<{ draft: TechnicalVisitDraft, action?: 'full' | 'signature' | 'preview', formId?: string }>()
const emit = defineEmits<{
    (e: 'submit'): void
}>()

const state = toRef(props, 'draft')
const loading = ref(false)

const auth = useAuthStore()

// Validation globale
const validate = (s: TechnicalVisitDraft) => {
    const errors: { name: string; message: string }[] = []

    if (!s.photo_inverter) errors.push({ name: 'photo_inverter', message: 'Photo de l\'onduleur requise.' })
    if (!s.photo_modules) errors.push({ name: 'photo_modules', message: 'Photo des modules solaires requise.' })

    // Signature
    if (props.action === 'signature') {
        // En mode signature: ne valide que le champ du signataire courant, et uniquement le nom
        if (auth.user?.is_staff) {
            if (!s.installer_signature.signer_name.trim()) errors.push({ name: 'installer_signature.signer_name', message: 'Nom du signataire requis.' })
        } else {
            if (!s.client_signature.signer_name.trim()) errors.push({ name: 'client_signature.signer_name', message: 'Nom du signataire requis.' })
        }
    } else {
        // En mode complet, signatures non obligatoires
    }

    return errors
}

async function onSubmit() {
    const toast = useToast()
    loading.value = true

    try {
        if (props.action === 'signature') {
            // Soumission d'une signature uniquement
            const role = auth.user?.is_staff ? 'installer' : 'client'
            const sig = role === 'installer' ? props.draft.installer_signature : props.draft.client_signature
            const formData = new FormData()
            formData.append('role', role)
            formData.append('signer_name', sig.signer_name)
            if (sig.file) formData.append('signature_file', sig.file)
            else if (sig.dataUrl) formData.append('signature_data', sig.dataUrl)

            const res = await $fetch(`/api/installations/forms/${props.formId}/sign/`, {
                method: 'POST',
                credentials: 'include',
                body: (() => { formData.append('document', 'technical_visit'); return formData })(),
            })
            if (res) {
                toast.add({ title: 'Signature enregistrée', color: 'success', icon: 'i-heroicons-check-circle' })
                loading.value = false
                emit('submit')
            }
            return
        }

        // Création/MàJ de l'installation effectuée
        const s = props.draft
        const fd = new FormData()
        fd.append('modules_installed', s.modules_installed ? '1' : '0')
        fd.append('inverters_installed', s.inverters_installed ? '1' : '0')
        fd.append('dc_ac_box_installed', s.dc_ac_box_installed ? '1' : '0')
        fd.append('battery_installed', s.battery_installed ? '1' : '0')
        if (s.photo_inverter) fd.append('photo_inverter', s.photo_inverter)
        if (s.photo_modules) fd.append('photo_modules', s.photo_modules)

        if (s.installer_signature.signer_name && (s.installer_signature.file || s.installer_signature.dataUrl)) {
            fd.append('installer_signer_name', s.installer_signature.signer_name)
            if (s.installer_signature.file) fd.append('installer_signature_file', s.installer_signature.file)
            else if (s.installer_signature.dataUrl) fd.append('installer_signature_data', s.installer_signature.dataUrl)
        }
        const res = await $fetch(`/api/installations/forms/${props.formId}/installation-completed/`, {
            method: 'POST',
            credentials: 'include',
            body: fd,
        })
        if (res) {
            toast.add({ title: 'Installation enregistrée avec succès', color: 'success', icon: 'i-heroicons-check-circle' })
            emit('submit')
            loading.value = false
        }
    } catch (e: any) {
        const msg = e?.data?.detail || e.message || 'Erreur inconnue'
        const toast = useToast()
        toast.add({ title: 'Échec de soumission', description: String(msg), color: 'error' })
    }
}

</script>

<template>
    <UForm :state="state" :validate="validate" class="space-y-3" @submit.prevent="onSubmit">
        <div v-if="action === 'full'" class="space-y-3">

            <!-- Informations sur la toiture -->
            <UCard>
                <template #header>
                    <div class="font-semibold">Installation des éléments suivants</div>
                </template>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <UCheckbox v-model="state.modules_installed" label="Modules solaires" />
                    <UCheckbox v-model="state.inverters_installed" label="Onduleurs / micro-onduleurs" />
                    <UCheckbox v-model="state.dc_ac_box_installed" label="Coffret DC/AC" />
                    <UCheckbox v-model="state.battery_installed" label="Battéries" />
                </div>
            </UCard>

            <!-- Accessibilité -->
            <UCard>
                <template #header>
                    <div class="font-semibold">Photo des éléments installés</div>
                </template>
                <div class="space-y-4">
                    <UFormField name="photo_modules" label="Modules solaires" required>
                        <UFileUpload v-model="state.photo_modules" icon="i-lucide-image"
                            label="Importez la photo depuis la galerie" description="SVG, PNG, JPG ou JPEG"
                            accept="image/*" />
                    </UFormField>
                    <UFormField name="photo_inverter" label="Onduleur" required>
                        <UFileUpload v-model="state.photo_inverter" icon="i-lucide-image"
                            label="Importez la photo depuis la galerie" description="SVG, PNG, JPG ou JPEG"
                            accept="image/*" />
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
