<script setup lang="ts">
import { useAuthStore } from '~/store/auth'
import { storeToRefs } from 'pinia'

const { user } = storeToRefs(useAuthStore())

// État du modal
const showModal = ref(false)

// Fonction pour ouvrir le modal (seulement pour les admins)
const openModal = () => {
    if (user.value?.is_superuser) {
        showModal.value = true
    }
}

// Recharger le calendrier après la soumission d'une tâche
const calendarRef = ref()
const handleTaskCreated = () => {
    showModal.value = false
    if (calendarRef.value?.loadTasks) {
        calendarRef.value.loadTasks()
    }
}
</script>

<template>
    <div>
        <div class="sticky top-0 z-50 bg-white">
            <UDashboardNavbar :title="user?.is_superuser ? 'Calendrier & Planification' : 'Calendrier'"
                class="lg:text-2xl font-semibold" :ui="{ root: 'h-12 lg:h-(--ui-header-height)' }">
                <template #right>
                    <UButton v-if="user?.is_superuser" label="Nouvelle tâche" icon="i-heroicons-plus" color="primary"
                        @click="openModal" />
                </template>
            </UDashboardNavbar>
        </div>

        <PlanningCalendarView ref="calendarRef" />

        <PlanningModal v-model="showModal" @submit="handleTaskCreated" />
    </div>
</template>
