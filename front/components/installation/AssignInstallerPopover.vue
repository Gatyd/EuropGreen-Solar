<script setup lang="ts">
import SelectMenu from '~/components/user/SelectMenu.vue'

const props = defineProps<{ formId: string }>()
const open = defineModel('open', { type: Boolean, default: false })
const emit = defineEmits<{ (e: 'assigned'): void }>()

const installerId = ref<string | undefined>(undefined)
const loading = ref(false)
const toast = useToast()

const assign = async () => {
    if (!installerId.value) return
    loading.value = true
    const ok = await apiRequest(
        () => $fetch(`/api/installations/forms/${props.formId}/assign-installer/`, {
            method: 'POST',
            credentials: 'include',
            body: { installer_id: installerId.value }
        }),
        toast
    )
    loading.value = false
    if (ok !== null) {
        // Fermer le popover et notifier le parent
        open.value = false
        toast.add({
            title: 'Installateur assigné avec succès',
            color: 'success'
        })
        emit('assigned')
    }
}
</script>

<template>
    <UPopover v-model:open="open" :delay-duration="0" :content="{ side: 'right', align: 'start' }" :ui="{ content: 'p-4 w-80' }">
        <UTooltip text="Assigner un installateur">
            <UButton icon="i-heroicons-user-plus" color="neutral" variant="ghost" aria-label="Assigner un installateur" />
        </UTooltip>

        <template #content>
            <UFormField label="Sélectionner un installateur">
                <SelectMenu v-model="installerId" :placeholder="'Rechercher ou ajouter'" class="w-full" />
            </UFormField>
            <div class="mt-3 flex justify-end">
                <UButton :disabled="!installerId" :loading="loading" icon="i-heroicons-user-plus" label="Affecter"
                    @click="assign" />
            </div>
        </template>
    </UPopover>
</template>