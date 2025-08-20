<script setup lang="ts">
import type { Offer } from '~/types/offers'
import type { Product } from '~/types/billing'

const props = defineProps<{
    offer: Offer
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

const products = ref<Product[]>([])
const loading = ref(false)
const toast = useToast()

// Charger le catalogue produits
onMounted(async () => {
    try {
        const res = await $fetch<Product[]>(`/api/products/`, { credentials: 'include' })
        products.value = res.filter(p => p.is_active)
    } catch (e) {
        // noop UI toast ailleurs
    }
})

// Ligne d'entrée courante pour ajout
const entry = reactive({ productId: '', quantity: 1, discount_rate: 0 })
const entryErrors = ref<string[]>([])

const availableProducts = computed(() => {
    const usedIds = new Set(props.draft.lines.map(l => l.productId))
    return products.value.filter(p => !usedIds.has(p.id) || entry.productId === p.id)
})

function resetEntry() {
    entry.productId = ''
    entry.quantity = 1
    entry.discount_rate = 0
    entryErrors.value = []
}

function validateEntry() {
    const errors: string[] = []
    if (!entry.productId) errors.push('Produit obligatoire')
    if (!(entry.quantity > 0)) errors.push('La quantité doit être supérieure à 0')
    if (entry.discount_rate < 0 || entry.discount_rate > 100) errors.push('La remise doit être comprise entre 0 et 100%')
    entryErrors.value = errors
    return errors
}

function addLine() {
    const errs = validateEntry()
    if (errs.length) return
    const p = products.value.find(p => p.id === entry.productId)
    if (!p) return
    props.draft.lines.push({
        productId: p.id,
        name: p.name,
        description: p.description,
        unit_price: parseFloat(p.unit_price),
        quantity: entry.quantity,
        discount_rate: entry.discount_rate,
    })
    resetEntry()
}

function removeLine(index: number) {
    props.draft.lines.splice(index, 1)
}

function updateQty(index: number, qty: number) {
    if (qty > 0) props.draft.lines[index].quantity = qty
}

function updateDiscount(index: number, d: number) {
    if (d >= 0 && d <= 100) props.draft.lines[index].discount_rate = d
}

// Validation globale du formulaire (UForm)
const validate = (state: any) => {
    const errors: any[] = []
    // Exemple: titre facultatif, mais on peut ajouter une règle si besoin
    if (!state.valid_until) {
        errors.push({ name: 'valid_until', message: "La date de validité est requise." })
    }
    if (!props.draft.lines.length) {
        errors.push({ name: 'lines', message: "Ajoutez au moins une ligne au devis." })
    }
    return errors
}

function onSubmit() {
    // Simule l'envoi: journalise le brouillon et affiche un toast
    // Ici on pourrait mapper vers le payload API attendu pour /api/quotes
    // Pour l'instant, simple feedback
    // eslint-disable-next-line no-console
    console.log('Draft quote', JSON.parse(JSON.stringify(props.draft)))
    toast.add({ title: 'Brouillon prêt', description: 'Le devis est cohérent et prêt à être sauvegardé.', color: 'primary', icon: 'i-heroicons-check-circle' })
}

</script>

<template>
    <div v-bind="$attrs" class="p-4 space-y-4">
        <UForm :state="props.draft" :validate="validate" @submit="onSubmit" class="space-y-6">
            <!-- Section informations générales -->
            <UCard>
                <template #header>
                    <div class="font-semibold">Informations générales</div>
                </template>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <UFormField label="Titre du devis" class="md:col-span-2" name="title">
                        <UInput v-model="props.draft.title" class="w-full" placeholder="Devis pour fourniture et pose d'une installation 8.5kwc" />
                    </UFormField>
                    <UFormField label="Valide jusqu'au" name="valid_until" required>
                        <UInput v-model="props.draft.valid_until" class="w-full" type="date" />
                    </UFormField>
                </div>
            </UCard>

            <!-- Section ajout de lignes -->
            <UCard>
                <template #header>
                    <div class="flex items-center justify-between">
                        <div class="font-semibold">Lignes du devis</div>
                        <div class="text-xs text-gray-500">Sélectionnez un produit, saisissez quantité et remise puis
                            ajoutez</div>
                    </div>
                </template>

                <div class="grid grid-cols-1 md:grid-cols-5 gap-3 items-end">
                    <UFormField label="Produit" class="md:col-span-3" required>
                        <USelectMenu v-model="entry.productId" value-key="value" class="w-full"
                            :items="availableProducts.map(p => ({ label: p.name, value: p.id }))"
                            placeholder="Sélectionner un produit" searchable clearable />
                    </UFormField>
                    <UFormField label="Quantité" required>
                        <UInput v-model.number="entry.quantity" class="w-full" type="number" min="1" step="1" />
                    </UFormField>
                    <UFormField label="Remise (%)">
                        <UInput v-model.number="entry.discount_rate" class="w-full" type="number" min="0" max="100"
                            step="0.5" />
                    </UFormField>
                    <div class="md:col-span-5 flex justify-between items-center mt-1">
                        <div class="text-xs text-gray-500">
                            <template v-if="entry.productId">
                                <span>
                                    PU: {{Number(products.find(p => p.id === entry.productId)?.unit_price ||
                                        0).toFixed(2)}} €
                                </span>
                            </template>
                        </div>
                        <UButton color="primary" icon="i-heroicons-plus" :disabled="!!validateEntry().length"
                            @click="addLine" label="Ajouter la ligne" />
                    </div>
                    <!-- <div v-if="entryErrors.length" class="md:col-span-5">
                        <UAlert color="warning" variant="soft" icon="i-heroicons-exclamation-triangle"
                            :title="'Veuillez corriger : ' + entryErrors.join(', ')" />
                    </div> -->
                </div>

                <div v-if="props.draft.lines.length" class="mt-4 space-y-3">
                    <div v-for="(l, idx) in props.draft.lines" :key="l.productId" class="rounded border p-3">
                        <div class="flex items-center justify-between mb-2">
                            <div>
                                <div class="font-medium">{{ l.name }}</div>
                                <div class="text-xs text-gray-500 line-clamp-1">{{ l.description }}</div>
                            </div>
                            <UButton color="error" variant="soft" size="xs" icon="i-heroicons-trash"
                                @click="removeLine(idx)" />
                        </div>
                        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 items-end">
                            <UFormField label="Quantité">
                                <UInput :model-value="l.quantity" @update:model-value="v => updateQty(idx, Number(v))"
                                    type="number" min="1" step="1" />
                            </UFormField>
                            <UFormField label="Remise (%)">
                                <UInput :model-value="l.discount_rate"
                                    @update:model-value="v => updateDiscount(idx, Number(v))" type="number" min="0"
                                    max="100" step="0.5" />
                            </UFormField>
                            <div class="text-right text-sm text-gray-600">
                                Montant: {{ (l.unit_price * l.quantity * (1 - (l.discount_rate || 0) / 100)).toFixed(2)
                                }} €
                            </div>
                        </div>
                    </div>
                </div>
                <template #footer>
                    <div class="flex justify-end gap-2">
                        <UButton type="submit" color="primary" :loading="loading" icon="i-heroicons-check-circle"
                            label="Valider le brouillon" />
                    </div>
                </template>
            </UCard>
        </UForm>
    </div>
</template>