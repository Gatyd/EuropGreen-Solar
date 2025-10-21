<script setup lang="ts">
import { format, isSameMonth, isToday, isSameDay } from 'date-fns';
import { useAuthStore } from '~/store/auth';

const props = defineProps<{
    date: Date
    currentDate: Date
    tasks: any[]
    selectedDay: Date | null
    hoveredDay: Date | null
    isSmallScreen: boolean
}>()
const auth = useAuthStore();
const emit = defineEmits<{
    (e: 'click', date: Date): void
    (e: 'mouseenter', date: Date): void
    (e: 'mouseleave'): void
    (e: 'openTask', task: any): void
    (e: 'createTask', date: Date): void
}>()

// Contrôle de l'état du popover (pour mobile)
const popoverOpen = ref(false);

// Obtenir les tâches du jour
const dayTasks = computed(() => {
    return props.tasks.filter(task => {
        const taskDate = new Date(task.due_date);
        return isSameDay(taskDate, props.date);
    });
});

// Vérifier si le jour a des tâches
const hasTasks = computed(() => dayTasks.value.length > 0);

// Obtenir le nombre de tâches par priorité
const tasksByPriority = computed(() => {
    const priorityCounts = {
        urgent: 0,
        high: 0,
        normal: 0,
        low: 0
    };

    dayTasks.value.forEach(task => {
        if (priorityCounts.hasOwnProperty(task.priority)) {
            priorityCounts[task.priority as keyof typeof priorityCounts]++;
        }
    });

    return priorityCounts;
});

// Obtenir la couleur selon la priorité
const getPriorityColorClass = (priority: string): 'error' | 'warning' | 'info' | 'neutral' => {
    const colors: Record<string, 'error' | 'warning' | 'info' | 'neutral'> = {
        urgent: 'error',
        high: 'warning',
        normal: 'info',
        low: 'neutral',
    };
    return colors[priority] || 'info';
};

// Obtenir l'emoji de priorité
const getPriorityEmoji = (priority: string) => {
    const emojis: Record<string, string> = {
        urgent: '🔴',
        high: '🟠',
        normal: '🔵',
        low: '⚪',
    };
    return emojis[priority] || emojis.normal;
};

// Configuration du popover selon le type d'écran
const popoverMode = computed(() => props.isSmallScreen ? 'click' : 'hover');

// Configuration du contenu du popover pour gestion automatique du positionnement
const popoverContentConfig = computed(() => ({
    side: 'bottom' as const,
    align: 'start' as const,
    sideOffset: 8,
    collisionPadding: 8
}));

// Classes CSS pour le jour
const dayClasses = computed(() => ({
    'bg-gray-50': !isSameMonth(props.date, props.currentDate),
    'bg-white': isSameMonth(props.date, props.currentDate),
    'bg-primary-50': isToday(props.date),
    'hover:bg-gray-100': isSameMonth(props.date, props.currentDate) && !props.isSmallScreen,
    'ring-2 ring-primary ring-inset': props.selectedDay && isSameDay(props.date, props.selectedDay),
}));

// Classes CSS pour le numéro du jour
const dayNumberClasses = computed(() => ({
    'text-gray-400': !isSameMonth(props.date, props.currentDate),
    'text-gray-900': isSameMonth(props.date, props.currentDate),
    'text-primary font-bold': isToday(props.date),
}));

// Gestionnaires d'événements
const handleClick = () => {
    // Si le jour n'a pas de tâches et est dans le mois actuel, ouvrir le modal de création
    if (!hasTasks.value && isSameMonth(props.date, props.currentDate)) {
        emit('createTask', props.date)
        popoverOpen.value = false;
    } else {
        emit('click', props.date)
        // Ouvrir le popover si on a des tâches
        if (hasTasks.value) {
            popoverOpen.value = true;
        }
    }
};
const handleMouseEnter = () => !props.isSmallScreen && emit('mouseenter', props.date);
const handleMouseLeave = () => !props.isSmallScreen && emit('mouseleave');
const handleTaskClick = (task: any) => {
    emit('openTask', task);
    popoverOpen.value = false;
};
const handleCreateTask = () => {
    emit('createTask', props.date);
    popoverOpen.value = false;
};
</script>

