<script setup lang="ts">
import apiRequest from '~/utils/apiRequest'
import { useAuthStore } from '~/store/auth'

const model = defineModel({ type: Boolean })

const props = defineProps<{
    task: any
}>()

const emit = defineEmits<{
    (e: 'update:modelValue', value: boolean): void
    (e: 'updated'): void
    (e: 'deleted'): void
}>()

const { user } = storeToRefs(useAuthStore())
const toast = useToast()
const loading = ref(false)
const showEditModal = ref(false)
const showDeleteConfirm = ref(false)

// Statut local pour l'utilisateur assigné
const currentStatus = ref(props.task?.status || 'pending')

// Options de statut
const statusOptions = [
    { value: 'pending', label: 'En attente', color: 'neutral' as const },
    { value: 'in_progress', label: 'En cours', color: 'info' as const },
    { value: 'completed', label: 'Terminée', color: 'success' as const },
    { value: 'cancelled', label: 'Annulée', color: 'error' as const },
]

// Vérifier si l'utilisateur est admin
const isAdmin = computed(() => user.value?.is_superuser)

// Vérifier si l'utilisateur est assigné à cette tâche
const isAssignedUser = computed(() => user.value?.id === props.task?.assigned_to)

// Obtenir le label du statut
const getStatusLabel = (status: string) => {
    return statusOptions.find(s => s.value === status)?.label || status
}

// Obtenir la couleur du statut
const getStatusColor = (status: string) => {
    return statusOptions.find(s => s.value === status)?.color || 'neutral'
}

// Obtenir le badge de priorité
const getPriorityDisplay = (priority: string) => {
    const displays: Record<string, { label: string, color: 'error' | 'warning' | 'info' | 'neutral' }> = {
        urgent: { label: 'Urgente', color: 'error' },
        high: { label: 'Haute', color: 'warning' },
        normal: { label: 'Normale', color: 'info' },
        low: { label: 'Basse', color: 'neutral' },
    }
    return displays[priority] || displays.normal
}

// Changer le statut (pour l'utilisateur assigné)
const updateStatus = async (newStatus: string) => {
    loading.value = true
    const res = await apiRequest<any>(
        () => $fetch(`/api/tasks/${props.task.id}/`, {
            method: 'PATCH',
            body: { status: newStatus },
            credentials: 'include'
        }),
        toast
    )

    if (res) {
        toast.add({
            title: 'Statut mis à jour',
            color: 'success',
            icon: 'i-heroicons-check-circle'
        })
        currentStatus.value = newStatus
        emit('updated')
    }
    loading.value = false
}

// Supprimer la tâche (admin uniquement)
const deleteTask = async () => {
    loading.value = true
    const res = await apiRequest<any>(
        () => $fetch(`/api/tasks/${props.task.id}/`, {
            method: 'DELETE',
            credentials: 'include'
        }),
        toast
    )

    if (res !== null) {
        toast.add({
            title: 'Tâche supprimée',
            color: 'success',
            icon: 'i-heroicons-trash'
        })
        showDeleteConfirm.value = false
        emit('deleted')
        emit('update:modelValue', false)
    }
    loading.value = false
}

// Gérer la fermeture du modal d'édition
const handleEditSubmit = () => {
    showEditModal.value = false
    // Recharger les données de la tâche
    emit('updated')
}

// Fermer le modal
const closeModal = () => {
    emit('update:modelValue', false)
}

watch(() => props.task?.status, (newStatus) => {
    if (newStatus) currentStatus.value = newStatus
}, { immediate: true })

// Mettre à jour les données locales quand la tâche change
watch(() => props.task, (newTask) => {
    if (newTask) {
        currentStatus.value = newTask.status || 'pending'
    }
}, { immediate: true, deep: true })
</script>

