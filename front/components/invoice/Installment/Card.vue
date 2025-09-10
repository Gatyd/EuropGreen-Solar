<script setup lang="ts">
import type { Installment } from '~/types/billing'
import { formatPrice } from '~/utils/formatPrice'

const props = defineProps<{ installment: Installment }>()
</script>

<template>
  <div class="border rounded p-3 text-sm flex flex-col gap-1 bg-white/40 dark:bg-gray-900/40">
    <div class="flex justify-between items-start">
      <span class="font-medium">{{ installment.label }}</span>
      <UBadge :color="installment.is_paid ? 'success' : 'warning'" size="xs">
        {{ installment.is_paid ? 'Payée' : 'En attente' }}
      </UBadge>
    </div>
    <div class="flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-600 dark:text-gray-400">
      <span v-if="installment.percentage">{{ installment.percentage }}%</span>
      <span v-if="installment.amount">{{ formatPrice(Number(installment.amount)) }}</span>
      <span v-if="installment.due_date">Échéance: {{ installment.due_date }}</span>
      <span>Position: {{ installment.position }}</span>
    </div>
  </div>
</template>
