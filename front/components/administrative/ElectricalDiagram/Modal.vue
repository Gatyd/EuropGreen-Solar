<script setup lang="ts">

const props = defineProps<{ formId?: string }>()
const emit = defineEmits<{
    (e: 'submit'): void
}>()

const model = defineModel({ type: Boolean })

const onSubmit = () => {
    emit('submit')
    model.value = false
}

</script>
<template>
    <UModal v-model:open="model" title="Schéma électrique" description="Importation et le stockage du schéma électrique de l'installation.">
        <template #body>
            <AdministrativeElectricalDiagramForm :formId="props.formId" @submit="onSubmit" />
        </template>
    </UModal>
</template>