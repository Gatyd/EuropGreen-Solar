<script setup lang="ts">
import apiRequest from '~/utils/apiRequest'

const props = defineProps<{
    modelValue: boolean
    task?: any | null
}>()

const emit = defineEmits<{
    (e: 'update:modelValue', value: boolean): void
    (e: 'submit'): void
}>()

const loading = ref(false)

const state = reactive({
    title: '',
    description: '',
    assigned_to: '',
    due_date: '',
    due_time: '',
    priority: 'normal',
    related_installation: '',
    notes: ''
})

// Options de priorité
const priorityOptions = [
    { value: 'low', label: '⚪ Basse' },
    { value: 'normal', label: '🔵 Normale' },
    { value: 'high', label: '🟠 Haute' },
    { value: 'urgent', label: '🔴 Urgente' },
]

watch(() => props.task, (v) => {
    if (v) {
        Object.assign(state, v)
    }
}, { immediate: true })

const validate = (st: any) => {
    const errors: any[] = []
    if (!st.title || st.title.trim().length < 3) {
        errors.push({ path: 'title', message: 'Le titre doit contenir au moins 3 caractères.' })
    }
    if (!st.assigned_to) {
        errors.push({ path: 'assigned_to', message: 'Veuillez sélectionner un utilisateur.' })
    }
    if (!st.due_date) {
        errors.push({ path: 'due_date', message: 'La date d\'échéance est requise.' })
    }
    return errors
}

const submit = async () => {
    loading.value = true
    const toast = useToast()

    const endpoint = props.task?.id
        ? `/api/tasks/${props.task.id}/`
        : '/api/tasks/'
    const method = props.task?.id ? 'PATCH' : 'POST'

    const res = await apiRequest<any>(
        () => $fetch(endpoint, { method, body: state, credentials: 'include' }),
        toast
    )

    if (res) {
        toast.add({
            title: props.task?.id ? 'Tâche modifiée avec succès' : 'Tâche créée avec succès',
            color: 'success',
            icon: 'i-heroicons-check-circle'
        })
        emit('submit')
        emit('update:modelValue', false)
    }
    loading.value = false
}
</script>

<template>
    <UModal :open="modelValue" @update:open="v => emit('update:modelValue', v)"
        :title="task?.id ? 'Modifier la tâche' : 'Nouvelle tâche'" :ui="{ title: 'text-xl', content: 'max-w-2xl' }">
        <template #body>
            <UForm :state="state" :validate="validate" @submit="submit" class="grid grid-cols-2 gap-4">
                <!-- Titre -->
                <UFormField label="Titre de la tâche" name="title" required class="col-span-2">
                    <UInput v-model="state.title" placeholder="Ex: Effectuer visite technique" class="w-full" />
                </UFormField>

                <!-- Assigné à -->
                <UFormField label="Assigné à" name="assigned_to" required>
                    <UserSelectMenu :staff-only="true" v-model="state.assigned_to" placeholder="Sélectionner un utilisateur"
                        class="w-full" />
                </UFormField>

                <!-- Priorité -->
                <UFormField label="Priorité" name="priority" required>
                    <USelectMenu v-model="state.priority" :items="priorityOptions" value-key="value" class="w-full" />
                </UFormField>

                <!-- Date d'échéance -->
                <UFormField label="Date d'échéance" name="due_date" required>
                    <UInput v-model="state.due_date" type="date" :min="new Date().toISOString().split('T')[0]"
                        class="w-full" />
                </UFormField>

                <!-- Heure -->
                <UFormField label="Heure (optionnelle)" name="due_time">
                    <UInput v-model="state.due_time" type="time" class="w-full" />
                </UFormField>

                <!-- Installation liée -->
                <UFormField label="Installation liée (optionnelle)" name="related_installation" class="col-span-2">
                    <InstallationSelectMenu v-model="state.related_installation"
                        placeholder="Sélectionner une installation" class="w-full" />
                </UFormField>

                <!-- Description -->
                <UFormField label="Description" name="description">
                    <UTextarea v-model="state.description" placeholder="Détaillez la tâche..." :rows="3"
                        class="w-full" />
                </UFormField>

                <!-- Notes -->
                <UFormField label="Notes additionnelles" name="notes">
                    <UTextarea v-model="state.notes" placeholder="Ajoutez des notes..." :rows="3" class="w-full" />
                </UFormField>

                <div class="col-span-2 flex justify-end mt-2">
                    <UButton type="submit" :loading="loading" color="primary" icon="i-heroicons-check"
                        :label="task?.id ? 'Modifier' : 'Créer la tâche'" />
                </div>
            </UForm>
        </template>
    </UModal>
</template>
