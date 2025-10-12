<script setup lang="ts">
import type { ProspectSource, ProspectRequestPayload, ProspectRequest } from '~/types/requests'

const props = defineProps<{ 
	modelValue: boolean
	payload?: ProspectRequest | null
	title?: string
	description?: string
}>()
const emit = defineEmits(['update:modelValue', 'submit'])

const modalTitle = computed(() => {
	if (props.title) return props.title
	return props.payload ? 'Modifier demande' : 'Nouvelle demande'
})

const onSubmit = (form: FormData) => {
	emit('submit', form)
}
</script>

<template>
	<UModal :open="modelValue" @update:open="v => emit('update:modelValue', v)"
		:title="modalTitle"
		:description="props.description"
		:ui="{ title: 'text-xl', content: 'max-w-4xl' }">
		<template #body>
			<RequestForm :model-value="props.payload ?? null" @submit="onSubmit" />
		</template>
	</UModal>
</template>
