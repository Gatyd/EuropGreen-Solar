<script setup lang="ts">
import type { InstallationForm, InstallationStatus } from '~/types/installations'

const props = defineProps<{
	title: string
	status: InstallationStatus
	items: InstallationForm[]
	loading?: boolean
	count?: number
}>()
const emit = defineEmits(['open'])

// Palette pensée pour refléter chaque étape
// technical_visit: bleu clair (exploration)
// representation_mandate: indigo (juridique/mandat)
// administrative_validation: amber (attention/validation)
// installation_completed: emerald (réalisé)
// consuel_visit: cyan (contrôle technique)
// enedis_connection: violet (raccordement réseau)
// commissioning: green (mise en service, succès)
const colors: Record<InstallationStatus, { col: string; ring: string }> = {
	technical_visit: { col: 'bg-sky-100', ring: 'ring-sky-300' },
	representation_mandate: { col: 'bg-indigo-100', ring: 'ring-indigo-300' },
	administrative_validation: { col: 'bg-amber-100', ring: 'ring-amber-300' },
	installation_completed: { col: 'bg-emerald-100', ring: 'ring-emerald-300' },
	consuel_visit: { col: 'bg-cyan-100', ring: 'ring-cyan-300' },
	enedis_connection: { col: 'bg-violet-100', ring: 'ring-violet-300' },
	commissioning: { col: 'bg-green-100', ring: 'ring-green-300' },
}

const onOpen = (item: InstallationForm) => {
	emit('open', item)
}

const goToDetails = (item: InstallationForm) => {
	// Redirige vers /home/installations/[id]
	const router = useRouter()
	router.push({ path: `/home/installations/${item.id}` })
}
</script>

<template>
	<div :class="[
			'flex flex-col gap-2 rounded-lg p-2 min-h-40 min-w-[340px] ring-1',
			colors[status].col,
			colors[status].ring
		]">
		<div class="flex items-center justify-between px-1 py-2">
			<div class="font-semibold">{{ title }}</div>
			<UBadge color="neutral" variant="soft">{{ (count ?? items?.length) ?? 0 }}</UBadge>
		</div>
		<div v-if="loading">
			<USkeleton class="h-24 w-full mb-2" v-for="i in 3" :key="i" />
		</div>
		<div v-else class="flex flex-col gap-2">
			<div v-for="it in items" :key="it.id" @click.stop.prevent="goToDetails(it)">
				<InstallationCard :item="it" />
			</div>
		</div>
	</div>
  
</template>
