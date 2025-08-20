<script setup lang="ts">

const props = defineProps<{ lastQuote: any }>()

const emit = defineEmits<{
    (e: 'submitted', message: string): void
}>()

const state = reactive({ message: '' })
const loading = ref(false)

const validate = (s: { message: string }) => {
    const errors: { path: string; message: string }[] = []
    if (!s.message || !s.message.trim()) {
        errors.push({ path: 'message', message: 'Veuillez entrer votre message.' })
    }
    return errors
}

const onSubmit = async () => {
    if (!props.lastQuote) return
    const toast = useToast()
    loading.value = true
    const res = await apiRequest(
        () => $fetch(`/api/quotes/${props.lastQuote.id}/negotiate/`, {
            method: 'POST',
            body: { message: state.message },
        }),
        toast
    )
    if (res) {
        emit('submitted', state.message.trim())
    }
    loading.value = false
}
</script>

<template>
    <UForm :state="state" :validate="validate" @submit.prevent="onSubmit">
        <UFormField name="message" label="Votre question / demande de négociation">
            <UTextarea v-model="state.message" :rows="8" class="w-full"
                placeholder="Décrivez votre question, vos contraintes ou votre proposition..." />
        </UFormField>
        <div class="mt-4">
            <UButton type="submit" :loading="loading" color="primary" label="Envoyer" />
        </div>
    </UForm>
</template>
