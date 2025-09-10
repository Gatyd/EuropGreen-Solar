<script setup lang="ts">
import type { Installment, Payment } from '~/types/billing'

const model = defineModel({ type: Boolean })

const props = defineProps<{ invoiceId: string; remaining: number; payment?: Payment | null; installments?: Installment[] }>()

const emit = defineEmits<{ (e: 'created', item: Payment): void }>()

const loading = ref(false)
const paymentMethods = ['Carte bancaire', 'Virement bancaire', 'Chèque', 'Espèces', 'Autre']

const installmentItems = computed(() => (props.installments || []).map((i: any) => ({
    label: i.label || i.name || `Echéance ${i.id}`,
    value: i.id
})))

const state = reactive<{ date: string; amount: number | null; method: string; reference: string; installment: string | null; notes: string }>(
    props.payment ? {
        date: props.payment.date,
        amount: parseFloat(props.payment.amount),
        method: props.payment.method || 'Espèces',
        reference: props.payment.reference || '',
        installment: props.payment.installment || null,
        notes: props.payment.notes || ''
    } : {
        date: new Date().toISOString().slice(0, 10),
        amount: null,
        method: 'Espèces',
        reference: '',
        installment: null,
        notes: ''
    }
)

function validate(state: any) {
    const errors: any[] = []
    if (!state.date) errors.push({ name: 'date', message: 'Date requise' })
    if (state.amount === null || state.amount <= 0) errors.push({ name: 'amount', message: 'Montant > 0 requis' })
    if (state.amount && state.amount > props.remaining) errors.push({ name: 'amount', message: 'Montant dépasse le solde restant' })
    return errors
}

async function onSubmit() {
    loading.value = true
    const toast = useToast()
    const body: any = { invoice: props.invoiceId, date: state.date, amount: state.amount, method: state.method, reference: state.reference }
    if (state.installment) body.installment = state.installment
    const res = await apiRequest(
        () => $fetch<Payment>('/api/payments/', { method: 'POST', body, credentials: 'include' }),
        toast
    )
    if (res) {
        toast.add({ title: 'Paiement ajouté', color: 'success' })
        emit('created', res)
    }
    loading.value = false
}
</script>

<template>
    <UModal v-model:open="model" title="Ajouter un paiement">
        <template #body>
            <UForm :state="state" :validate="validate" @submit="onSubmit" class="space-y-4">
                <div class="grid grid-cols-12 gap-4">
                    <UFormField class="col-span-6 sm:col-span-4" label="Date" name="date" required>
                        <UInput v-model="state.date" class="w-full" type="date" />
                    </UFormField>
                    <UFormField class="col-span-6 sm:col-span-3" label="Montant" name="amount" required>
                        <UInput v-model.number="state.amount" class="w-full" type="number" step="0.01" min="0" />
                    </UFormField>
                    <UFormField class="col-span-12 sm:col-span-5" label="Echéance" name="installment">
                        <USelect v-model="state.installment" :items="installmentItems" value-key="value" class="w-full" />
                    </UFormField>
                    <div class="col-span-12 sm:col-span-6 grid grid-cols-6 gap-2">
                        <UFormField class="col-span-3 sm:col-span-6" label="Méthode de paiement" name="payment_method">
                            <USelect v-model="state.method" :items="paymentMethods" value-key="id" class="w-full" />
                        </UFormField>
                        <UFormField class="col-span-3 sm:col-span-6" label="Référence" name="reference">
                            <UInput v-model="state.reference" class="w-full" />
                        </UFormField>
                    </div>
                    <UFormField class="col-span-12 sm:col-span-6" label="Notes" name="notes">
                        <UTextarea v-model="state.notes" class="w-full" :rows="4" />
                    </UFormField>
                </div>
                <div class="flex justify-end gap-2 pt-2">
                    <UButton variant="ghost" @click="model = false" type="button">Annuler</UButton>
                    <UButton type="submit" :loading="loading" color="primary">Enregistrer</UButton>
                </div>
            </UForm>
        </template>
    </UModal>
</template>
