<script setup lang="ts">
import type { User } from '~/types'

const props = defineProps<{
    modelValue: boolean
    user: User
}>()

const emit = defineEmits(['update:modelValue', 'submit'])

const toast = useToast()
const loading = ref(false)

const state = reactive({
    type: 'percentage' as 'percentage' | 'value',
    value: 0
})

// Labels des rôles
const roleLabels: Record<string, string> = {
    sales: 'Commercial',
    collaborator: 'Collaborateur',
    customer: 'Client'
}

const roleLabel = computed(() => roleLabels[props.user.role] || props.user.role)

// Validation
const validate = (state: any) => {
    const errors = []
    if (!state.type) errors.push({ name: 'type', message: 'Type de commission obligatoire.' })
    if (state.value === null || state.value === undefined || state.value < 0) {
        errors.push({ name: 'value', message: 'La valeur doit être supérieure ou égale à 0.' })
    }
    if (state.type === 'percentage' && state.value > 100) {
        errors.push({ name: 'value', message: 'Le pourcentage ne peut pas dépasser 100%.' })
    }
    return errors
}

// Options pour le type de commission
const typeOptions = [
    { label: 'Pourcentage (%)', value: 'percentage' },
    { label: 'Montant fixe (€)', value: 'value' }
]

// Réinitialiser le formulaire quand l'utilisateur change
watch(() => props.user, (newUser) => {
    if (newUser) {
        state.type = newUser.commission?.type || 'percentage'
        state.value = newUser.commission?.value || 0
    }
}, { immediate: true })

watch(() => props.modelValue, (newValue) => {
    if (!newValue) {
        // Réinitialiser à la fermeture
        if (props.user) {
            state.type = props.user.commission?.type || 'percentage'
            state.value = props.user.commission?.value || 0
        }
    }
})

const closeModal = () => {
    emit('update:modelValue', false)
}

const submit = async () => {
    loading.value = true

    const res = await apiRequest(
        () => $fetch(`/api/users/${props.user.id}/commission/`, {
            method: props.user.commission ? 'PATCH' : 'POST',
            body: state,
            credentials: 'include'
        }),
        toast
    )

    if (res) {
        toast.add({
            title: 'Commission mise à jour avec succès',
            color: 'success',
            icon: 'i-heroicons-check-circle'
        })
        emit('submit', res)
        closeModal()
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
        // console.error('[CommissionModal] trySubmit error', e)
    }
}
</script>

<template>
    <UModal :open="modelValue" @update:open="(value: boolean) => emit('update:modelValue', value)"
        title="Gérer la commission" :ui="{ title: 'text-xl' }" @close="closeModal">
        <template #body>
            <p class="mb-4 text-sm text-gray-500 dark:text-gray-400">
                {{ user.first_name }} {{ user.last_name }} ({{ roleLabel }})
            </p>

            <UForm ref="formRef" :state="state" :validate="validate" class="w-full">
                <div class="grid grid-cols-12 gap-6 mb-10">
                    <!-- Type de commission -->
                    <UFormField class="col-span-12 md:col-span-6" label="Type de commission" name="type" required>
                        <USelectMenu v-model="state.type" :items="typeOptions" value-key="value" label-key="label"
                            placeholder="Sélectionnez le type" class="w-full" />
                    </UFormField>

                    <!-- Valeur -->
                    <UFormField class="col-span-12 md:col-span-6" label="Valeur" name="value"
                        :help="state.type === 'percentage' ? 'Entre 0 et 100%' : 'Montant fixe en euros'"
                        required>
                        <UInput v-model.number="state.value" type="number" min="0" step="0.01" class="w-full"
                            :placeholder="state.type === 'percentage' ? 'Ex: 15.50' : 'Ex: 500.00'"
                            :trailing-icon="state.type === 'percentage' ? 'i-heroicons-percent-badge' : 'i-heroicons-currency-euro'" />
                    </UFormField>
                </div>

                <div class="flex justify-center">
                    <UButton type="button" :loading="loading" @click="trySubmit" label="Enregistrer la commission" />
                </div>
            </UForm>
        </template>
    </UModal>
</template>
