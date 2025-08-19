<script setup lang="ts">
import type { Offer } from '~/types/offers'

const props = defineProps<{ item: Offer }>()
</script>

<template>
  <UCard :ui="{ body: 'p-3' }" class="cursor-grab">
    <div class="font-medium">
      {{ item.last_name }} {{ item.first_name }}
    </div>
    <div class="text-sm text-gray-500">
      {{ item.phone }} • {{ item.email }}
    </div>
    <div class="text-xs text-gray-400 truncate">
      {{ item.address }}
    </div>
  </UCard>
</template>
