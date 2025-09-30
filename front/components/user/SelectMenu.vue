<script setup lang="ts">
import type { Item, User } from '~/types'
import UserModal from '~/components/user/Modal.vue'

const model = defineModel({
    type: String
})

const props = defineProps<{
    roleFilter?: string // 'sales', 'customer', 'collaborator'
}>()

const users = ref<Item[]>([])
const openMenu = ref(false)
const showModal = ref(false)
const loading = ref(false)
const toast = useToast()
const selectedUser = ref<User | null>(null)

const addNewUser = async (e?: Event) => {
    openMenu.value = false
    showModal.value = true
    selectedUser.value = null
}

const fetchUsers = async () => {
    loading.value = true
    let endpoint = '/api/users/'
    
    // Filtrage par rôle
    if (props.roleFilter === 'sales') {
        endpoint += '?role=sales'
    } else if (props.roleFilter === 'customer') {
        endpoint += '?role=customer'
    } else if (props.roleFilter === 'collaborator') {
        endpoint += '?role=collaborator'
    }
    
    const response = await apiRequest<User[]>(
        () => $fetch(endpoint, { credentials: 'include' }),
        toast
    )
    if (response) {
        users.value = response.map((user: User) => ({
            label: `${user.first_name} ${user.last_name}`,
            value: user.id
        }))
    }
    loading.value = false
}

const selectNewUser = (user: User) => {
    users.value.unshift({
        label: `${user.first_name} ${user.last_name}`,
        value: user.id
    })
    model.value = user.id
}

// Refetch quand le roleFilter change
watch(() => props.roleFilter, () => {
    fetchUsers()
}, { immediate: false })

onMounted(() => {
    fetchUsers()
})

</script>
<template>
    <Teleport to="body">
        <UserModal v-if="showModal" v-model="showModal" :user="selectedUser" @submit="selectNewUser" />
    </Teleport>
    <USelectMenu v-model="model" v-model:open="openMenu" v-bind="$attrs" :items="users" :loading="loading"
        value-key="value">
        <template #content-bottom>
            <UButton icon="i-heroicons-plus" color="neutral" label="Ajouter un utilisateur" @click.stop="addNewUser"
                block />
        </template>
    </USelectMenu>
</template>