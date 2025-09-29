<script setup lang="ts">
import type { Offer } from '~/types/offers'

const props = defineProps<{ modelValue: boolean; offer: Offer }>()
const emit = defineEmits<{ (e: 'update:modelValue', v: boolean): void; (e: 'created'): void }>()

const open = computed({ get: () => props.modelValue, set: v => emit('update:modelValue', v) })
const note = ref('')
const loading = ref(false)

const canSubmit = computed(() => note.value.trim().length > 0)

async function submit() {
    if (!canSubmit.value || loading.value) return
    loading.value = true
    const toast = useToast()
    const res = await apiRequest<any>(
        () => $fetch(`/api/offers/${props.offer.id}/add_note/`, {
            method: 'POST',
            credentials: 'include',
            body: { note: note.value }
        }),
        toast
    )
    if (res) {
        toast.add({ title: 'Note ajoutée', color: 'success', icon: 'i-heroicons-check-circle' })
        emit('created')
        open.value = false
        note.value = ''
    }
    loading.value = false
}
</script>

<template>
    <UModal :open="open" @update:open="v => (open = v)" title="Ajouter une note" :ui="{ content: 'max-w-sm' }">
        <template #body>
            <form class="space-y-4" @submit.prevent="submit">
                <UFormGroup label="Note" required>
                    <UTextarea v-model="note" class="w-full" :rows="6" placeholder="Saisissez votre note..." />
                </UFormGroup>
                <div class="flex justify-end gap-2 mt-5">
                    <UButton variant="subtle" color="neutral" label="Annuler" @click="open = false" />
                    <UButton :disabled="!canSubmit" :loading="loading" color="primary" label="Enregistrer"
                        type="submit" />
                </div>
            </form>
        </template>
    </UModal>
</template>
