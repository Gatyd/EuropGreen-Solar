<script setup lang="ts">
import type { Invoice, Installment, Payment } from '~/types/billing'
import type { Offer } from '~/types/offers'

const props = defineProps<{ offer: Offer; invoice?: Invoice | null }>()

const emit = defineEmits<{ (e: 'submit'): void }>()

const openInstallmentModal = ref(false)
const openPaymentModal = ref(false)
const installmentsLoading = ref(false)
const paymentsLoading = ref(false)
const toast = useToast()

const installments = ref<Installment[]>([])
const payments = ref<Payment[]>([])

const remaining = computed(() => props.invoice ? parseFloat(props.invoice.balance_due || '0') : 0)

const refresInstallments = async () => {
    installmentsLoading.value = true
    if (!props.invoice) return
    const res = await apiRequest(
        () => $fetch<Installment[]>(`/api/installments/?invoice=${props.invoice?.id}`, { credentials: 'include' }),
        toast
    )
    if (res) installments.value = res.sort((a, b) => a.position - b.position)
    installmentsLoading.value = false
}

const refreshPayments = async () => {
    paymentsLoading.value = true
    if (!props.invoice) return
    const res = await apiRequest(
        () => $fetch<Payment[]>(`/api/payments/?invoice=${props.invoice?.id}`, { credentials: 'include' }),
        toast
    )
    if (res) payments.value = res
    paymentsLoading.value = false
}

watch(() => props.invoice, (inv) => {
    installments.value = inv?.installments ? [...inv.installments].sort((a, b) => a.position - b.position) : []
    payments.value = inv?.payments ? [...inv.payments] : []
}, { immediate: true })

function onInstallmentCreated() {
    openInstallmentModal.value = false
    emit('submit')
}
function onPaymentCreated() {
    openPaymentModal.value = false
    emit('submit')
}
</script>

<template>
    <div class="flex flex-col sm:sticky sm:top-0 gap-4 h-full min-h-[80vh]">
        <!-- Modal création / édition échéance -->
        <InvoiceInstallmentModal v-if="props.invoice" v-model="openInstallmentModal" :invoice-id="props.invoice.id"
            :total="props.invoice.total" :remaining="remaining" @created="onInstallmentCreated" />
        <!-- Modal création paiement -->
        <InvoicePaymentModal v-if="props.invoice" v-model="openPaymentModal" :invoice-id="props.invoice.id"
            :installments="installments" :remaining="remaining" @created="onPaymentCreated" />

        <!-- Échéances -->
        <UCard class="flex-1 min-h-0 flex flex-col">
            <template #header>
                <div class="flex items-center justify-between gap-2">
                    <div class="font-semibold">Échéances</div>
                    <div class="flex items-center gap-2">
                        <UTooltip text="Rafraîchir">
                            <UButton size="xs" variant="ghost" icon="i-heroicons-arrow-path" :loading="installmentsLoading"
                                @click="refresInstallments" />
                        </UTooltip>
                        <UButton size="xs" icon="i-heroicons-plus" @click="openInstallmentModal = true"
                            :disabled="!props.invoice">Ajouter</UButton>
                    </div>
                </div>
            </template>
            <div class="flex-1 min-h-0 overflow-auto divide-y text-xs">
                <div v-if="!installments.length" class="p-3 italic text-gray-500">Aucune échéance définie</div>
                <InvoiceInstallmentCard v-for="i in installments" :key="i.id" :installment="i" />
            </div>
        </UCard>

        <!-- Paiements -->
        <UCard class="flex-1 min-h-0 flex flex-col">
            <template #header>
                <div class="flex items-center justify-between gap-2">
                    <div class="font-semibold">Paiements</div>
                    <div class="flex items-center gap-2">
                        <UTooltip text="Rafraîchir">
                            <UButton size="xs" variant="ghost" icon="i-heroicons-arrow-path" :loading="paymentsLoading"
                                @click="refreshPayments" />
                        </UTooltip>
                        <UButton size="xs" icon="i-heroicons-plus" @click="openPaymentModal = true"
                            :disabled="!props.invoice">Ajouter</UButton>
                    </div>
                </div>
            </template>
            <div class="flex-1 min-h-0 overflow-auto divide-y text-xs">
                <div v-if="!payments.length" class="p-3 italic text-gray-500">Aucun paiement enregistré</div>
                <InvoicePaymentCard v-for="p in payments" :key="p.id" :payment="p" />
            </div>
        </UCard>
    </div>
</template>
