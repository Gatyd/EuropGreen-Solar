<script setup lang="ts">
import type { ProspectRequest, ProspectStatus } from '~/types/requests'

const props = defineProps<{
    title: string
    status: ProspectStatus
    items: ProspectRequest[]
    loading?: boolean
    count?: number
}>()
const emit = defineEmits(['drop', 'open'])

// DnD via HTML5 API
const onDragStart = (event: DragEvent, item: ProspectRequest) => {
    event.dataTransfer?.setData('text/plain', JSON.stringify(item))
}

const onDrop = (event: DragEvent) => {
    event.preventDefault()
    const data = event.dataTransfer?.getData('text/plain')
    if (!data) return
    try {
        const item: ProspectRequest = JSON.parse(data)
        emit('drop', { to: props.status, item })
    } catch (e) {
        // ignore
    }
}

const onDragOver = (event: DragEvent) => {
    event.preventDefault()
}
</script>

<template>
    <div :class="[
        'flex flex-col gap-2 rounded-lg p-2 min-h-40 min-w-[340px] ring-1',
        status === 'new' && 'bg-primary-200 ring-primary-400',
        status === 'followup' && 'bg-warning-200 ring-warning-400',
        status === 'info' && 'bg-secondary-200 ring-secondary-400',
        status === 'in_progress' && 'bg-info-200 ring-info-400',
        status === 'closed' && 'bg-neutral-200 ring-neutral-400'
    ]" @drop="onDrop" @dragover="onDragOver">
        <div class="flex items-center justify-between px-1 py-2">
            <div class="font-semibold">{{ title }}</div>
            <UBadge color="neutral" variant="soft">{{ (count ?? items?.length) ?? 0 }}</UBadge>
        </div>
        <RequestSkeleton v-if="loading" :title="title" />
        <div v-else class="flex flex-col gap-2">
            <div v-for="it in items" :key="it.id" draggable="true" @dragstart="(e: DragEvent) => onDragStart(e, it)">
                <div @click.stop.prevent="emit('open', it)">
                    <RequestCard :item="it" />
                </div>
            </div>
        </div>
    </div>
</template>
