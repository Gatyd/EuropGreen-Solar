<script setup lang="ts">
defineProps<{ title?: string }>()
</script>

<template>
    <div class="flex flex-col gap-2 bg-gray-50 rounded-lg p-2 min-h-40 min-w-[340px] ring-1 ring-gray-200">
        <div class="flex items-center justify-between px-1 py-2">
            <div class="font-semibold text-gray-400">{{ title || 'Chargement…' }}</div>
            <UBadge color="neutral" variant="soft">0</UBadge>
        </div>
        <div class="flex flex-col gap-2">
            <UCard :ui="{ body: 'p-3' }">
                <USkeleton class="h-4 w-3/5 mb-2" />
                <USkeleton class="h-3 w-2/5 mb-2" />
                <USkeleton class="h-3 w-4/5" />
            </UCard>
            <UCard :ui="{ body: 'p-3' }">
                <USkeleton class="h-4 w-2/5 mb-2" />
                <USkeleton class="h-3 w-1/3 mb-2" />
                <USkeleton class="h-3 w-3/4" />
            </UCard>
            <UCard :ui="{ body: 'p-3' }">
                <USkeleton class="h-4 w-1/2 mb-2" />
                <USkeleton class="h-3 w-1/4 mb-2" />
                <USkeleton class="h-3 w-2/3" />
            </UCard>
        </div>
    </div>
</template>

<style scoped></style>
