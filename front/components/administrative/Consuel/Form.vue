<script setup lang="ts">
const props = defineProps<{ draft: any; form?: any; formId?: string }>()

const active = ref('144A')

watch(active, (v) => {
	// mappe vers la valeur backend attendue
	const map: Record<string, string> = {
		'144A': 'SC-144A',
		'144B': 'SC-144B',
		'144C': 'SC-144C',
		'144C2': 'SC-144C2',
	}
	props.draft.model = map[v] || 'SC-144A'
})

onMounted(() => {
	props.draft.model = 'SC-144A'
})
</script>

<template>
	<div class="space-y-4">
		<UTabs v-model="active" :items="[
			{ label: '144A', slot: 'a' },
			{ label: '144B', slot: 'b' },
			{ label: '144C', slot: 'c' },
			{ label: '144C2', slot: 'c2' },
		]" />

		<div v-show="active==='144A'">
			<AdministrativeConsuelFormSC144A v-model="props.draft" />
		</div>
		<div v-show="active==='144B'">
			<div class="text-gray-500 text-sm">Formulaire 144B à venir…</div>
		</div>
		<div v-show="active==='144C'">
			<div class="text-gray-500 text-sm">Formulaire 144C à venir…</div>
		</div>
		<div v-show="active==='144C2'">
			<div class="text-gray-500 text-sm">Formulaire 144C2 à venir…</div>
		</div>
	</div>
</template>
