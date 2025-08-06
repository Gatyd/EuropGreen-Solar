<script setup lang="ts">
import type { User, UserRoles } from '~/types';

const props = defineProps<{
    modelValue: boolean,
    user?: User | null
}>()
const emit = defineEmits(['update:modelValue', 'submit'])

const loading = ref(false)
const toast = useToast()

const state = reactive({
    last_name: '',
    first_name: '',
    email: '',
    role: '' as UserRoles,
    useraccess: [] as string[]
})

const validate = (state: any) => {
    const errors = []
    if (!state.last_name) errors.push({ name: 'last_name', message: 'Nom obligatoire.' })
    if (!state.first_name) errors.push({ name: 'first_name', message: 'Prénom(s) obligatoire(s).' })
    if (!state.email) errors.push({ name: 'email', message: 'Adresse email obligatoire.' })
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(state.email))
        errors.push({ name: 'email', message: 'Adresse email invalide' })
    if (!state.role) errors.push({ name: 'role', message: 'Rôle obligatoire.' })
    if (state.role !== 'admin' && state.useraccess.length === 0) {
        errors.push({ name: 'useraccess', message: 'Au moins un accès doit être sélectionné.' })
    }
    return errors
}

const roles = [
    { label: 'Administrateur', value: 'admin' },
    { label: 'Employé', value: 'employee' },
    { label: 'Installateur', value: 'installer' },
    { label: 'Sécrétaire', value: 'secretary' }
]

const allAccess = [
    { label: 'Installation', value: 'installation' },
    { label: 'Demandes', value: 'requests' },
    { label: 'Offres', value: 'offers' },
    { label: 'Démarches administratives', value: 'administrative_procedures' }
]

const updateAccess = (role: string) => {
    if (role === 'employee') {
        state.useraccess = ['installation', 'offers', 'requests']
    } else if (role === 'installer') {
        state.useraccess = ['installation']
    } else if (role === 'secretary') {
        state.useraccess = ['installation', 'administrative_procedures']
    } else {
        state.useraccess = []
    }
}

const formatAccess = (selectedAccess: string[]) => {
    const accessObject: Record<string, boolean> = {}
    allAccess.forEach(acces => {
        accessObject[acces.value] = selectedAccess.includes(acces.value)
    })
    return accessObject
}

const formatDataForAPI = () => {
    const data = {
        email: state.email,
        first_name: state.first_name,
        last_name: state.last_name,
        role: state.role,
        useraccess: formatAccess(state.useraccess)
    }

    return data
}

const resetForm = () => {
    state.last_name = ''
    state.first_name = ''
    state.email = ''
    state.role = '' as UserRoles
    state.useraccess = []
}

watch(() => props.user, (newUser) => {
    if (newUser) {
        state.last_name = newUser.last_name || ''
        state.first_name = newUser.first_name || ''
        state.email = newUser.email || ''
        state.role = newUser.role || ''
        state.useraccess = Object.entries(newUser.useraccess || {})
            .filter(([_, value]) => value)
            .map(([key]) => key)
    } else {
        resetForm()
    }
}, { immediate: true })

watch(() => props.modelValue, (newValue) => {
    if (!newValue) {
        resetForm()
    }
})

const closeModal = () => {
    emit('update:modelValue', false)
}

const submit = async () => {
    console.log('Submitting form with state:', state)
    loading.value = true
    const res = await apiRequest<User>(
        () => $fetch(`/api/users/${props.user ? `${props.user.id}/` : ''}`, {
            method: props.user ? "PATCH" : "POST",
            body: formatDataForAPI(),
            credentials: "include"
        }),
        toast
    )
    if (res) {
        toast.add({
            title: `${props.user ? 'Informations de compte modifiés' : 'Invitation envoyée'} avec succès`,
            color: 'success',
            icon: 'i-heroicons-check-circle'
        })
        emit('submit');
        closeModal();
    }
    loading.value = false
}
</script>

<template>
    <UModal :open="modelValue" @update:open="(value: boolean) => emit('update:modelValue', value)"
        :title="props.user ? 'Modification de l\'utilisateur' : 'Invitation d\'un nouvel utilisateur'"
        :ui="{ title: 'text-xl', content: 'max-w-2xl' }" @close="closeModal">
        <template #body>
            <UForm :state="state" :validate="validate" @submit="submit" class="w-full">
                <div class="grid grid-cols-2 gap-6 mb-10">
                    <UFormField label="Nom" name="last_name" required>
                        <UInput v-model="state.last_name" class="w-full" type="text" placeholder="Entrez le nom" />
                    </UFormField>
                    <UFormField label="Prénom" name="first_name" required>
                        <UInput v-model="state.first_name" class="w-full" type="text" placeholder="Entrez le prénom" />
                    </UFormField>
                    <UFormField label="Email" name="email" help="L'invitation sera envoyée à cette adresse email"
                        required>
                        <UInput v-model="state.email" type="email" class="w-full"
                            placeholder="Entrez l'adresse email" />
                    </UFormField>
                    <UFormField label="Rôle" name="role" required>
                        <USelectMenu v-model="state.role" class="w-full" :items="roles" value-key="value"
                            label-key="label" placeholder="Sélectionnez un rôle" @update:model-value="updateAccess" />
                    </UFormField>
                    <UFormField v-if="state.role !== 'admin'" class="col-span-2" label="Accès" name="useraccess">
                        <USelectMenu v-model="state.useraccess" class="w-full" :items="allAccess" value-key="value"
                            label-key="label" placeholder="Sélectionnez les accès" multiple />
                    </UFormField>
                    <UAlert v-else class="col-span-2" title="Accès administrateur" variant="subtle"
                        description="En invitant un administrateur, il aura un accès complet à tous les modules et fonctionnalités, y compris la gestion des utilisateurs et des configurations."
                        icon="i-heroicons-shield-check" :ui="{
                            icon: 'size-11'
                        }" />
                </div>

                <div class="flex justify-center">
                    <UButton type="submit" :loading="loading"
                        :label="user ? 'Modifier l\'utilisateur' : 'Inviter un nouvel utilisateur'" />
                </div>
            </UForm>
        </template>
    </UModal>
</template>