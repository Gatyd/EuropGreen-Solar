<script setup lang="ts">
const props = defineProps<{ draft: any; form?: any; formId?: string }>()
const emit = defineEmits<{
    (e: 'submit'): void
}>()

const tabsItems = [
    { label: '144A', value: '144a', slot: 'a' },
    { label: '144B', value: '144b', slot: 'b' },
    { label: '144C', value: '144c', slot: 'c' },
    { label: '144C2', value: '144c2', slot: 'c2' }
]
const loading = ref(false)
const toast = useToast()

async function onSubmit() {
    loading.value = true
    try {
        // Construire le payload: si signature/cachet fournis, utiliser FormData, sinon JSON
        const draft: any = props.draft
        // Construire une vue normalisée du draft (pas de formatage date côté front)
        const normalized: any = { ...draft }
        const hasSignatureUpload = !!(draft?.installer_signature?.file)
        const hasSignatureDraw = !!(draft?.installer_signature?.dataUrl)
        const hasStamp = !!draft?.installer_stamp

        let bodyToSend: any = null
        let headers: any = undefined
        if (hasSignatureUpload || hasSignatureDraw || hasStamp) {
            const fd = new FormData()
            for (const [k, v0] of Object.entries(normalized)) {
                if (k === 'installer_signature' || k === 'installer_stamp') continue
                // sérialiser booléens en '1'/'0'
                const v: any = v0 as any
                if (typeof v === 'boolean') fd.append(k, v ? '1' : '0')
                else if (v != null) fd.append(k, String(v))
            }
            // Signature
            if (hasSignatureUpload && draft.installer_signature.file) {
                fd.append('installer_signature', draft.installer_signature.file)
                if (draft.installer_signature.signer_name) fd.append('installer_name', draft.installer_signature.signer_name)
            } else if (hasSignatureDraw && draft.installer_signature.dataUrl) {
                // Passer via data URL; le backend la décodera si aucun fichier direct n'est fourni
                fd.append('installer_signature_data_url', draft.installer_signature.dataUrl)
                if (draft.installer_signature.signer_name) fd.append('installer_name', draft.installer_signature.signer_name)
            }
            // Ne pas forcer signature_date; le backend ajoute une valeur par défaut
            // Cachet
            const stamp: any = draft.installer_stamp
            if (stamp && typeof stamp === 'object' && 'name' in stamp && 'size' in stamp) {
                // suppose un File ou Blob avec name
                fd.append('installer_stamp', stamp as File)
            } else if (draft.installer_stamp && (draft.installer_stamp as any).name) {
                fd.append('installer_stamp', draft.installer_stamp as File)
            }
            bodyToSend = fd
        } else {
            // JSON simple (les booléens peuvent rester booleans)
            const { installer_signature, installer_stamp, ...rest } = normalized
            bodyToSend = { ...rest }
            headers = { 'Content-Type': 'application/json' }
        }

        const resp = await apiRequest(
            () => $fetch(`/api/administrative/consuel/form/${props.formId}/`, {
                method: 'POST',
                body: bodyToSend,
                credentials: 'include'
            }),
            toast
        )
        if(resp){
            toast.add({ title: 'Consuel enregistré avec succès', color: 'success', icon: 'i-heroicons-check-circle' })
            emit('submit')
        }
    } catch (e: any) {
        const msg = e?.data?.detail || e.message || 'Erreur inconnue'
        const toast = useToast()
        toast.add({ title: 'Échec de soumission', description: String(msg), color: 'error' })
    } finally {
        loading.value = false
    }
}

</script>

<template>
    <div class="space-y-4">
        <UTabs v-model="draft.template" :items="tabsItems">
            <template #a>
                <AdministrativeConsuelFormSC144A :draft="draft" :loading="loading" @submit="onSubmit" />
            </template>
            <template #b>
                <AdministrativeConsuelFormSC144B :draft="draft" :loading="loading" @submit="onSubmit" />
            </template>
            <template #c>
                <AdministrativeConsuelFormSC144C :draft="draft" :loading="loading" @submit="onSubmit" />
            </template>
            <template #c2>
                <AdministrativeConsuelFormSC144C2 :draft="draft" :loading="loading" @submit="onSubmit" />
            </template>
        </UTabs>
    </div>
</template>
