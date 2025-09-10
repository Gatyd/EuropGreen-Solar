<script setup lang="ts">
import type { Invoice, Installment, Payment } from '~/types/billing'
import type { Offer } from '~/types/offers'
import { formatPrice } from '~/utils/formatPrice'

const props = defineProps<{ offer: Offer; invoice?: Invoice | null }>()

const emit = defineEmits<{ (e: 'updated', invoice: Invoice): void }>()

const openInstallmentModal = ref(false)
const openPaymentModal = ref(false)
const loadingRefresh = ref(false)
const toast = useToast()

const installments = ref<Installment[]>([])
const payments = ref<Payment[]>([])

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
        const inv = await $fetch<Invoice>(`/api/invoices/${props.invoice.id}/`, { credentials: 'include' })
        installments.value = inv.installments ? sortInstallments(inv.installments) : []
        payments.value = inv.payments ? [...(inv.payments || [])] : []
        emit('updated', inv)
    } catch (e: any) {
        toast.add({ title: 'Erreur rafraîchissement', description: e?.message || 'Impossible de rafraîchir la facture', color: 'error' })
    } finally {
        loadingRefresh.value = false
    }
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
        <InvoiceInstallmentModal
            v-if="props.invoice"
            v-model="openInstallmentModal"
            :invoice-id="props.invoice.id"
            :total="props.invoice.total"
            :remaining="remaining"
            :installments="installments"
            @created="onInstallmentCreated"
        />
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
                            <UButton size="xs" variant="ghost" icon="i-heroicons-arrow-path" :loading="loadingRefresh"
                                @click="refreshInvoice" />
                        </UTooltip>
                        <UButton size="xs" icon="i-heroicons-plus" @click="openInstallmentModal = true"
                            :disabled="!props.invoice">Ajouter</UButton>
                    </div>
                </div>
            </template>
            <div class="flex-1 min-h-0 overflow-auto space-y-2 p-3">
                <div v-if="!installments.length" class="italic text-gray-500">Aucune échéance définie</div>
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
                            <UButton size="xs" variant="ghost" icon="i-heroicons-arrow-path" :loading="loadingRefresh"
                                @click="refreshInvoice" />
                        </UTooltip>
                        <UButton size="xs" icon="i-heroicons-plus" @click="openPaymentModal = true"
                            :disabled="!props.invoice">Ajouter</UButton>
                    </div>
                </div>
            </template>
            <div class="flex-1 min-h-0 overflow-auto space-y-2 p-3">
                <div v-if="!payments.length" class="p-3 italic text-gray-500">Aucun paiement enregistré</div>
                <InvoicePaymentCard v-for="p in payments" :key="p.id" :payment="p" />
            </div>
        </UCard>
    </div>
</template>
