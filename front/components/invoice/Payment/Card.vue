<script setup lang="ts">
import type { Payment } from '~/types/billing'
import { formatPrice } from '~/utils/formatPrice'

const props = defineProps<{ payment: Payment }>()
</script>

<template>
  <div class="border rounded p-3 text-sm flex flex-col gap-1 bg-white/40 dark:bg-gray-900/40">
    <div class="flex justify-between items-start">
      <span class="font-medium">Paiement</span>
      <UBadge color="primary" size="xs">{{ payment.date }}</UBadge>
    </div>
    <div class="flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-600 dark:text-gray-400">
      <span>{{ formatPrice(Number(payment.amount)) }}</span>
      <span v-if="payment.method">Méthode: {{ payment.method }}</span>
      <span v-if="payment.reference">Ref: {{ payment.reference }}</span>
      <span v-if="payment.installment">Echéance liée</span>
    </div>
  </div>
</template>
