<script setup lang="ts">
import type { Invoice, Installment, Payment } from '~/types/billing'
import type { Offer } from '~/types/offers'

const props = defineProps<{ offer: Offer; invoice?: Invoice | null }>()

const emit = defineEmits<{ (e: 'refresh'): void }>()

const openInstallmentModal = ref(false)
const openInstallmentDelete = ref(false)
const openPaymentModal = ref(false)
const openPaymentDelete = ref(false)
const loadingRefresh = ref(false)
const toast = useToast()

const installments = ref<Installment[]>([])
const installment = ref<Installment | null>(null)
const payments = ref<Payment[]>([])
const payment = ref<Payment | null>(null)

const remaining = computed(() => props.invoice ? parseFloat(props.invoice.balance_due || '0') : 0)

function sortInstallments(list: Installment[]) {
    return [...list].sort((a, b) => {
        const da = a.due_date || ''
        const db = b.due_date || ''
        return da.localeCompare(db)
    })
}

watch(() => props.invoice, (inv) => {
    installments.value = inv?.installments ? sortInstallments(inv.installments) : []
    payments.value = inv?.payments ? [...inv.payments] : []
}, { immediate: true })

async function refreshInvoice() {
    if (!props.invoice) return
    try {
        loadingRefresh.value = true
        const inv = await apiRequest(
            () => $fetch<Invoice>(`/api/invoices/${props.invoice?.id}/`, { credentials: 'include' }),
            toast
        )
        if (inv) {
            installments.value = inv.installments ? sortInstallments(inv.installments) : []
            payments.value = inv.payments ? [...(inv.payments || [])] : []
            emit('refresh')
        }
    } catch (e: any) {
        toast.add({ title: 'Erreur rafraîchissement', description: e?.message || 'Impossible de rafraîchir la facture', color: 'error' })
    } finally {
        loadingRefresh.value = false
    }
}

function createInstallment() {
    openInstallmentModal.value = true
    installment.value = null
}

function onUpdateInstallment(item: Installment) {
    openInstallmentModal.value = true
    installment.value = item
}

function onDeleteInstallment(item: Installment) {
    openInstallmentDelete.value = true
    installment.value = item
}

function createPayment() {
    openPaymentModal.value = true
    payment.value = null
}

function onUpdatePayment(item: Payment) {
    openPaymentModal.value = true
    payment.value = item
}

function onDeletePayment(item: Payment) {
    openPaymentDelete.value = true
    payment.value = item
}

function onInstallmentCreated() {
    openInstallmentModal.value = false
    refreshInvoice()
}
function onPaymentCreated() {
    openPaymentModal.value = false
    refreshInvoice()
}
</script>

<template>
    <div class="flex flex-col gap-4 h-full min-h-[80vh]">
        <!-- Modal création / édition échéance -->
        <InvoiceInstallmentModal v-if="props.invoice" v-model="openInstallmentModal" :invoice-id="props.invoice.id"
            :total="props.invoice.total" :remaining="remaining" :installments="installments" :installment="installment"
            @created="onInstallmentCreated" />
        <InvoiceInstallmentDelete v-if="installment" v-model="openInstallmentDelete" :installment="installment"
            @submit="refreshInvoice" />
        <!-- Modal création paiement -->
        <InvoicePaymentModal v-if="props.invoice" v-model="openPaymentModal" :invoice-id="props.invoice.id"
            :installments="installments" :remaining="remaining" :payment="payment" @created="onPaymentCreated" />
        <InvoicePaymentDelete v-if="payment" v-model="openPaymentDelete" :payment="payment" @submit="refreshInvoice" />

        <!-- Échéances -->
        <UCard class="flex-1 min-h-0 flex flex-col">
            <template #header>
                <div class="flex items-center justify-between gap-2">
                    <div class="font-semibold">Échéances</div>
                    <div v-if="invoice?.balance_due && parseFloat(invoice.balance_due) > 0"
                        class="flex items-center gap-2">
                        <UTooltip text="Rafraîchir">
                            <UButton size="xs" variant="ghost" icon="i-heroicons-arrow-path" :loading="loadingRefresh"
                                @click="refreshInvoice" />
                        </UTooltip>
                        <UButton size="xs" icon="i-heroicons-plus" @click="createInstallment"
                            :disabled="!props.invoice">Ajouter
                        </UButton>
                    </div>
                </div>
            </template>
            <div class="flex-1 min-h-0 overflow-auto space-y-2 p-3">
                <div v-if="!installments.length" class="italic text-gray-500">Aucune échéance définie</div>
                <InvoiceInstallmentCard v-for="i in installments" :key="i.id" :installment="i"
                    @update="onUpdateInstallment" @delete="onDeleteInstallment" />
            </div>
        </UCard>

        <!-- Paiements -->
        <UCard class="flex-1 min-h-0 flex flex-col">
            <template #header>
                <div class="flex items-center justify-between gap-2">
                    <div class="font-semibold">Paiements</div>
                    <div v-if="invoice?.balance_due && parseFloat(invoice.balance_due) > 0"
                        class="flex items-center gap-2">
                        <UTooltip text="Rafraîchir">
                            <UButton size="xs" variant="ghost" icon="i-heroicons-arrow-path" :loading="loadingRefresh"
                                @click="refreshInvoice" />
                        </UTooltip>
                        <UButton size="xs" icon="i-heroicons-plus" @click="createPayment" :disabled="!props.invoice">
                            Ajouter</UButton>
                    </div>
                </div>
            </template>
            <div class="flex-1 min-h-0 overflow-auto space-y-2 p-3">
                <div v-if="!payments.length" class="p-3 italic text-gray-500">Aucun paiement enregistré</div>
                <InvoicePaymentCard v-for="p in payments" :key="p.id" :payment="p" @update="onUpdatePayment"
                    @delete="onDeletePayment" />
            </div>
        </UCard>
    </div>
</template>
