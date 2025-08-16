<script setup lang="ts">
definePageMeta({ layout: 'public' })

const toast = useToast()
const creating = ref(false)
onMounted(() => { creating.value = true })

const submitPublic = async (form: FormData) => {
    form.set('source', 'web_form')
    const res = await apiRequest(
        () => $fetch('/api/requests/', { method: 'POST', body: form, credentials: 'include' }),
        toast
    )
    if (res) {
        toast.add({ title: 'Votre demande a été soumise avec succès', color: 'success' })
        creating.value = false
    }
}
</script>

<template>
    <div class="container mx-auto py-10">
        <UCard class="max-w-3xl mx-auto">
            <template #header>
                <h1 class="text-2xl font-semibold">Demande / Prospect</h1>
            </template>
            <RequestForm @submit="submitPublic" />
        </UCard>
    </div>
</template>