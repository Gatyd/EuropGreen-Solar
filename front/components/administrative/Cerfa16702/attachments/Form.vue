<script setup lang="ts">
import SignatureField from '~/components/common/SignatureField.vue'

type cerfa16702Draft = {
    dpc1: File[]
    dpc2: File[]
    dpc3: File[]
    dpc4: File[]
    dpc5: File[]
    dpc6: File[]
    dpc7: File[]
    dpc8: File[]
    dpc11: File[]
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
    if (!s.dpc1?.length) errors.push({ name: 'dpc1', message: 'DPC 1 requis (≥1 fichier).' })
    if (!s.dpc2?.length) errors.push({ name: 'dpc2', message: 'DPC 2 requis (≥1 fichier).' })
    if (!s.dpc3?.length) errors.push({ name: 'dpc3', message: 'DPC 3 requis (≥1 fichier).' })
    if (!s.dpc4?.length) errors.push({ name: 'dpc4', message: 'DPC 4 requis (≥1 fichier).' })
    if (!s.dpc5?.length) errors.push({ name: 'dpc5', message: 'DPC 5 requis (≥1 fichier).' })
    if (!s.dpc6?.length) errors.push({ name: 'dpc6', message: 'DPC 6 requis (≥1 fichier).' })
    if (!s.dpc7?.length) errors.push({ name: 'dpc7', message: 'DPC 7 requis (≥1 fichier).' })
    if (!s.dpc8?.length) errors.push({ name: 'dpc8', message: 'DPC 8 requis (≥1 fichier).' })
    if (!s.dpc11?.length) errors.push({ name: 'dpc11', message: 'DPC 11 requis (≥1 fichier).' })

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
        const appendList = (key: keyof cerfa16702Draft) => {
            if (Array.isArray(s[key])) {
                for (const f of s[key] as File[]) fd.append(key, f)
            }
        }
        appendList('dpc1'); appendList('dpc2'); appendList('dpc3'); appendList('dpc4');
        appendList('dpc5'); appendList('dpc6'); appendList('dpc7'); appendList('dpc8'); appendList('dpc11')

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
                <UFormField name="dpc1" label="DPC1 - Plan de situation du terrain (multi)" required>
                    <UFileUpload v-model="state.dpc1" multiple icon="i-lucide-image" label="Ajouter des images"
                        description="PNG, JPG ou JPEG" accept="image/*" />
                </UFormField>
                <UFormField name="dpc2" label="DPC2 - Plan de masse coté (multi)" required>
                    <UFileUpload v-model="state.dpc2" multiple icon="i-lucide-image" label="Ajouter des images"
                        description="PNG, JPG ou JPEG" accept="image/*" />
                </UFormField>
                <UFormField name="dpc3" label="DPC3 - Plan en coupe (multi)" required>
                    <UFileUpload v-model="state.dpc3" multiple icon="i-lucide-image" label="Ajouter des images"
                        description="PNG, JPG ou JPEG" accept="image/*" />
                </UFormField>
                <UFormField name="dpc4" label="DPC4 - Plan des façades/toitures (multi)" required>
                    <UFileUpload v-model="state.dpc4" multiple icon="i-lucide-image" label="Ajouter des images"
                        description="PNG, JPG ou JPEG" accept="image/*" />
                </UFormField>
                <UFormField name="dpc5" label="DPC5 - Aspect extérieur (multi)" required>
                    <UFileUpload v-model="state.dpc5" multiple icon="i-lucide-image" label="Ajouter des images"
                        description="PNG, JPG ou JPEG" accept="image/*" />
                </UFormField>
                <UFormField name="dpc6" label="DPC6 - Document graphique (multi)" required>
                    <UFileUpload v-model="state.dpc6" multiple icon="i-lucide-image" label="Ajouter des images"
                        description="PNG, JPG ou JPEG" accept="image/*" />
                </UFormField>
                <UFormField name="dpc7" label="DPC7 - Photo environnement proche (multi)" required>
                    <UFileUpload v-model="state.dpc7" multiple icon="i-lucide-image" label="Ajouter des images"
                        description="PNG, JPG ou JPEG" accept="image/*" />
                </UFormField>
                <UFormField name="dpc8" label="DPC8 - Photo paysage lointain (multi)" required>
                    <UFileUpload v-model="state.dpc8" multiple icon="i-lucide-image" label="Ajouter des images"
                        description="PNG, JPG ou JPEG" accept="image/*" />
                </UFormField>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <UFormField name="dpc11" label="DPC11 - Notice descriptive des matériaux (multi)" required>
                    <UFileUpload v-model="state.dpc11" multiple icon="i-lucide-image" label="Ajouter des images"
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
