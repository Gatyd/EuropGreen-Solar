<script setup lang="ts">
import type { InstallationForm } from '~/types/installations'

const model = defineModel({ type: Boolean })

const props = defineProps<{
	form?: InstallationForm | null
	formId?: string
}>()

const emit = defineEmits<{ (e: 'submit'): void }>()

// Brouillon minimal; le contenu précis sera géré par les sous-formulaires
const draft = reactive<any>({
	model: 'SC-144A',
	y_offset_mm: 8,
})

const onSubmit = () => {
	emit('submit')
	model.value = false
}
</script>

<template>
	<UModal v-model:open="model" title="Consuel" fullscreen>
		<template #body>
			<div class="flex flex-col xl:flex-row gap-4 h-full overflow-hidden">
				<!-- Colonne formulaire -->
				<div class="xl:basis-1/2 min-h-0 overflow-auto">
					<AdministrativeConsuelForm class="w-full" :draft="draft" :form="props.form" :form-id="props.formId" @submit="onSubmit" />
				</div>

				<!-- Colonne aperçu -->
				<div class="xl:basis-1/2 min-h-0 overflow-auto">
					<AdministrativeConsuelPreview mode="edit" :draft="draft" />
				</div>
			</div>
		</template>
	</UModal>
  
</template>
