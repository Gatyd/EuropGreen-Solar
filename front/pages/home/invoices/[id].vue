<script setup lang="ts">
import type { Invoice } from '~/types/billing'
import { formatPrice } from '~/utils/formatPrice'

definePageMeta({
    middleware: 'admin'
})

const route = useRoute()
const toast = useToast()
const invoice = ref<Invoice | null>(null)
const loading = ref(false)
const showEditModal = ref(false)

const statusLabels: Record<string, string> = {
    draft: 'Brouillon',
    issued: 'Émise',
    partially_paid: 'Partiellement payée',
    paid: 'Payée',
    cancelled: 'Annulée',
}

const statusColors: Record<string, string> = {
    draft: 'gray',
    issued: 'blue',
    partially_paid: 'orange',
    paid: 'green',
    cancelled: 'red',
}

function getRecipientDisplay(): string {
    if (!invoice.value) return '—'
    const name = invoice.value.custom_recipient_name || ''
    const company = invoice.value.custom_recipient_company || ''
    if (name && company) return `${name} (${company})`
    return name || company || '—'
}

async function fetchInvoice() {
    try {
        loading.value = true
        const res = await $fetch<Invoice>(`/api/invoices/${route.params.id}/`, { credentials: 'include' })
        invoice.value = res
    } catch (e: any) {
        toast.add({ title: 'Erreur', description: 'Impossible de charger la facture', color: 'error' })
        navigateTo('/home/invoices')
    } finally {
        loading.value = false
    }
}

function openEditModal() {
    showEditModal.value = true
}

function onInvoiceUpdated() {
    fetchInvoice()
}

function openPrint() {
    if (!invoice.value) return
    const url = `/print/standalone-invoice/${invoice.value.id}?auto=1`
    window.open(url, '_blank', 'noopener,width=1024,height=800')
}

onMounted(() => {
    fetchInvoice()
})
</script>