<template>
    <UModal v-model:open="model" @update:model-value="(v: boolean) => emit('update:modelValue', v)"
        :ui="{ title: 'text-xl', content: 'max-w-3xl' }">
        <template #header>
            <div class="flex items-start justify-between gap-4 w-full">
                <div class="flex-1">
                    <h3 class="text-xl font-semibold text-gray-900 dark:text-white">
                        {{ task.title }}
                    </h3>
                    <div class="flex items-center gap-2 mt-2">
                        <UBadge :label="getPriorityDisplay(task.priority).label"
                            :color="getPriorityDisplay(task.priority).color" size="sm" variant="subtle" />
                        <UBadge :label="getStatusLabel(currentStatus)" :color="getStatusColor(currentStatus)"
                            size="sm" />
                    </div>
                </div>

                <!-- Bouton de fermeture -->
                <UButton icon="i-heroicons-x-mark" color="neutral" variant="ghost" @click="closeModal" />
            </div>
        </template>

        <template #body>
            <div class="space-y-6">
                <!-- Description -->
                <div v-if="task.description">
                    <h4 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Description</h4>
                    <p class="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap">{{ task.description }}</p>
                </div>

                <!-- Informations principales -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <!-- Assigné à -->
                    <div>
                        <h4 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Assigné à</h4>
                        <div class="flex items-center gap-2">
                            <UIcon name="i-heroicons-user" class="w-4 h-4 text-gray-500" />
                            <span class="text-sm text-gray-900 dark:text-white">{{ task.assigned_to_name }}</span>
                        </div>
                    </div>

                    <!-- Créé par -->
                    <div>
                        <h4 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Créé par</h4>
                        <div class="flex items-center gap-2">
                            <UIcon name="i-heroicons-user-circle" class="w-4 h-4 text-gray-500" />
                            <span class="text-sm text-gray-900 dark:text-white">{{ task.assigned_by_name }}</span>
                        </div>
                    </div>

                    <!-- Date d'échéance -->
                    <div>
                        <h4 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Date d'échéance</h4>
                        <div class="flex items-center gap-2">
                            <UIcon name="i-heroicons-calendar" class="w-4 h-4 text-gray-500" />
                            <span class="text-sm text-gray-900 dark:text-white">
                                {{ new Date(task.due_date).toLocaleDateString('fr-FR') }}
                                <span v-if="task.due_time" class="text-gray-500">
                                    à {{ task.due_time.substring(0, 5) }}
                                </span>
                            </span>
                        </div>
                    </div>

                    <!-- Installation liée -->
                    <div v-if="task.related_installation">
                        <h4 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Installation liée</h4>
                        <div class="flex items-center gap-2">
                            <NuxtLink :to="`/home/installations/${task.related_installation}`"
                                class="flex items-center gap-2 text-sm text-primary hover:text-secondary">
                                <UIcon name="i-heroicons-wrench-screwdriver" class="w-4 h-4" />
                                <span>Voir l'installation</span>
                            </NuxtLink>
                        </div>
                    </div>
                </div>

                <!-- Notes -->
                <div v-if="task.notes">
                    <h4 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Notes</h4>
                    <p class="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap">{{ task.notes }}</p>
                </div>

                <!-- Changement de statut pour l'utilisateur assigné (non admin) -->
                <div v-if="isAssignedUser && !isAdmin" class="border-t pt-4">
                    <h4 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Modifier le statut</h4>
                    <div class="flex flex-wrap gap-2">
                        <!-- Logique intelligente : 
                             - Si pending : montrer in_progress et completed
                             - Si in_progress : montrer completed uniquement
                             - Si completed : montrer in_progress (pour rouvrir)
                        -->
                        <template v-if="currentStatus === 'pending'">
                            <UButton label="En cours" color="info" variant="outline" size="sm" :loading="loading"
                                @click="updateStatus('in_progress')" />
                            <UButton label="Terminée" color="success" variant="outline" size="sm" :loading="loading"
                                @click="updateStatus('completed')" />
                        </template>
                        <template v-else-if="currentStatus === 'in_progress'">
                            <UButton label="Terminée" color="success" variant="outline" size="sm" :loading="loading"
                                @click="updateStatus('completed')" />
                        </template>
                        <template v-else-if="currentStatus === 'completed'">
                            <UButton label="Rouvrir (En cours)" color="info" variant="outline" size="sm"
                                :loading="loading" @click="updateStatus('in_progress')" />
                        </template>
                    </div>
                </div>

                <!-- Actions admin en bas -->
                <div v-if="isAdmin" class="flex items-center justify-end gap-2 border-t pt-4">
                    <UButton icon="i-heroicons-pencil" label="Modifier" color="secondary" variant="outline" size="sm"
                        @click="showEditModal = true" />
                    <UButton icon="i-heroicons-trash" label="Supprimer" color="error" variant="outline" size="sm"
                        @click="showDeleteConfirm = true" />
                </div>
            </div>
        </template>
    </UModal>

    <!-- Modal d'édition -->
    <PlanningModal v-if="showEditModal" v-model="showEditModal" :task="task" @submit="handleEditSubmit" />

    <!-- Confirmation de suppression -->
    <UModal v-model:open="showDeleteConfirm" title="Confirmer la suppression"
        :ui="{ content: 'max-w-md', footer: 'justify-end gap-4' }">
        <template #body>
            <p class="text-sm text-gray-600 dark:text-gray-400">
                Êtes-vous sûr de vouloir supprimer la tâche "{{ task.title }}" ?
                Cette action est irréversible.
            </p>
        </template>
        <template #footer>
            <UButton label="Annuler" color="neutral" variant="ghost" @click="showDeleteConfirm = false" />
            <UButton label="Supprimer" variant="soft" color="error" icon="i-heroicons-trash" :loading="loading" @click="deleteTask" />
        </template>
    </UModal>
</template>
