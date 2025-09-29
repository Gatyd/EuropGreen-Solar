<script setup lang="ts">
import type { User, UserRoles, Role } from '~/types';
import RoleSelect from '~/components/user/role/SelectMenu.vue'

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
    phone_number: '',
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
        errors.push({ name: 'useraccess', message: 'Sélectionnez au moins un accès.' })
    }
    return errors
}

// Nouveau sélecteur de rôles (objet complet)
const selectedRole = ref<Role | null>(null)
const ACCESS_KEYS = ['installation', 'offers', 'requests', 'administrative_procedures'] as const

watch(selectedRole, (val) => {
    if (val) {
        state.role = val.name as UserRoles
        state.useraccess = ACCESS_KEYS.filter(k => (val as any)[k]) as string[]
    } else {
        state.role = '' as UserRoles
        state.useraccess = []
    }
})

const formatAccess = (selectedAccess: string[]) => {
    const accessObject: Record<string, boolean> = {}
    ACCESS_KEYS.forEach(key => {
        accessObject[key] = selectedAccess.includes(key)
    })
    return accessObject
}

// Options pour multisélection accès (libellés utilisateurs)
const accessOptions = [
    { label: 'Installations', value: 'installation' },
    { label: 'Offres', value: 'offers' },
    { label: 'Demandes', value: 'requests' },
    { label: 'Démarches administratives', value: 'administrative_procedures' }
]

const formatDataForAPI = () => {
    const data = {
        email: state.email,
        phone_number: state.phone_number,
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
    state.phone_number = ''
    state.role = '' as UserRoles
    state.useraccess = []
}

watch(() => props.user, (newUser) => {
    if (newUser) {
        state.last_name = newUser.last_name || ''
        state.first_name = newUser.first_name || ''
        state.email = newUser.email || ''
        state.phone_number = newUser.phone_number || ''
        state.role = newUser.role || ''
        state.useraccess = Object.entries(newUser.useraccess || {})
            .filter(([_, value]) => value)
            .map(([key]) => key)
        selectedRole.value = {
            id: 'prefill:' + newUser.role,
            name: newUser.role,
            installation: !!(newUser.useraccess?.installation ?? (newUser.role === 'admin')),
            offers: !!(newUser.useraccess?.offers ?? (newUser.role === 'admin')),
            requests: !!(newUser.useraccess?.requests ?? (newUser.role === 'admin')),
            administrative_procedures: !!(newUser.useraccess?.administrative_procedures ?? (newUser.role === 'admin')),
            created_at: '',
            updated_at: ''
        }
    } else {
        resetForm()
        selectedRole.value = null
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
        emit('submit', res);
        closeModal();
    }
    loading.value = false
}

const formRef = ref<any>(null)
const trySubmit = async () => {
    try {
        if (formRef.value?.validate) {
            const errors = await formRef.value.validate()
            if (Array.isArray(errors) && errors.length) {
                return
            }
        } else {
            const errors = validate(state)
            if (errors.length) return
        }
        await submit()
    } catch (e) {
        // console.error('[UserModal] trySubmit error', e)
    }
}
</script>

<template>
    <UModal :open="modelValue" @update:open="(value: boolean) => emit('update:modelValue', value)"
        :title="props.user ? 'Modification de l\'utilisateur' : 'Invitation d\'un nouvel utilisateur'"
        :ui="{ title: 'text-xl', content: 'max-w-2xl' }" @close="closeModal">
        <template #body>
            <UForm ref="formRef" :state="state" :validate="validate" class="w-full">
                <div class="grid grid-cols-12 gap-6 mb-10">
                    <UFormField class="col-span-12 md:col-span-6" label="Nom" name="last_name" required>
                        <UInput v-model="state.last_name" class="w-full" type="text" placeholder="Entrez le nom" />
                    </UFormField>
                    <UFormField class="col-span-12 md:col-span-6" label="Prénom" name="first_name" required>
                        <UInput v-model="state.first_name" class="w-full" type="text" placeholder="Entrez le prénom" />
                    </UFormField>
                    <UFormField class="col-span-12 md:col-span-6" label="Email" name="email"
                        help="L'invitation sera envoyée à cette adresse email" required>
                        <UInput v-model="state.email" type="email" class="w-full"
                            placeholder="Entrez l'adresse email" />
                    </UFormField>
                    <UFormField class="col-span-12 md:col-span-6" label="Numéro de téléphone" name="phone_number">
                        <UInput v-model="state.phone_number" class="w-full"
                            placeholder="Entrez le numéro de téléphone" />
                    </UFormField>
                    <UFormField class="col-span-12 md:col-span-4" label="Rôle" name="role" required>
                        <RoleSelect v-model="selectedRole" />
                    </UFormField>
                    <UAlert v-if="state.role === 'admin'" class="col-span-12 md:col-span-8" title="Accès administrateur"
                        variant="subtle"
                        description="En invitant un administrateur, il aura un accès complet à tous les modules et fonctionnalités."
                        icon="i-heroicons-shield-check" :ui="{ icon: 'size-11' }" />
                    <UFormField v-else class="col-span-12 md:col-span-8" label="Accès personnalisés" name="useraccess"
                        help="Sélectionnez les accès spécifiques pour cet utilisateur">
                        <USelectMenu v-model="state.useraccess" :items="accessOptions" value-key="value"
                            label-key="label" multiple placeholder="Sélectionnez les accès" class="w-full" />
                    </UFormField>
                </div>

                <div class="flex justify-center">
                    <UButton type="button" :loading="loading" @click="trySubmit"
                        :label="user ? 'Modifier l\'utilisateur' : 'Inviter un nouvel utilisateur'" />
                </div>
            </UForm>
        </template>
    </UModal>
</template>