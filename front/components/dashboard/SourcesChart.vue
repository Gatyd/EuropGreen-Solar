<script setup lang="ts">
import { Pie } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, ArcElement)

const props = defineProps<{ queryParams: Record<string, string> }>()
const toast = useToast()
const loading = ref(true)
const chartData = ref<any>(null)

async function fetchData() {
    loading.value = true
    const result = await apiRequest<any>(
        () => $fetch('/api/admin-platform/dashboard/sources_breakdown/', {
            credentials: 'include',
            params: props.queryParams
        }),
        toast
    )

    if (result) {
        chartData.value = {
            labels: result.labels,
            datasets: [{
                data: result.data,
                backgroundColor: [
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(139, 92, 246, 0.8)',
                    'rgba(236, 72, 153, 0.8)'
                ]
            }]
        }
    }
    loading.value = false
}

watch(() => props.queryParams, fetchData, { deep: true })
onMounted(fetchData)
</script>

<template>
    <UCard>
        <template #header>
            <span class="font-semibold text-sm">Sources des Prospects</span>
        </template>

        <div v-if="loading" class="h-48 flex items-center justify-center">
            <UIcon name="i-heroicons-arrow-path" class="animate-spin text-2xl text-gray-400" />
        </div>
        <div v-else-if="chartData" class="h-48">
            <Pie :data="chartData" :options="{ responsive: true, maintainAspectRatio: false }" />
        </div>
    </UCard>
</template>
