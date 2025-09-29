<script setup lang="ts">
import { useAuthStore } from '~/store/auth';
import type { InstallationForm } from '~/types/installations'

const props = defineProps<{ item: InstallationForm }>()
const auth = useAuthStore()
</script>

<template>
	<UCard :ui="{ body: 'p-3 sm:p-4' }" class="cursor-pointer">
		<div v-if="auth.user?.is_staff" class="font-medium">
			{{ item.client?.last_name }} {{ item.client?.first_name }}
		</div>
		<div class="text-sm text-gray-500">
			Puissance: {{ item.installation_power }} kWc • {{ item.installation_type }}
		</div>
		<div class="text-xs text-gray-400 truncate">
			{{ item.client_address }}
		</div>
		<div class="mt-2 flex justify-between items-center text-xs text-gray-500">
			<span>Créée le {{ new Date(item.created_at).toLocaleDateString('fr-FR', { dateStyle: 'medium' }) }}</span>
			<!-- <UBadge size="xs" color="neutral" variant="soft">{{ item.status }}</UBadge> -->
		</div>
	</UCard>
</template>
