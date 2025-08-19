<script setup lang="ts">
import type { Offer, OfferStatus } from '~/types/offers'

const props = defineProps<{
  title: string
  status: OfferStatus
  items: Offer[]
  loading?: boolean
  count?: number
}>()
const emit = defineEmits(['drop', 'open'])

const onDragStart = (event: DragEvent, item: Offer) => {
  event.dataTransfer?.setData('text/plain', JSON.stringify(item))
}

const onDrop = (event: DragEvent) => {
  event.preventDefault()
  const data = event.dataTransfer?.getData('text/plain')
  if (!data) return
  try {
    const item: Offer = JSON.parse(data)
    emit('drop', { to: props.status, item })
  } catch {}
}

const onDragOver = (event: DragEvent) => {
  event.preventDefault()
}
</script>

<template>
  <div :class="[
    'flex flex-col gap-2 rounded-lg p-2 min-h-40 min-w-[340px] ring-1',
    status === 'to_contact' && 'bg-primary-200 ring-primary-400',
    status === 'phone_meeting' && 'bg-warning-200 ring-warning-400',
    status === 'meeting' && 'bg-secondary-200 ring-secondary-400',
    status === 'quote_sent' && 'bg-info-200 ring-info-400',
    status === 'negotiation' && 'bg-amber-200 ring-amber-400',
    status === 'quote_signed' && 'bg-emerald-200 ring-emerald-400'
  ]" @drop="onDrop" @dragover="onDragOver">
    <div class="flex items-center justify-between px-1 py-2">
      <div class="font-semibold">{{ title }}</div>
      <UBadge color="neutral" variant="soft">{{ (count ?? items?.length) ?? 0 }}</UBadge>
    </div>
    <RequestSkeleton v-if="loading" :title="title" />
    <div v-else class="flex flex-col gap-2">
      <div v-for="it in items" :key="it.id" draggable="true" @dragstart="(e: DragEvent) => onDragStart(e, it)">
        <div @click.stop.prevent="emit('open', it)">
          <OfferCard :item="it" />
        </div>
      </div>
    </div>
  </div>
</template>
