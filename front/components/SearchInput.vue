<script lang="ts" setup>

const model = defineModel({
    type: String,
    default: ''
})
defineProps<{ placeholder?: string }>()
const inputRef = ref();

onMounted(() => {
    const inputEl = inputRef.value?.$el?.querySelector('input');
    defineShortcuts({
        "/": () => {
            if (inputEl) {
                inputEl.focus();
            } else {
                console.warn("Impossible de récupérer l'élément input.");
            }
        },
        escape: () => {
            if (inputEl) {
                model.value = "";
            } else {
                console.warn("Impossible de récupérer l'élément input.");
            }
        }
    });
})
</script>
<template>
    <UInput ref="inputRef" v-model="model" icon="i-heroicons-magnifying-glass" autocomplete="off"
        :placeholder="placeholder || 'Rechercher...'" class="" @keydown.esc="$event.target.blur()">
        <template #trailing>
            <UKbd value="/" />
        </template>
    </UInput>
</template>