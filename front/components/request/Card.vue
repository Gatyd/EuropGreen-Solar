<script setup lang="ts">
import type { ProspectRequest } from '~/types/requests'
import { useAuthStore } from '~/store/auth'

const props = defineProps<{ item: ProspectRequest }>()
const emit = defineEmits(['convert'])
const auth = useAuthStore()
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
        <div v-if="auth.user?.is_superuser && item.assigned_to" class="mt-2 pt-2 border-t text-xs text-gray-500">
            Chargé d'affaire: {{ item.assigned_to.first_name }} {{ item.assigned_to.last_name }}
        </div>
        <div v-if="item.status === 'closed'" class="mt-2 flex justify-end">
            <UButton size="xs" color="primary" variant="solid" icon="i-heroicons-arrow-right-circle" label="Transformer en offre" @click.stop="emit('convert', item)" />
        </div>
    </UCard>
</template>
