<script setup lang="ts">
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isToday, isSameDay, addMonths, subMonths } from 'date-fns';
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

// Obtenir les tâches d'un jour spécifique
const getTasksForDay = (date: Date) => {
    return tasks.value.filter(task => {
        const taskDate = new Date(task.due_date);
        return isSameDay(taskDate, date);
    });
};

// Vérifier si un jour a des tâches
const hasTasksOnDay = (date: Date) => {
    return getTasksForDay(date).length > 0;
};

// Obtenir le nombre de tâches par priorité pour un jour
const getTasksByPriority = (date: Date) => {
    const dayTasks = getTasksForDay(date);
    const priorityCounts = {
        urgent: 0,
        high: 0,
        normal: 0,
        low: 0
    };

    dayTasks.forEach(task => {
        if (priorityCounts.hasOwnProperty(task.priority)) {
            priorityCounts[task.priority as keyof typeof priorityCounts]++;
        }
    });

    return priorityCounts;
};

// Obtenir la couleur selon la priorité (pour badges)
const getPriorityColorClass = (priority: string): 'error' | 'warning' | 'info' | 'neutral' => {
    const colors: Record<string, 'error' | 'warning' | 'info' | 'neutral'> = {
        urgent: 'error',
        high: 'warning',
        normal: 'info',
        low: 'neutral',
    };
    return colors[priority] || 'info';
};

// Obtenir l'emoji de priorité (pour le calendrier uniquement)
const getPriorityEmoji = (priority: string) => {
    const emojis: Record<string, string> = {
        urgent: '🔴',
        high: '🟠',
        normal: '🔵',
        low: '⚪',
    };
    return emojis[priority] || emojis.normal;
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

// Gérer le clic sur un jour
const handleDayClick = (date: Date) => {
    if (!isSameMonth(date, currentDate.value)) return;

    selectedDay.value = isSameDay(date, selectedDay.value || new Date('1900-01-01')) ? null : date;
};

// Charger les tâches au montage et lors du changement de mois
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
                    <div v-for="(date, index) in daysInMonth" :key="index"
                        class="relative min-h-[80px] md:min-h-[110px] p-1 md:p-2 cursor-pointer transition-colors"
                        :class="{
                            'bg-gray-50 dark:bg-gray-900/50': !isSameMonth(date, currentDate),
                            'bg-white dark:bg-gray-800': isSameMonth(date, currentDate),
                            'bg-primary-50 dark:bg-primary-900/20': isToday(date),
                            'hover:bg-gray-100 dark:hover:bg-gray-700': isSameMonth(date, currentDate) && !isSmallScreen,
                            'ring-2 ring-primary ring-inset': selectedDay && isSameDay(date, selectedDay),
                        }" @click="handleDayClick(date)" @mouseenter="!isSmallScreen && (hoveredDay = date)"
                        @mouseleave="!isSmallScreen && (hoveredDay = null)">
                        <!-- Numéro du jour -->
                        <div class="flex justify-between mb-1">
                            <span class="text-xs md:text-sm font-medium" :class="{
                                'text-gray-400 dark:text-gray-600': !isSameMonth(date, currentDate),
                                'text-gray-900 dark:text-white': isSameMonth(date, currentDate),
                                'text-primary font-bold': isToday(date),
                            }">
                                {{ format(date, 'd') }}
                            </span>

                            <!-- Indicateur de tâches -->
                            <div v-if="hasTasksOnDay(date) && isSameMonth(date, currentDate)"
                                class="flex flex-col items-end gap-0.5">
                                <!-- Afficher un indicateur par priorité avec son emoji et nombre -->
                                <template v-for="priority in ['urgent', 'high', 'normal', 'low']" :key="priority">
                                    <div v-if="getTasksByPriority(date)[priority as 'urgent' | 'high' | 'normal' | 'low'] > 0"
                                        class="flex items-center gap-1 text-[10px] md:text-xs">
                                        <span>{{ getPriorityEmoji(priority) }}</span>
                                        <span class="font-medium text-gray-700 dark:text-gray-300">
                                            {{ getTasksByPriority(date)[priority as 'urgent' | 'high' | 'normal' | 'low'] }}
                                        </span>
                                    </div>
                                </template>
                            </div>
                        </div>

                        <!-- Aperçu des tâches sur hover (desktop) ou clic (mobile) -->
                        <div v-if="hasTasksOnDay(date) && isSameMonth(date, currentDate) &&
                            ((isSmallScreen && selectedDay && isSameDay(date, selectedDay)) ||
                                (!isSmallScreen && hoveredDay && isSameDay(date, hoveredDay)))"
                            class="absolute left-0 top-full mt-1 z-20 w-64 md:w-80 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 p-3 max-h-96 overflow-y-auto">
                            <div class="space-y-2">
                                <div v-for="task in getTasksForDay(date)" :key="task.id"
                                    class="p-2 bg-gray-50 dark:bg-gray-900 rounded-md cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                                    @click.stop="openTaskDetail(task)">
                                    <div class="flex items-start justify-between gap-2 mb-1">
                                        <h4 class="text-sm font-semibold text-gray-900 dark:text-white flex-1">
                                            {{ task.title }}
                                        </h4>
                                        <UBadge 
                                            :label="task.priority === 'urgent' ? 'Urgente' : task.priority === 'high' ? 'Haute' : task.priority === 'low' ? 'Basse' : 'Normale'"
                                            :color="getPriorityColorClass(task.priority)"
                                            size="xs"
                                            variant="subtle" />
                                    </div>
                                    <p v-if="task.description"
                                        class="text-xs text-gray-600 dark:text-gray-400 mb-1 line-clamp-2">
                                        {{ task.description }}
                                    </p>
                                    <div class="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                                        <UIcon name="i-heroicons-user" class="w-3 h-3" />
                                        <span>{{ task.assigned_to_name }}</span>
                                        <span v-if="task.due_time" class="flex items-center gap-1">
                                            <UIcon name="i-heroicons-clock" class="w-3 h-3" />
                                            {{ task.due_time.substring(0, 5) }}
                                        </span>
                                    </div>
                                    <div class="mt-1">
                                        <UBadge
                                            :label="task.status === 'pending' ? 'En attente' : task.status === 'in_progress' ? 'En cours' : task.status === 'completed' ? 'Terminée' : 'Annulée'"
                                            :color="(task.status === 'completed' ? 'success' : task.status === 'in_progress' ? 'info' : task.status === 'cancelled' ? 'error' : 'neutral')"
                                            size="xs" />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
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
    <PlanningTaskDetailModal v-if="selectedTask" v-model="showTaskDetail" :task="selectedTask" @updated="handleTaskUpdated"
        @deleted="loadTasks" />
</template>

<style scoped>
.line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
</style>
