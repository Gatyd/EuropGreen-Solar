<script setup lang="ts">
import type { Offer } from '~/types/offers'

const props = defineProps<{
    offer: Offer
    quote?: any
    draft: {
        title: string
        valid_until: string | null
        tax_rate: number
        lines: Array<{
            productId: string
            name: string
            description: string
            unit_price: number
            quantity: number
            discount_rate: number
        }>
    }
}>()

const today = computed(() => new Date().toLocaleDateString('fr-FR'))

const previewLines = computed(() => props.draft.lines.map(l => {
    const amount = l.unit_price * l.quantity * (1 - (l.discount_rate || 0) / 100)
    return {
        titre: l.name,
        description: l.description,
        quantite: l.quantity,
        prix: l.unit_price,
        remise: l.discount_rate,
        montant: amount,
    }
}))

const totalHT = computed(() => previewLines.value.reduce((s, l) => s + l.montant, 0))
const tva = computed(() => totalHT.value * (props.draft.tax_rate / 100))
const totalTTC = computed(() => totalHT.value + tva.value)
</script>

<template>
    <div v-bind="$attrs" class="inline-block w-[793.8px] xl:min-h-[1122.66px] xl:mx-auto text-xs px-6 py-2 bg-white shadow-md rounded-lg">
        <!-- En-tête -->
        <div class="flex justify-between items-center mb-6">
            <!-- Logo (image à gauche) -->
            <div>
                <Logo />
            </div>

            <!-- Infos société -->
            <div class="text-[11px] font-medium text-gray-500 text-right">
                <p class="text-2xl text-black font-normal mb-2">DEVIS</p>
                <p class="font-bold">Europ'Green Solar</p>
                <p>18 rue de Berlin</p>
                <p>68000 Colmar GES</p>
                <p>France</p>
                <p>n° SIREN: 932 121 536</p>
                <p class="mb-2">n° TVA: FR23932121536</p>
                <p>Dirigeant</p>
                <p>0970702656</p>
                <p>0761303795</p>
                <p>europgreensolar@gmail.com</p>
                <p>europ-greensolar.fr</p>
            </div>
        </div>

        <div class="flex justify-between">
            <!-- Infos client -->
            <div class="mb-6">
                <p class="font-bold">À :</p>
                <p>{{ props.offer.first_name }} {{ props.offer.last_name }}</p>
                <p>{{ props.offer.address }}</p>
                <!-- <p>{{ props.offer.email }}</p>
                <p>{{ props.offer.phone }}</p> -->
            </div>

            <!-- Infos devis -->
            <div class="mb-6 w-60">
                <p class="flex justify-between font-medium">Devis N° :<span class="font-bold"> {{ quote?.number || '—' }}</span></p>
                <p class="flex justify-between font-medium">Date :<span class="font-bold"> {{ today }}</span></p>
                <p class="flex justify-between font-medium">Valide jusqu’au :<span class="font-bold"> {{ props.draft.valid_until ? new Date(props.draft.valid_until).toLocaleDateString('fr-FR') : '—' }}</span></p>
            </div>
        </div>

        <!-- Tableau -->
    <p class="mb-2 text-xs">{{ props.draft.title || "" }}</p>
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
                <tr v-for="(ligne, i) in previewLines" :key="i" class="">
                    <td class="p-2">
                        <p class="font-semibold mb-1">{{ ligne.titre }}</p>
                        <p class="whitespace-pre-line text-[11px] font-medium text-zinc-500">{{ ligne.description }}</p>
                    </td>
                    <td class="p-2 text-right">{{ ligne.quantite }}</td>
                    <td class="p-2 text-right">{{ ligne.prix.toFixed(2) }}</td>
                    <td class="p-2 text-right">{{ ligne.remise.toFixed(2) }}</td>
                    <td class="p-2 text-right">{{ ligne.montant.toFixed(2) }}</td>
                </tr>
            </tbody>
        </table>

        <!-- Totaux -->
        <div class="mt-6 text-sm flex justify-end">
            <div class="w-64">
                <div class="flex justify-between border-t py-1">
                    <span class="font-semibold">TOTAL H.T. :</span>
                    <span>{{ totalHT.toFixed(2) }} €</span>
                </div>
                <div class="flex justify-between py-1">
                    <span class="font-semibold">TVA 20% :</span>
                    <span>{{ tva.toFixed(2) }} €</span>
                </div>
                <div class="flex justify-between border-t font-bold py-1">
                    <span>TOTAL (EUR) :</span>
                    <span>{{ totalTTC.toFixed(2) }} €</span>
                </div>
            </div>
        </div>
    </div>
</template>
