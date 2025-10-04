<script setup lang="ts">
import { Bar } from 'vue-chartjs'
import {
    Chart as ChartJS,
    Title,
    Tooltip,
    Legend,
    BarElement,
    CategoryScale,
    LinearScale
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

interface FunnelData {
    stages: Array<{
        name: string
        count: number
        percentage: number
    }>
}

const props = defineProps<{
    queryParams: Record<string, string>
}>()

const toast = useToast()
const loading = ref(true)
const chartData = ref<any>(null)

async function fetchData() {
    loading.value = true
    const result = await apiRequest<FunnelData>(
        () => $fetch('/api/admin-platform/dashboard/conversion_funnel/', {
            credentials: 'include',
            params: props.queryParams
        }),
        toast
    )

    if (result) {
        chartData.value = {
            labels: result.stages.map(s => s.name),
            datasets: [{
                label: 'Nombre',
                data: result.stages.map(s => s.count),
                backgroundColor: [
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(139, 92, 246, 0.8)'
                ]
            }]
        }
    }
    loading.value = false
}

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: false
        },
        title: {
            display: true,
            text: 'Funnel de Conversion'
        }
    }
}

watch(() => props.queryParams, fetchData, { deep: true })
onMounted(fetchData)
</script>

<template>
    <UCard>
        <template #header>
            <div class="flex items-center gap-2">
                <UIcon name="i-heroicons-funnel" class="text-xl text-primary-500" />
                <span class="font-semibold">Funnel de Conversion</span>
            </div>
        </template>

        <div v-if="loading" class="h-64 flex items-center justify-center">
            <UIcon name="i-heroicons-arrow-path" class="animate-spin text-3xl text-gray-400" />
        </div>
        <div v-else-if="chartData" class="h-64">
            <Bar :data="chartData" :options="chartOptions" />
        </div>
    </UCard>
</template>
