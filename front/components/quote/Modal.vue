<script setup lang="ts">
const model = defineModel({
    type: Boolean
})
</script>
<template>
    <UModal v-model:open="model" title="Nouveau Devis" fullscreen>
        <template #body>
            
        </template>
    </UModal>
</template>