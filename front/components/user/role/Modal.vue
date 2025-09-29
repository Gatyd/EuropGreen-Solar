<script setup lang="ts">
import type { Role } from '~/types';

const model = defineModel({
    type: Boolean,
    default: false
})

const props = defineProps<{
    role?: Role | null
}>()

const emit = defineEmits(['created', 'updated'])

const loading = ref(false)
const toast = useToast()

const accessOptions = [
    { label: 'Installations', value: 'installation' },
    { label: 'Offres', value: 'offers' },
    { label: 'Demandes', value: 'requests' },
    { label: 'Démarches administratives', value: 'administrative_procedures' }
]

const state = reactive({
    name: ''
})

const selectedAccessObjects = ref<Array<{ label: string; value: string }>>([])

// Computed pour obtenir les accès sélectionnés sous forme de strings
const selectedAccesses = computed(() => selectedAccessObjects.value.map(item => item.value))

// Initialisation du formulaire quand le modal s'ouvre
watch(model, (isOpen) => {
    if (isOpen) {
        if (props.role) {
            // Mode édition
            state.name = props.role.name
            selectedAccessObjects.value = accessOptions.filter(option => (props.role as any)[option.value])
        } else {
            // Mode création
            state.name = ''
            selectedAccessObjects.value = []
        }
    }
}, { immediate: true })

const validate = (state: any) => {
    const errors: { name: string; message: string }[] = []
    if (!state.name?.trim()) errors.push({ name: 'name', message: 'Nom obligatoire.' })
    else if (state.name.trim().length > 20) errors.push({ name: 'name', message: 'Le nom ne doit pas dépasser 20 caractères.' })
    if (selectedAccesses.value.length === 0) errors.push({ name: 'accesses', message: 'Au moins un accès doit être sélectionné.' })
    return errors
}

const submitForm = async () => {

    loading.value = true

    try {
        const body = {
            name: state.name.trim(),
            installation: selectedAccesses.value.includes('installation'),
            offers: selectedAccesses.value.includes('offers'),
            requests: selectedAccesses.value.includes('requests'),
            administrative_procedures: selectedAccesses.value.includes('administrative_procedures')
        }

        let result: Role | null = null

        if (props.role) {
            // Mode édition
            result = await apiRequest<Role>(
                () => $fetch(`/api/roles/${props.role!.id}/`, {
                    method: 'PATCH',
                    body,
                    credentials: 'include'
                }),
                toast
            )
        } else {
            // Mode création
            result = await apiRequest<Role>(
                () => $fetch('/api/roles/', {
                    method: 'POST',
                    body,
                    credentials: 'include'
                }),
                toast
            )
        }

        if (result) {
            toast.add({
                title: props.role ? 'Rôle modifié' : 'Rôle créé',
                description: props.role
                    ? `Le rôle "${result.name}" a été modifié avec succès.`
                    : `Le rôle "${result.name}" a été créé avec succès.`,
                icon: 'i-heroicons-check-circle',
                color: 'success'
            })

            model.value = false
            emit(props.role ? 'updated' : 'created', result)
        }
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <UModal v-model:open="model" :title="role ? 'Modifier le rôle' : 'Nouveau rôle'"
        :description="role ? 'Modifiez les informations du rôle' : 'Créez un nouveau rôle avec ses accès'">
        <template #body>
            <!-- Formulaire -->
            <UForm :state="state" :validate="validate" @submit="submitForm" class="space-y-4">
                <UFormField name="name" label="Nom du rôle" required>
                    <UInput v-model="state.name" placeholder="Saisissez le nom du rôle" :disabled="loading"
                        autocomplete="off" class="w-full" />
                </UFormField>

                <UFormField name="accesses" label="Accès autorisés" help="Sélectionnez les modules auxquels ce rôle aura accès"
                    required>
                    <USelectMenu multiple v-model="selectedAccessObjects" :items="accessOptions" :disabled="loading"
                        placeholder="Choisissez les accès" class="w-full" />
                </UFormField>

                <!-- Boutons d'action -->
                <div class="flex flex-col sm:flex-row justify-end gap-3 pt-4">
                    <UButton type="button" color="neutral" variant="soft" size="lg" @click="model = false"
                        class="sm:order-1 w-full sm:w-auto" :disabled="loading">
                        Annuler
                    </UButton>

                    <UButton type="submit" color="primary" size="lg" :loading="loading"
                        :icon="role ? 'i-heroicons-pencil-square' : 'i-heroicons-plus'"
                        class="sm:order-2 w-full sm:w-auto"
                        :disabled="loading || !state.name.trim() || selectedAccesses.length === 0">
                        {{ role ? 'Enregistrer' : 'Créer le rôle' }}
                    </UButton>
                </div>
            </UForm>
        </template>
    </UModal>
</template>
