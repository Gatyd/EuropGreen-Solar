<script setup lang="ts">
import type { Offer } from '~/types/offers'

const props = defineProps<{
    modelValue: boolean
    offer: Offer
}>()
const emit = defineEmits<{
    (e: 'update:modelValue', v: boolean): void
    (e: 'add-note'): void
}>()

const open = computed({
    get: () => props.modelValue,
    set: v => emit('update:modelValue', v)
})

const notesSorted = computed(() => {
    const arr = (props.offer.notes || []).slice()
    return arr.sort((a, b) => a.date.localeCompare(b.date))
})
</script>

<template>
    <UModal :open="open" @update:open="v => (open = v)" title="Notes de l'offre" :ui="{ content: 'max-w-2xl' }">
        <template #body>
            <div class="space-y-4">
                <div class="flex justify-between items-center gap-3">
                    <h3 class="text-sm font-semibold">Chronologie</h3>
                    <UButton size="xs" color="primary" icon="i-heroicons-plus" label="Ajouter une note"
                        @click="emit('add-note')" />
                </div>
                <div v-if="notesSorted.length" class="space-y-3 max-h-[50vh] overflow-y-auto pr-2">
                    <div v-for="(n, i) in notesSorted" :key="i"
                        class="rounded-md border border-gray-200 dark:border-gray-700 p-2 bg-gray-50 dark:bg-gray-800/40">
                        <div class="flex items-center justify-between mb-1">
                            <span class="text-[11px] uppercase tracking-wide text-gray-500 font-medium">{{ new
                                Date(n.date).toLocaleString() }}</span>
                            <UBadge size="xs" variant="subtle" color="neutral">#{{ i + 1 }}</UBadge>
                        </div>
                        <p class="text-xs whitespace-pre-wrap leading-snug text-gray-700 dark:text-gray-200">{{ n.note
                            }}</p>
                    </div>
                </div>
                <div v-else class="text-sm text-gray-500">Aucune note pour l'instant.</div>
            </div>
        </template>
    </UModal>
</template>
