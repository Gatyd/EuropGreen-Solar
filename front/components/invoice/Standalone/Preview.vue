<script setup lang="ts">
import type { Invoice } from '~/types/billing'
import { formatPrice } from '~/utils/formatPrice'

const props = defineProps<{
    draft: {
        custom_recipient_name: string
        custom_recipient_company: string
        custom_recipient_address: string
        custom_recipient_siret: string
        title: string
        notes: string
        tax_rate: number
        lines: Array<{
            productId: string
            name: string
            description: string
            unit_price: number
            cost_price?: number
            product_type?: string
            quantity: number
            discount_rate: number
        }>
    }
    invoice?: Invoice | null
}>()

const company = {
    name: "Europ'Green Solar",
    address1: '18 rue de Berlin',
    zipCity: '68000 Colmar GES',
    country: 'France',
    siren: '932 121 536',
    tva: 'FR23932121536',
    rge: 'QPV/78468',
    decennale: '037.0012525-S178822',
    iban: 'FR76 1695 8000 0141 8260 6580 536'
}

const today = computed(() => new Date().toLocaleDateString('fr-FR'))

// Calculs basés sur draft
const computedLines = computed(() => {
    return props.draft.lines.map(l => {
        const lineSubtotal = l.unit_price * l.quantity
        const discountAmount = lineSubtotal * (l.discount_rate / 100)
        const lineTotal = lineSubtotal - discountAmount
        return { ...l, line_total: lineTotal }
    })
})

const totalHT = computed(() => computedLines.value.reduce((s, l) => s + l.line_total, 0))
const tva = computed(() => totalHT.value * (props.draft.tax_rate / 100))
const totalTTC = computed(() => totalHT.value + tva.value)

// Données du destinataire
const recipientName = computed(() => props.draft.custom_recipient_name || props.invoice?.custom_recipient_name)
const recipientCompany = computed(() => props.draft.custom_recipient_company || props.invoice?.custom_recipient_company)
const recipientAddress = computed(() => props.draft.custom_recipient_address || props.invoice?.custom_recipient_address)
const recipientSiret = computed(() => props.draft.custom_recipient_siret || props.invoice?.custom_recipient_siret)
</script>

<template>
    <div class="inline-block w-full xl:min-h-[1122.66px] xl:mx-auto text-xs px-8 py-6 bg-white">
        <!-- En-tête classique avec logo et infos facture -->
        <div class="flex justify-between items-start mb-6">
            <div class="flex gap-6">
                <div class="shrink-0">
                    <Logo size="md" />
                </div>
            </div>
            <div class="text-[11px] font-medium text-gray-600 text-right leading-tight">
                <p class="text-xl font-semibold text-black tracking-wide mb-1">FACTURE</p>
                <p class="font-bold text-black">{{ company.name }}</p>
                <p>{{ company.address1 }}, {{ company.zipCity }}, {{ company.country }}</p>
                <p class="mt-1">SIREN: {{ company.siren }} • TVA: {{ company.tva }}</p>
            </div>
        </div>

        <div class="text-[12px] flex justify-between items-start mb-6">
            <!-- Infos destinataire -->
            <div class="mb-4">
                <p class="font-semibold mb-1">Facturé à :</p>
                <p v-if="recipientCompany" class="font-medium">{{ recipientCompany }}</p>
                <p v-if="recipientCompany" class="text-gray-600">Représenté par : {{ recipientName }}</p>
                <p v-else class="font-medium">{{ recipientName }}</p>
                <p v-if="recipientSiret" class="mt-1 text-gray-600">SIRET: {{ recipientSiret }}</p>
                <p v-if="recipientAddress" class="whitespace-pre-line">{{ recipientAddress }}</p>
            </div>
            <div>
                <p><span class="text-gray-500">Facture N° :</span> <span class="font-semibold">{{ invoice?.number ||
                        'Brouillon' }}</span></p>
                <p><span class="text-gray-500">Date :</span> <span class="font-semibold">{{ invoice?.issue_date ? new
                    Date(invoice.issue_date).toLocaleDateString('fr-FR') : today }}</span></p>
                <p v-if="invoice?.due_date"><span class="text-gray-500">Échéance :</span> <span class="font-semibold">{{
                    new Date(invoice.due_date).toLocaleDateString('fr-FR') }}</span></p>
            </div>
        </div>

        <!-- Lignes produits -->
        <div class="mb-6">
            <p v-if="draft.title || invoice?.title" class="mb-2 text-xs font-medium">{{ draft.title || invoice?.title }}
            </p>
            <table class="w-full text-xs border-collapse">
                <thead>
                    <tr class="bg-blue-600 text-white">
                        <th class="p-2 text-left">DESCRIPTION</th>
                        <th class="p-2 text-right">QUANTITÉ</th>
                        <th class="p-2 text-right">PRIX (€)</th>
                        <th class="p-2 text-right">REMISE %</th>
                        <th class="p-2 text-right">MONTANT (€)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(l, idx) in computedLines" :key="idx" class="border-b last:border-b-0">
                        <td class="p-2 align-top">
                            <p class="font-semibold mb-1">{{ l.name }}</p>
                            <p class="whitespace-pre-line text-[11px] font-medium text-zinc-500">{{ l.description }}</p>
                        </td>
                        <td class="p-2 text-right align-top">{{ formatPrice(l.quantity) }}</td>
                        <td class="p-2 text-right align-top">{{ formatPrice(l.unit_price, true) }}</td>
                        <td class="p-2 text-right align-top">{{ formatPrice(l.discount_rate, true) }}</td>
                        <td class="p-2 text-right align-top">{{ formatPrice(l.line_total, true) }}</td>
                    </tr>
                    <tr v-if="!computedLines.length">
                        <td colspan="5" class="p-4 text-center text-gray-500 italic">Aucune ligne de produit/service
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Totaux -->
        <div class="flex justify-end mb-6">
            <div class="w-64 space-y-1">
                <div class="flex justify-between text-sm">
                    <span>Total HT :</span>
                    <span class="font-semibold">{{ formatPrice(totalHT, true) }} €</span>
                </div>
                <div class="flex justify-between text-sm">
                    <span>TVA ({{ draft.tax_rate }}%) :</span>
                    <span class="font-semibold">{{ formatPrice(tva, true) }} €</span>
                </div>
                <div class="flex justify-between text-base font-bold border-t pt-1">
                    <span>Total TTC :</span>
                    <span>{{ formatPrice(totalTTC, true) }} €</span>
                </div>
            </div>
        </div>

        <!-- Notes -->
        <div v-if="draft.notes || invoice?.notes" class="mb-4 text-[11px]">
            <p class="font-semibold mb-1">Notes :</p>
            <p class="whitespace-pre-line">{{ draft.notes || invoice?.notes }}</p>
        </div>

        <!-- Pied de page -->
        <div class="mt-8 pt-4 border-t border-dashed text-[10px] text-gray-600 grid gap-1">
            <div>Certification RGE QualiPv : {{ company.rge }} • Assurance Décennale : {{ company.decennale }}</div>
            <div>IBAN : {{ company.iban }}</div>
            <div>SIREN: {{ company.siren }} • TVA: {{ company.tva }} • {{ company.address1 }}, {{ company.zipCity }}, {{
                company.country }}</div>
        </div>
    </div>
</template>
