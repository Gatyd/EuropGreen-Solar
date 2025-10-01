<script setup lang="ts">
import type { Item } from '~/types'

const model = defineModel({
    type: String
})

const installations = ref<Item[]>([])
const loading = ref(false)
const toast = useToast()

const fetchInstallations = async () => {
    loading.value = true
    const response = await apiRequest<any[]>(
        () => $fetch('/api/installations/forms/', { credentials: 'include' }),
        toast
    )
    if (response) {
        installations.value = response.map((installation: any) => {
            // Format: Prénom Initiale. - Adresse
            const request = installation.offer?.request
            const lastNameInitial = request?.last_name?.charAt(0) || ''
            const firstName = request?.first_name || ''
            const address = request?.address || installation.client_address || 'Adresse non renseignée'
            
            return {
                label: `${firstName} ${lastNameInitial}.  •  ${address}`,
                value: installation.id
            }
        })
    }
    loading.value = false
}

onMounted(() => {
    fetchInstallations()
})
</script>

<template>
    <USelectMenu v-model="model" v-bind="$attrs" :items="installations" :loading="loading" searchable
        searchable-placeholder="Rechercher une installation..." value-key="value" />
</template>
