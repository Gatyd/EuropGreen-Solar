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
    <div class="m-20">
        <Logo />
    </div>
</template>