<script setup lang="ts">
import { format, startOfMonth, endOfMonth, eachDayOfInterval, addMonths, subMonths } from 'date-fns';
import { fr } from 'date-fns/locale';

// État du calendrier
const currentDate = ref(new Date());
const tasks = ref<any[]>([]);
const loading = ref(false);
const selectedDay = ref<Date | null>(null);
const hoveredDay = ref<Date | null>(null);

// Modal de détails
const showTaskDetail = ref(false);
const selectedTask = ref<any>(null);

// Ouvrir le modal de détails
const openTaskDetail = (task: any) => {
    selectedTask.value = task;
    showTaskDetail.value = true;
};

// Recharger les tâches et mettre à jour la tâche sélectionnée
const handleTaskUpdated = async () => {
    await loadTasks();
    // Mettre à jour la tâche sélectionnée avec les nouvelles données
    if (selectedTask.value) {
        const updatedTask = tasks.value.find(t => t.id === selectedTask.value.id);
        if (updatedTask) {
            selectedTask.value = updatedTask;
        }
    }
};

// Calculer le mois actuel
const currentMonth = computed(() => format(currentDate.value, 'MMMM yyyy', { locale: fr }));
const monthStart = computed(() => startOfMonth(currentDate.value));
const monthEnd = computed(() => endOfMonth(currentDate.value));

// Générer tous les jours du mois
const daysInMonth = computed(() => {
    const days = eachDayOfInterval({ start: monthStart.value, end: monthEnd.value });

    // Ajouter les jours du mois précédent pour compléter la première semaine
    const firstDayOfWeek = days[0].getDay();
    const daysToAdd = firstDayOfWeek === 0 ? 6 : firstDayOfWeek - 1; // Lundi = 0

    const previousMonthDays = [];
    for (let i = daysToAdd; i > 0; i--) {
        const date = new Date(days[0]);
        date.setDate(date.getDate() - i);
        previousMonthDays.push(date);
    }

    // Ajouter les jours du mois suivant pour compléter la dernière semaine
    const lastDayOfWeek = days[days.length - 1].getDay();
    const daysToAddAtEnd = lastDayOfWeek === 0 ? 0 : 7 - lastDayOfWeek;

    const nextMonthDays = [];
    for (let i = 1; i <= daysToAddAtEnd; i++) {
        const date = new Date(days[days.length - 1]);
        date.setDate(date.getDate() + i);
        nextMonthDays.push(date);
    }

    return [...previousMonthDays, ...days, ...nextMonthDays];
});

// Jours de la semaine
const weekDays = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'];

// Charger les tâches du mois
const loadTasks = async () => {
    loading.value = true;
    try {
        const monthParam = format(currentDate.value, 'yyyy-MM');
        const response = await $fetch(`/api/tasks/?month=${monthParam}`, {
            credentials: 'include',
            headers: useRequestHeaders(['cookie']),
        });
        tasks.value = response as any[];
    } catch (error) {
        console.error('Erreur lors du chargement des tâches:', error);
        useToast().add({
            title: 'Erreur',
            description: 'Impossible de charger les tâches du mois.',
            color: 'error',
            icon: 'i-heroicons-x-circle',
        });
    } finally {
        loading.value = false;
    }
};

// Navigation entre les mois
const previousMonth = () => {
    currentDate.value = subMonths(currentDate.value, 1);
    loadTasks();
};

const nextMonth = () => {
    currentDate.value = addMonths(currentDate.value, 1);
    loadTasks();
};

const goToToday = () => {
    currentDate.value = new Date();
    loadTasks();
};

// Gestionnaires d'événements pour Day
const handleDayClick = (date: Date) => {
    selectedDay.value = selectedDay.value && selectedDay.value.getTime() === date.getTime() ? null : date;
};

const handleDayMouseEnter = (date: Date) => {
    hoveredDay.value = date;
};

const handleDayMouseLeave = () => {
    hoveredDay.value = null;
};

// Charger les tâches au montage
onMounted(() => {
    loadTasks();
});

// Exposer loadTasks pour permettre le rechargement depuis le parent
defineExpose({
    loadTasks
});

// Responsive : détecter la taille de l'écran
const isSmallScreen = ref(false);

onMounted(() => {
    const checkScreenSize = () => {
        isSmallScreen.value = window.innerWidth < 768;
    };
    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);

    onUnmounted(() => {
        window.removeEventListener('resize', checkScreenSize);
    });
});
</script>

<template>
    <div class="w-full p-4 md:p-6">
        <!-- En-tête du calendrier -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-2 md:p-4 mb-2 md:mb-4">
            <div class="flex items-center justify-between flex-wrap gap-4">
                <!-- Navigation mois -->
                <div class="flex items-center gap-2">
                    <UButton icon="i-heroicons-chevron-left" color="neutral" variant="ghost" @click="previousMonth"
                        :disabled="loading" />
                    <h2
                        class="text-lg md:text-xl font-semibold text-gray-900 dark:text-white capitalize min-w-[100px] sm:min-w-[140px] md:min-w-[180px] text-center">
                        {{ currentMonth }}
                    </h2>
                    <UButton icon="i-heroicons-chevron-right" color="neutral" variant="ghost" @click="nextMonth"
                        :disabled="loading" />
                </div>

                <!-- Bouton Aujourd'hui -->
                <UButton label="Aujourd'hui" icon="i-heroicons-calendar" color="primary" variant="soft"
                    @click="goToToday" :disabled="loading" />
            </div>
        </div>

        <!-- Grille du calendrier -->
        <div
            class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
            <!-- Loader -->
            <div v-if="loading" class="p-8 text-center">
                <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin text-primary mx-auto" />
                <p class="mt-2 text-sm text-gray-500">Chargement...</p>
            </div>

            <!-- Calendrier -->
            <div v-else>
                <!-- Jours de la semaine -->
                <div class="grid grid-cols-7 bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
                    <div v-for="day in weekDays" :key="day"
                        class="p-2 md:p-3 text-center text-xs md:text-sm font-semibold text-gray-700 dark:text-gray-300">
                        {{ day }}
                    </div>
                </div>

                <!-- Grille des jours -->
                <div class="grid grid-cols-7 divide-x divide-y divide-gray-200 dark:divide-gray-700">
                    <PlanningCalendarDay v-for="(date, index) in daysInMonth" :key="index" :date="date"
                        :current-date="currentDate" :tasks="tasks" :selected-day="selectedDay" :hovered-day="hoveredDay"
                        :is-small-screen="isSmallScreen" @click="handleDayClick" @mouseenter="handleDayMouseEnter"
                        @mouseleave="handleDayMouseLeave" @open-task="openTaskDetail" />
                </div>
            </div>
        </div>

        <!-- Légende -->
        <div
            class="mt-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
            <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Priorités</h3>
            <div class="flex flex-wrap gap-4">
                <div class="flex items-center gap-2">
                    <span class="text-sm text-gray-600 dark:text-gray-400">🔴 Urgente</span>
                </div>
                <div class="flex items-center gap-2">
                    <span class="text-sm text-gray-600 dark:text-gray-400">🟠 Haute</span>
                </div>
                <div class="flex items-center gap-2">
                    <span class="text-sm text-gray-600 dark:text-gray-400">🔵 Normale</span>
                </div>
                <div class="flex items-center gap-2">
                    <span class="text-sm text-gray-600 dark:text-gray-400">⚪ Basse</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal de détails de la tâche -->
    <PlanningDetailModal v-if="selectedTask" v-model="showTaskDetail" :task="selectedTask" @updated="handleTaskUpdated"
        @deleted="loadTasks" />
</template>
