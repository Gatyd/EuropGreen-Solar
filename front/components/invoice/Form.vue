<script setup lang="ts">
import type { Invoice, Installment, Payment } from '~/types/billing'
import type { Offer } from '~/types/offers'

const props = defineProps<{ offer: Offer; invoice: Invoice | null }>()

const emit = defineEmits<{ (e: 'updated', invoice: Invoice): void }>()

// Placeholders pour les deux cartes (échéances et paiements)
// On ajustera la logique et les appels API dans l'étape suivante.
</script>

<template>
  <div class="flex flex-col gap-4 h-full">
    <UCard class="flex-1 min-h-[40vh]">
      <template #header>
        <div class="font-semibold">Échéances</div>
      </template>
      <div class="h-[calc(50vh-6rem)] overflow-auto text-sm text-gray-600">
        <div class="italic">Configuration des échéances à venir…</div>
      </div>
    </UCard>

    <UCard class="flex-1 min-h-[40vh]">
      <template #header>
        <div class="font-semibold">Paiements</div>
      </template>
      <div class="h-[calc(50vh-6rem)] overflow-auto text-sm text-gray-600">
        <div class="italic">Gestion des paiements à venir…</div>
      </div>
    </UCard>
  </div>
</template>