<template>
    <div class="p-6 space-y-6">
        <InvoiceStandaloneInvoiceModal v-if="invoice" v-model="showEditModal" :invoice="invoice" @updated="onInvoiceUpdated" />

        <div v-if="loading" class="flex justify-center py-12">
            <UIcon name="i-heroicons-arrow-path" class="animate-spin size-8" />
        </div>

        <template v-else-if="invoice">
            <!-- En-tête -->
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-4">
                    <UButton icon="i-heroicons-arrow-left" variant="ghost" to="/home/invoices" />
                    <div>
                        <h1 class="text-2xl font-bold">Facture {{ invoice.number }}</h1>
                        <p class="text-gray-600">{{ getRecipientDisplay() }}</p>
                    </div>
                </div>
                <div class="flex items-center gap-2">
                    <UBadge :color="(statusColors[invoice.status] as any)" size="lg">
                        {{ statusLabels[invoice.status] }}
                    </UBadge>
                    <UButton v-if="invoice.status === 'draft' || invoice.status === 'issued'" 
                        icon="i-heroicons-pencil" @click="openEditModal">Modifier</UButton>
                    <UButton icon="i-heroicons-printer" @click="openPrint" color="primary">Imprimer</UButton>
                </div>
            </div>

            <!-- Détails facture -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <!-- Informations destinataire -->
                <UCard>
                    <template #header>
                        <h3 class="font-semibold">Destinataire</h3>
                    </template>
                    <div class="space-y-2 text-sm">
                        <div v-if="invoice.custom_recipient_name">
                            <p class="text-gray-600">Nom</p>
                            <p class="font-medium">{{ invoice.custom_recipient_name }}</p>
                        </div>
                        <div v-if="invoice.custom_recipient_company">
                            <p class="text-gray-600">Entreprise</p>
                            <p class="font-medium">{{ invoice.custom_recipient_company }}</p>
                        </div>
                        <div v-if="invoice.custom_recipient_address">
                            <p class="text-gray-600">Adresse</p>
                            <p class="font-medium whitespace-pre-line">{{ invoice.custom_recipient_address }}</p>
                        </div>
                        <div v-if="invoice.custom_recipient_siret">
                            <p class="text-gray-600">SIRET</p>
                            <p class="font-medium">{{ invoice.custom_recipient_siret }}</p>
                        </div>
                    </div>
                </UCard>

                <!-- Informations facture -->
                <UCard>
                    <template #header>
                        <h3 class="font-semibold">Détails facture</h3>
                    </template>
                    <div class="space-y-2 text-sm">
                        <div>
                            <p class="text-gray-600">Date d'émission</p>
                            <p class="font-medium">{{ new Date(invoice.issue_date).toLocaleDateString('fr-FR') }}</p>
                        </div>
                        <div v-if="invoice.due_date">
                            <p class="text-gray-600">Date d'échéance</p>
                            <p class="font-medium">{{ new Date(invoice.due_date).toLocaleDateString('fr-FR') }}</p>
                        </div>
                        <div v-if="invoice.title">
                            <p class="text-gray-600">Titre</p>
                            <p class="font-medium">{{ invoice.title }}</p>
                        </div>
                        <div v-if="invoice.notes">
                            <p class="text-gray-600">Notes</p>
                            <p class="font-medium whitespace-pre-line">{{ invoice.notes }}</p>
                        </div>
                    </div>
                </UCard>

                <!-- Montants -->
                <UCard>
                    <template #header>
                        <h3 class="font-semibold">Montants</h3>
                    </template>
                    <div class="space-y-2 text-sm">
                        <div class="flex justify-between">
                            <span class="text-gray-600">Sous-total HT</span>
                            <span class="font-medium">{{ formatPrice(parseFloat(invoice.subtotal), true) }} €</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-gray-600">TVA ({{ invoice.tax_rate }}%)</span>
                            <span class="font-medium">{{ formatPrice(parseFloat(invoice.subtotal) * parseFloat(invoice.tax_rate) / 100, true) }} €</span>
                        </div>
                        <div class="flex justify-between font-bold text-base border-t pt-2">
                            <span>Total TTC</span>
                            <span>{{ formatPrice(parseFloat(invoice.total), true) }} €</span>
                        </div>
                        <div v-if="invoice.amount_paid && parseFloat(invoice.amount_paid) > 0" 
                            class="flex justify-between text-green-600 border-t pt-2">
                            <span>Montant payé</span>
                            <span class="font-semibold">{{ formatPrice(parseFloat(invoice.amount_paid), true) }} €</span>
                        </div>
                        <div v-if="invoice.balance_due && parseFloat(invoice.balance_due) > 0" 
                            class="flex justify-between text-orange-600 border-t pt-2">
                            <span>Reste à payer</span>
                            <span class="font-semibold">{{ formatPrice(parseFloat(invoice.balance_due), true) }} €</span>
                        </div>
                    </div>
                </UCard>
            </div>

            <!-- Lignes de produits -->
            <UCard>
                <template #header>
                    <h3 class="font-semibold">Lignes de produits/services</h3>
                </template>
                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead>
                            <tr class="border-b">
                                <th class="text-left p-2">Description</th>
                                <th class="text-right p-2">Quantité</th>
                                <th class="text-right p-2">Prix unitaire</th>
                                <th class="text-right p-2">Remise</th>
                                <th class="text-right p-2">Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="line in invoice.lines" :key="line.id" class="border-b last:border-b-0">
                                <td class="p-2">
                                    <p class="font-semibold">{{ line.name }}</p>
                                    <p class="text-xs text-gray-600">{{ line.description }}</p>
                                </td>
                                <td class="text-right p-2">{{ formatPrice(parseFloat(line.quantity)) }}</td>
                                <td class="text-right p-2">{{ formatPrice(parseFloat(line.unit_price), true) }} €</td>
                                <td class="text-right p-2">{{ formatPrice(parseFloat(line.discount_rate)) }}%</td>
                                <td class="text-right p-2 font-semibold">{{ formatPrice(parseFloat(line.line_total), true) }} €</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </UCard>

            <!-- Gestion paiements et échéances - Réutilisation du composant existant -->
            <InvoiceForm :offer="{ id: '', first_name: invoice.custom_recipient_name || '', last_name: '', address: invoice.custom_recipient_address || '' } as any" 
                :invoice="invoice" @refresh="fetchInvoice" />
        </template>
    </div>
</template>
