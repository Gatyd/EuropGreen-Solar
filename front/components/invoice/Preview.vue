<script setup lang="ts">
import type { Invoice, Installment, Payment, QuoteLine } from '~/types/billing'
import type { Offer } from '~/types/offers'
import { formatPrice } from '~/utils/formatPrice'

const props = defineProps<{ offer: Offer; invoice: Invoice | null }>()

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

const lines = computed<QuoteLine[]>(() => props.invoice?.lines ?? [])
const totalHT = computed(() => lines.value.reduce((s, l) => s + parseFloat(l.line_total), 0))
const tva = computed(() => totalHT.value * (props.invoice ? parseFloat(props.invoice.tax_rate) / 100 : 0))
const totalTTC = computed(() => totalHT.value + tva.value)

const installments = computed<Installment[]>(() => props.invoice?.installments ?? [])
const unpaidInstallments = computed(() => installments.value.filter(i => !i.is_paid))
const payments = computed<Payment[]>(() => props.invoice?.payments ?? [])
const amountPaid = computed(() => (props.invoice ? parseFloat(props.invoice.amount_paid || '0') : 0))
const balanceDue = computed(() => (props.invoice ? parseFloat(props.invoice.balance_due || '0') : 0))
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
            <!-- Infos client -->
            <div class="mb-4">
                <p class="font-semibold mb-1">Facturé à :</p>
                <p class="font-medium">{{ props.offer.first_name }} {{ props.offer.last_name }}</p>
                <p>{{ props.offer.address }}</p>
            </div>
            <div>
                <p><span class="text-gray-500">Facture N° :</span> <span class="font-semibold">{{ invoice?.number || '—'
                        }}</span></p>
                <p><span class="text-gray-500">Date :</span> <span class="font-semibold">{{ invoice?.issue_date ||
                        today }}</span></p>
                <p v-if="invoice?.due_date"><span class="text-gray-500">Échéance :</span> <span class="font-semibold">{{
                    invoice.due_date }}</span></p>
                <!-- <p v-if="invoice?.status" class="mt-1"><span class="text-gray-500">Statut :</span> <span
                        class="uppercase font-semibold">{{ invoice.status.replace('_', ' ') }}</span></p> -->
            </div>
        </div>

        <!-- Lignes produits -->
        <div class="mb-6">
            <p v-if="invoice?.title" class="mb-2 text-xs font-medium">{{ invoice.title }}</p>
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
                    <tr v-for="l in lines" :key="l.id" class="border-b last:border-b-0">
                        <td class="p-2 align-top">
                            <p class="font-semibold mb-1">{{ l.name }}</p>
                            <p class="whitespace-pre-line text-[11px] font-medium text-zinc-500">{{ l.description }}</p>
                        </td>
                        <td class="p-2 text-right align-top">{{ l.quantity }}</td>
                        <td class="p-2 text-right align-top">{{ formatPrice(parseFloat(l.unit_price), true) }}</td>
                        <td class="p-2 text-right align-top">{{ formatPrice(parseFloat(l.discount_rate), true) }}</td>
                        <td class="p-2 text-right align-top">{{ formatPrice(parseFloat(l.line_total), true) }}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Totaux -->
        <div class="mt-2 mb-6 flex justify-end">
            <div class="w-72 text-sm">
                <div class="flex justify-between border-t py-1"><span class="font-semibold">TOTAL H.T. :</span><span>{{
                    formatPrice(totalHT, true) }} €</span></div>
                <div class="flex justify-between py-1"><span class="font-semibold">TVA {{ invoice ?
                    formatPrice(parseFloat(invoice.tax_rate)) : '—' }}% :</span><span>{{ formatPrice(tva, true) }}
                        €</span></div>
                <div class="flex justify-between border-t font-bold py-1"><span>TOTAL (EUR) :</span><span>{{
                    formatPrice(totalTTC, true) }} €</span></div>
                <div class="flex justify-between py-1"><span class="font-semibold">Payé :</span><span>{{
                    formatPrice(amountPaid, true) }} €</span></div>
                <div class="flex justify-between py-1"><span class="font-semibold">Reste à payer :</span><span>{{
                    formatPrice(balanceDue, true) }} €</span></div>
            </div>
        </div>

        <!-- Échéances de paiements (si non soldées) -->
        <div v-if="unpaidInstallments.length" class="mb-4 text-[11px] leading-relaxed">
            <p class="font-semibold text-red-600 mb-1">Échéances de paiements :</p>
            <div v-for="i in unpaidInstallments" :key="i.id" class="pl-1">
                <span class="font-medium">{{ i.label || 'Échéance' }}</span>
                — <span>{{ i.amount ? formatPrice(parseFloat(i.amount), true) + ' €' : (i.percentage ?
                    formatPrice(parseFloat(i.percentage), true) + ' %' : '—') }}</span>
                — <span>Échéance {{ i.due_date || '—' }}</span>
            </div>
        </div>

        <!-- Règlements encaissés -->
        <div v-if="payments.length" class="mb-6 text-[11px] leading-relaxed">
            <p class="font-semibold text-gray-700 mb-1">Règlements encaissés :</p>
            <div v-for="p in payments" :key="p.id" class="pl-1">
                <span class="font-medium">{{ p.date }}</span>
                — <span>{{ p.method || 'Méthode inconnue' }}</span>
                <span v-if="p.reference" class="text-gray-500"> (Ref: {{ p.reference }})</span>
                — <span class="font-semibold">{{ formatPrice(parseFloat(p.amount), true) }} €</span>
            </div>
        </div>

        <!-- Notes -->
        <div v-if="invoice?.notes" class="mb-8">
            <div class="text-sm font-semibold text-zinc-700 mb-2">Notes</div>
            <div
                class="border border-zinc-200 rounded-md bg-zinc-50 p-4 text-sm leading-relaxed text-zinc-800 whitespace-pre-line">
                {{ invoice?.notes }}
            </div>
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
