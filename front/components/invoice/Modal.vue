<script setup lang="ts">
import type { Invoice } from '~/types/billing'
import type { Offer } from '~/types/offers'

const model = defineModel({ type: Boolean })

const props = defineProps<{
    offer: Offer
    formId?: string
    invoice?: Invoice | null
}>()

const emit = defineEmits<{ (e: 'submit'): void }>()

function openPrint() {
    if (!props.formId) return
    const url = `/print/installation-form/${props.formId}/invoice?auto=1`
    // Ouvre une nouvelle fenêtre contrôlée (meilleur pour impression propre)
    const w = window.open(url, '_blank', 'noopener,width=1024,height=800')
}
</script>

<template>
    <UModal v-model:open="model" title="Gestion de la facture" fullscreen>
        <template #header>
            <div class="flex items-center justify-between w-full pr-2">
                <span class="font-semibold">Gestion de la facture</span>
                <div class="flex items-center gap-2" v-if="props.invoice">
                    <UButton size="sm" icon="i-heroicons-printer" @click="openPrint" color="primary">Imprimer</UButton>
                    <UButton icon="i-lucide-x" @click="model = false" color="neutral" variant="ghost" />
                </div>
            </div>
        </template>
        <template #body>
            <div class="flex flex-col xl:flex-row gap-4 p-2 lg:p-4">
                <InvoiceForm class="xl:basis-1/2" :offer="props.offer" :invoice="props.invoice"
                    @refresh="emit('submit')" />
                <InvoicePreview class="xl:basis-1/2 shadow-md rounded-lg border border-default bg-white"
                    :offer="props.offer" :invoice="props.invoice || null" />
            </div>
        </template>
    </UModal>
</template>
