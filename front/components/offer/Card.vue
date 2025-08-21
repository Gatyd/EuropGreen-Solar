<script setup lang="ts">
import type { Offer } from '~/types/offers'

const props = defineProps<{ item: Offer }>()
const toast = useToast()
const onMoveToInstallation = () => {
  toast.add({
    title: 'Logique de déplacement vers installation à venir',
    color: 'info',
    icon: 'i-heroicons-information-circle'
  })
}
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
    <div v-if="item.status === 'quote_signed'" class="mt-2 flex justify-end">
      <UButton size="xs" color="primary" variant="solid" icon="i-heroicons-arrow-right-circle" label="Déplacer vers installation" @click.stop="onMoveToInstallation" />
    </div>
  </UCard>
</template>
