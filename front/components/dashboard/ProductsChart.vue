<script setup lang="ts">
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const props = defineProps<{ queryParams: Record<string, string> }>()
const toast = useToast()
const loading = ref(true)
const chartData = ref<any>(null)

async function fetchData() {
    loading.value = true
    const result = await apiRequest<any>(
        () => $fetch('/api/admin-platform/dashboard/products_performance/', {
            credentials: 'include',
            params: props.queryParams
        }),
        toast
    )

    if (result) {
        chartData.value = {
            labels: result.labels,
            datasets: [{
                label: 'CA (€)',
                data: result.revenue,
                backgroundColor: 'rgba(59, 130, 246, 0.8)'
            }]
        }
    }
    loading.value = false
}

watch(() => props.queryParams, fetchData, { deep: true })
onMounted(fetchData)
</script>

<template>
    <UCard v-bind="$attrs">
        <template #header>
            <span class="font-semibold text-sm">Performance Produits</span>
        </template>

        <div v-if="loading" class="h-48 flex items-center justify-center">
            <UIcon name="i-heroicons-arrow-path" class="animate-spin text-2xl text-gray-400" />
        </div>
        <div v-else-if="chartData" class="h-48">
            <Bar :data="chartData"
                :options="{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }" />
        </div>
    </UCard>
</template>
