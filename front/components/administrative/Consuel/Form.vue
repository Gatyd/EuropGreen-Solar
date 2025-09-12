<script setup lang="ts">
const props = defineProps<{ draft: any; form?: any; formId?: string }>()

const active = ref('144a')

const tabsItems = [
    { label: '144A', value: '144a', slot: 'a' },
    { label: '144B', value: '144b', slot: 'b' },
    { label: '144C', value: '144c', slot: 'c' },
    { label: '144C2', value: '144c2', slot: 'c2' }
]

onMounted(() => {
    props.draft.model = 'SC-144A'
})
</script>

<template>
    <div class="space-y-4">
        <UTabs v-model="active" :items="tabsItems">
            <template #a>
                <AdministrativeConsuelFormSC144A v-model="props.draft" />
            </template>
            <template #b>
                <div class="text-gray-500 text-sm">Formulaire 144B à venir…</div>
            </template>
            <template #c>
                <div class="text-gray-500 text-sm">Formulaire 144C à venir…</div>
            </template>
            <template #c2>
                <div class="text-gray-500 text-sm">Formulaire 144C2 à venir…</div>
            </template>
        </UTabs>
    </div>
</template>
