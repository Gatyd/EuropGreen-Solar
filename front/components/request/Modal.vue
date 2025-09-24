<script setup lang="ts">
import type { ProspectSource, ProspectRequestPayload, ProspectRequest } from '~/types/requests'

const props = defineProps<{ modelValue: boolean; payload?: ProspectRequest | null }>()
const emit = defineEmits(['update:modelValue', 'submit'])

const onSubmit = (form: FormData) => {
	emit('submit', form)
}
</script>

<template>
	<UModal :open="modelValue" @update:open="v => emit('update:modelValue', v)"
		:title="props.payload ? 'Modifier demande' : 'Nouvelle demande'"
		:ui="{ title: 'text-xl', content: 'max-w-2xl' }">
		<template #body>
			<RequestForm :model-value="props.payload ?? null" @submit="onSubmit" />
		</template>
	</UModal>
</template>