<template>
    <UPopover v-if="hasTasks && isSameMonth(date, currentDate)" v-model:open="popoverOpen" :mode="popoverMode"
        :content="popoverContentConfig">
        <!-- Trigger : le jour du calendrier -->
        <div class="relative min-h-[80px] md:min-h-[110px] p-1 md:p-2 cursor-pointer transition-colors"
            :class="dayClasses" @click="handleClick" @mouseenter="handleMouseEnter" @mouseleave="handleMouseLeave">
            <!-- Numéro du jour -->
            <div class="flex justify-between mb-1">
                <span class="text-xs md:text-sm font-medium" :class="dayNumberClasses">
                    {{ format(date, 'd') }}
                </span>

                <!-- Indicateur de tâches -->
                <div class="flex flex-col items-end gap-0.5">
                    <!-- Afficher un indicateur par priorité avec son emoji et nombre -->
                    <template v-for="priority in ['urgent', 'high', 'normal', 'low']" :key="priority">
                        <div v-if="tasksByPriority[priority as 'urgent' | 'high' | 'normal' | 'low'] > 0"
                            class="flex items-center gap-1 text-[10px] md:text-xs">
                            <span>{{ getPriorityEmoji(priority) }}</span>
                            <span class="font-medium text-gray-700">
                                {{ tasksByPriority[priority as 'urgent' | 'high' | 'normal' | 'low'] }}
                            </span>
                        </div>
                    </template>
                </div>
            </div>
        </div>

        <!-- Content : aperçu des tâches -->
        <template #content>
            <div class="w-64 md:w-80 bg-white rounded-lg shadow-md">
                <!-- Bouton Nouvelle tâche en haut -->
                <div v-if="auth.user?.is_superuser" class="p-2 border-b border-gray-200">
                    <UButton label="Nouvelle tâche" icon="i-heroicons-plus" color="primary" size="xs" block
                        @click.stop="handleCreateTask" />
                </div>

                <!-- Zone scrollable pour les tâches -->
                <div class="overflow-y-auto max-h-[250px] pb-1 md:max-h-[300px]">
                    <div class="space-y-2 p-3 pb-3">
                        <div v-for="task in dayTasks" :key="task.id"
                            class="p-2 bg-gray-100 rounded-md cursor-pointer hover:bg-gray-200 transition-colors"
                            @click.stop="handleTaskClick(task)">
                            <div class="flex items-start justify-between gap-2 mb-1">
                                <h4 class="text-sm font-semibold text-gray-900 flex-1">
                                    {{ task.title }}
                                </h4>
                                <UBadge
                                    :label="task.priority === 'urgent' ? 'Urgente' : task.priority === 'high' ? 'Haute' : task.priority === 'low' ? 'Basse' : 'Normale'"
                                    :color="getPriorityColorClass(task.priority)" size="xs" variant="subtle" />
                            </div>
                            <p v-if="task.description" class="text-xs text-gray-600 mb-1 line-clamp-2">
                                {{ task.description }}
                            </p>
                            <div class="flex items-center gap-2 text-xs text-gray-500">
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
        </template>
    </UPopover>

    <!-- Jour sans tâches : affichage simple -->
    <div v-else class="relative min-h-[80px] md:min-h-[110px] p-1 md:p-2 cursor-pointer transition-colors"
        :class="dayClasses" @click="handleClick" @mouseenter="handleMouseEnter" @mouseleave="handleMouseLeave">
        <!-- Numéro du jour -->
        <div class="flex justify-between mb-1">
            <span class="text-xs md:text-sm font-medium" :class="dayNumberClasses">
                {{ format(date, 'd') }}
            </span>
        </div>
    </div>
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
