<script setup lang="ts">

const props = defineProps<{ formId?: string }>()
const emit = defineEmits<{
    (e: 'submit'): void
}>()

const loading = ref(false)

const state = reactive({
    file: null as File | null
})

const validate = () => {
    const errors: { name: string; message: string }[] = []
    if (!state.file) {
        errors.push({ name: 'file', message: 'Schéma électrique requis' })
    }
    return errors
}

const submit = async () => {
    const toast = useToast()
    loading.value = true
    try {
        const fd = new FormData()
        fd.append('file', state.file as File)

        const res = await $fetch(`/api/administrative/electrical-diagram/form/${props.formId}/`, {
            method: 'POST',
            credentials: 'include',
            body: fd,
        })
        if (res) {
            toast.add({ title: 'Diagramme électrique enregistré avec succès', color: 'success', icon: 'i-heroicons-check-circle' })
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
    <UForm :state="state" :validate="validate" @submit="submit">
        <UFormField name="file" required>
            <UFileUpload v-model="state.file" icon="i-heroicons-arrow-up-tray-16-solid" label="Importer une image"
                description="PNG, JPG, JPEG ou PDF" accept="image/*,.pdf" />
        </UFormField>
        <div class="flex items-center justify-end mt-4">
            <UButton type="submit">Enregistrer</UButton>
        </div>
    </UForm>
</template>