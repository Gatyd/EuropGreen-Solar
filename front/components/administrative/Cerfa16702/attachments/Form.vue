<script setup lang="ts">
import SignatureField from '~/components/common/SignatureField.vue'

type cerfa16702Draft = {
    dpc1: File | null,
    dpc2: File | null,
    dpc3: File | null,
    dpc4: File | null,
    dpc5: File | null,
    dpc6: File | null,
    dpc7: File | null,
    dpc8: File | null,
    dpc11: File | null,
    dpc11_notice_materiaux: string
}

const props = defineProps<{ draft: cerfa16702Draft, cerfaId?: string }>()
const emit = defineEmits<{
    (e: 'submit'): void
}>()

const state = toRef(props, 'draft')
const loading = ref(false)

// Validation globale
const validate = (s: cerfa16702Draft) => {
    const errors: { name: string; message: string }[] = []

    // Pièces jointes
    if (!s.dpc1) errors.push({ name: 'dpc1', message: 'DPC 1 requis.' })
    if (!s.dpc2) errors.push({ name: 'dpc2', message: 'DPC 2 requis.' })
    if (!s.dpc3) errors.push({ name: 'dpc3', message: 'DPC 3 requis.' })
    if (!s.dpc4) errors.push({ name: 'dpc4', message: 'DPC 4 requis.' })
    if (!s.dpc5) errors.push({ name: 'dpc5', message: 'DPC 5 requis.' })
    if (!s.dpc6) errors.push({ name: 'dpc6', message: 'DPC 6 requis.' })
    if (!s.dpc7) errors.push({ name: 'dpc7', message: 'DPC 7 requis.' })
    if (!s.dpc8) errors.push({ name: 'dpc8', message: 'DPC 8 requis.' })
    if (!s.dpc11) errors.push({ name: 'dpc11', message: 'DPC 11 requis.' })

    return errors
}

async function onSubmit() {
    const toast = useToast()
    loading.value = true

    try {
        // Création/MàJ des pièces jointes du CERFA 16702
        const s = props.draft
        const fd = new FormData()
        fd.append('dpc11_notice_materiaux', s.dpc11_notice_materiaux)

        // Pièces jointes
        if (s.dpc1) fd.append('dpc1', s.dpc1)
        if (s.dpc2) fd.append('dpc2', s.dpc2)
        if (s.dpc3) fd.append('dpc3', s.dpc3)
        if (s.dpc4) fd.append('dpc4', s.dpc4)
        if (s.dpc5) fd.append('dpc5', s.dpc5)
        if (s.dpc6) fd.append('dpc6', s.dpc6)
        if (s.dpc7) fd.append('dpc7', s.dpc7)
        if (s.dpc8) fd.append('dpc8', s.dpc8)
        if (s.dpc11) fd.append('dpc11', s.dpc11)

        const res = await $fetch(`/api/administrative/cerfa16702/${props.cerfaId}/attachments/`, {
            method: 'POST',
            credentials: 'include',
            body: fd,
        })
        if (res) {
            toast.add({ title: 'Pièces jointes du CERFA 16702 enregistrées', color: 'success', icon: 'i-heroicons-check-circle' })
            emit('submit')
            loading.value = false
        }
    } catch (e: any) {
        const msg = e?.data?.detail || e.message || 'Erreur inconnue'
        const toast = useToast()
        toast.add({ title: 'Échec de soumission', description: String(msg), color: 'error' })
        loading.value = false
    }
}

</script>

<template>
    <UForm :state="state" :validate="validate" class="space-y-3 px-3" @submit.prevent="onSubmit">

        <div class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <UFormField name="dpc1" label="DPC1 - Plan de situation du terrain" required>
                    <UFileUpload v-model="state.dpc1" icon="i-lucide-image" label="Importer une image"
                        description="PNG, JPG ou JPEG" accept="image/*" />
                </UFormField>
                <UFormField name="dpc2" label="DPC2 - Plan de masse coté dans les 3 dimensions" required>
                    <UFileUpload v-model="state.dpc2" icon="i-lucide-image" label="Importer une image"
                        description="PNG, JPG ou JPEG" accept="image/*" />
                </UFormField>
                <UFormField name="dpc3" label="DPC3 - Plan en coupe précisant l'implantation de la constrauction par rapport au profil du terrain" required>
                    <UFileUpload v-model="state.dpc3" icon="i-lucide-image" label="Importer une image"
                        description="PNG, JPG ou JPEG" accept="image/*" />
                </UFormField>
                <UFormField name="dpc4" label="DPC4 - Plan des façades et des toitures" required>
                    <UFileUpload v-model="state.dpc4" icon="i-lucide-image" label="Importer une image"
                        description="PNG, JPG ou JPEG" accept="image/*" />
                </UFormField>
                <UFormField name="dpc5" label="DPC5 - Représentation de l'aspect extérieur de la construction" required>
                    <UFileUpload v-model="state.dpc5" icon="i-lucide-image" label="Importer une image"
                        description="PNG, JPG ou JPEG" accept="image/*" />
                </UFormField>
                <UFormField name="dpc6" label="DPC6 - Document graphique permettant d'apprécier l'insertion du projet dans son environnement" required>
                    <UFileUpload v-model="state.dpc6" icon="i-lucide-image" label="Importer une image"
                        description="PNG, JPG ou JPEG" accept="image/*" />
                </UFormField>
                <UFormField name="dpc7" label="DPC7 - Photographie permettant de situer le terrain dans l'environnement proche" required>
                    <UFileUpload v-model="state.dpc7" icon="i-lucide-image" label="Importer une image"
                        description="PNG, JPG ou JPEG" accept="image/*" />
                </UFormField>
                <UFormField name="dpc8" label="DPC8 - Photographie permettant de situer le terrain dans le paysage lointain" required>
                    <UFileUpload v-model="state.dpc8" icon="i-lucide-image" label="Importer une image"
                        description="PNG, JPG ou JPEG" accept="image/*" />
                </UFormField>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <UFormField name="dpc11" label="DPC11 - Notice descriptive des matériaux utilisés" required>
                    <UFileUpload v-model="state.dpc11" icon="i-lucide-image" label="Importer une image"
                        description="PNG, JPG ou JPEG" accept="image/*" />
                </UFormField>
                <UFormField name="dpc11_notice_materiaux" label="Notice descriptive des matériaux (texte)">
                    <UTextarea v-model="state.dpc11_notice_materiaux" :rows="6" class="w-full" />
                </UFormField>
            </div>
        </div>

        <div class="flex justify-end pt-2">
            <UButton :loading="loading" icon="i-heroicons-check-circle" type="submit" label="Enregistrer" />
        </div>
    </UForm>
</template>
