<script setup lang="ts">
import type { Invoice } from '~/types/billing'
import type { Offer } from '~/types/offers'

const model = defineModel({ type: Boolean })

const props = defineProps<{
    offer: Offer
    invoice?: Invoice | null
}>()

const emit = defineEmits<{ (e: 'submit'): void }>()

// état local minimal si besoin ultérieur
</script>

<template>
    <UModal v-model:open="model" title="Gestion de la facture" fullscreen>
        <template #body>
            <div class="flex flex-col xl:flex-row gap-4 p-2 lg:p-4">
                <InvoiceForm class="xl:basis-1/2" :offer="props.offer" :invoice="props.invoice"
                    @submit="emit('submit')" />
                <InvoicePreview class="xl:basis-1/2 shadow-md rounded-lg border border-default bg-white"
                    :offer="props.offer" :invoice="props.invoice || null" />
            </div>
        </template>
    </UModal>
</template>
