<script setup lang="ts">
import { Line } from 'vue-chartjs'
import {
    Chart as ChartJS,
    Title,
    Tooltip,
    Legend,
    LineElement,
    CategoryScale,
    LinearScale,
    PointElement
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale, PointElement)

interface RevenueData {
    labels: string[]
    data: number[]
}

const props = defineProps<{
    queryParams: Record<string, string>
}>()

const toast = useToast()
const loading = ref(true)
const chartData = ref<any>(null)

async function fetchData() {
    loading.value = true
    const result = await apiRequest<RevenueData>(
        () => $fetch('/api/admin-platform/dashboard/revenue_chart/', {
            credentials: 'include',
            params: props.queryParams
        }),
        toast
    )

    if (result) {
        chartData.value = {
            labels: result.labels,
            datasets: [{
                label: 'Chiffre d\'affaires (€)',
                data: result.data,
                borderColor: 'rgb(16, 185, 129)',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4,
                // fill: true
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
            text: 'Évolution du CA'
        }
    }
}

watch(() => props.queryParams, fetchData, { deep: true })
onMounted(fetchData)
</script>

<template>
    <UCard v-bind="$attrs">
        <template #header>
            <div class="flex items-center gap-2">
                <UIcon name="i-heroicons-chart-bar-square" class="text-xl text-green-500" />
                <span class="font-semibold">Évolution du Chiffre d'Affaires</span>
            </div>
        </template>

        <div v-if="loading" class="h-64 flex items-center justify-center">
            <UIcon name="i-heroicons-arrow-path" class="animate-spin text-3xl text-gray-400" />
        </div>
        <div v-else-if="chartData" class="h-64">
            <Line :data="chartData" :options="chartOptions" />
        </div>
    </UCard>
</template>
