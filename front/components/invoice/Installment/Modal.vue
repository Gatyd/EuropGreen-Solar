<script setup lang="ts">
import type { Installment } from '~/types/billing'

const model = defineModel({ type: Boolean })

const props = defineProps<{ invoiceId: string; total: string; remaining: number; installments?: Installment[]; installment?: Installment | null }>()

const emit = defineEmits<{ (e: 'created', item: Installment): void }>()

const state = reactive<{ label: string; type: 'deposit' | 'balance' | 'milestone'; percentage: number | null; amount: number | null; due_date: string | null; }>(
    { label: '', type: 'milestone', percentage: null, amount: null, due_date: null }
)

const totalNumeric = computed(() => parseFloat(props.total || '0'))
const loading = ref(false)

const updatePercentage = () => {
    if (state.amount && totalNumeric.value > 0) {
        const pct = (state.amount / totalNumeric.value) * 100
        state.percentage = parseFloat(pct.toFixed(2))
    }
}
const updateAmount = () => {
    if (state.percentage && totalNumeric.value > 0) {
        const amt = (state.percentage / 100) * totalNumeric.value
        state.amount = parseFloat(amt.toFixed(2))
    }
}

function resetForm() {
    state.label = ''
    state.type = 'milestone'
    state.percentage = null
    state.amount = null
    state.due_date = null
}

function validate(state: any) {
    const errors: any[] = []
    if (!['deposit', 'balance', 'milestone'].includes(state.type)) errors.push({ name: 'type', message: 'Type invalide' })
    if (!state.label) errors.push({ name: 'label', message: 'Libellé requis' })
    if (state.percentage !== null && (state.percentage <= 0 || state.percentage > 100)) errors.push({ name: 'percentage', message: 'Pourcentage 1-100' })
    if (state.amount !== null && state.amount <= 0) errors.push({ name: 'amount', message: 'Montant > 0 requis' })
    if (state.percentage === null && state.amount === null) errors.push({ name: 'amount', message: 'Indiquez le montant' })
    if (state.amount && state.amount > props.remaining) errors.push({ name: 'amount', message: 'Dépasse le restant dû' })
    return errors
}

async function onSubmit() {
    loading.value = true
    const toast = useToast()
    const body: any = { invoice: props.invoiceId, label: state.label, type: state.type }
    if (state.percentage !== null) body.percentage = state.percentage
    if (state.amount !== null) body.amount = state.amount
    if (state.due_date) body.due_date = state.due_date
    const res = await apiRequest(
        () => $fetch<Installment>('/api/installments/', { method: 'POST', body, credentials: 'include' }),
        toast
    )
    if (res) {
        toast.add({ title: 'Échéance ajoutée', color: 'success' })
        emit('created', res)
        resetForm()
    }
    loading.value = false
}
</script>

<template>
    <UModal v-model:open="model" title="Ajouter une échéance">
        <template #body>
            <UForm :state="state" :validate="validate" @submit="onSubmit" class="space-y-4">
                <div class="grid grid-cols-12 gap-4">
                    <UFormField class="col-span-12 sm:col-span-6" label="Type" name="type" required>
                        <USelect v-model="state.type" :items="[
                            { label: 'Acompte', value: 'deposit' },
                            { label: 'Échéance', value: 'milestone' },
                            { label: 'Solde', value: 'balance' }
                        ]" class="w-full" />
                    </UFormField>
                    <UFormField class="col-span-12 sm:col-span-6" label="Libellé" name="label" required>
                        <UInput v-model="state.label" class="w-full" placeholder="Ex: Acompte 30%" />
                    </UFormField>
                    <UFormField class="col-span-12 sm:col-span-4" label="Montant (€)" name="amount" required
                        :help="`Restant: ${remaining.toFixed(2)}`">
                        <UInput v-model.number="state.amount" @update:model-value="updatePercentage" class="w-full"
                            type="number" step="0.01" min="0" />
                    </UFormField>
                    <UFormField class="col-span-12 sm:col-span-4" label="Pourcentage (%)" name="percentage">
                        <UInput v-model.number="state.percentage" @update:model-value="updateAmount" class="w-full"
                            type="number" step="0.01" min="0" max="100" />
                    </UFormField>
                    <UFormField class="col-span-12 sm:col-span-4" label="Échéance" name="due_date">
                        <UInput v-model="state.due_date" class="w-full" type="date" />
                    </UFormField>
                </div>
                <div class="flex justify-end gap-2">
                    <UButton variant="ghost" type="button" @click="model = false">Annuler</UButton>
                    <UButton type="submit" :loading="loading" color="primary">Enregistrer</UButton>
                </div>
            </UForm>
        </template>
    </UModal>
</template>
