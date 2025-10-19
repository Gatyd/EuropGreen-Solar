<script setup lang="ts">
import type { Invoice } from '~/types/billing'
import type { Product } from '~/types/billing'
import apiRequest from '~/utils/apiRequest'

const props = defineProps<{
    draft: {
        custom_recipient_name: string
        custom_recipient_company: string
        custom_recipient_address: string
        custom_recipient_siret: string
        tax_rate: number
        notes: string
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
    invoice?: Invoice
}>()

const products = ref<Product[]>([])
const productModal = ref(false)
const loading = ref(false)
const toast = useToast()

const selectNewProduct = (product: Product) => {
    products.value.unshift(product)
    entry.productId = product.id
}

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
        cost_price: parseFloat(p.cost_price),
        product_type: p.type,
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
    if (!state.custom_recipient_name.trim()) {
        errors.push({ name: 'custom_recipient_name', message: "Le nom du destinataire est requis." })
    }
    if (state.tax_rate < 0 || state.tax_rate > 100) {
        errors.push({ name: 'tax_rate', message: "Le taux de TVA doit être compris entre 0 et 100%." })
    }
    return errors
}

const emit = defineEmits<{
    (e: 'created', invoice: Invoice): void
    (e: 'updated', invoice: Invoice): void
}>()

async function onSubmit() {
    if (!props.draft.lines.length) {
        toast.add({ title: 'Erreur', description: "Ajoutez au moins une ligne à la facture.", color: 'error', icon: 'i-heroicons-exclamation-triangle' })
        return
    }

    // Construire payload pour API
    const payload = {
        custom_recipient_name: props.draft.custom_recipient_name,
        custom_recipient_company: props.draft.custom_recipient_company,
        custom_recipient_address: props.draft.custom_recipient_address,
        custom_recipient_siret: props.draft.custom_recipient_siret,
        tax_rate: props.draft.tax_rate,
        notes: props.draft.notes,
        lines: props.draft.lines.map((l, idx) => ({
            position: idx,
            product_type: l.product_type,
            name: l.name,
            description: l.description,
            unit_price: l.unit_price,
            cost_price: l.cost_price ?? 0,
            quantity: l.quantity,
            discount_rate: l.discount_rate,
        })),
    }

    loading.value = true
    const isEdit = !!props.invoice

    // Création ou mise à jour : un seul appel PATCH/POST
    const method = isEdit ? 'PATCH' : 'POST'
    const url = isEdit ? `/api/invoices/${props.invoice!.id}/` : '/api/invoices/'
    
    const res = await apiRequest<Invoice>(() => $fetch(url, {
        method,
        body: payload,
        credentials: 'include'
    }), toast)
    
    loading.value = false
    if (res) {
        toast.add({ 
            title: isEdit ? 'Facture mise à jour' : 'Facture créée', 
            color: 'success', 
            icon: 'i-heroicons-check-circle' 
        })
        if (isEdit) {
            emit('updated', res)
        } else {
            emit('created', res)
        }
    }
}
</script>

<template>
    <Teleport to="body">
        <ProductModal v-if="productModal" v-model="productModal" @submit="selectNewProduct" />
    </Teleport>
    <div v-bind="$attrs" class="px-4 space-y-4">
        <UForm :state="props.draft" :validate="validate" @submit="onSubmit" class="space-y-6">
            <!-- Section destinataire -->
            <UCard>
                <template #header>
                    <div class="font-semibold">Destinataire</div>
                </template>
                <div class="grid grid-cols-1 md:grid-cols-12 gap-4">
                    <UFormField class="md:col-span-4" label="Nom" name="custom_recipient_name" required>
                        <UInput v-model="props.draft.custom_recipient_name" class="w-full" placeholder="Jean Dupont" />
                    </UFormField>
                    <UFormField class="md:col-span-3" label="Entreprise" name="custom_recipient_company">
                        <UInput v-model="props.draft.custom_recipient_company" class="w-full"
                            placeholder="SARL Exemple" />
                    </UFormField>
                    <UFormField class="md:col-span-3" label="SIRET" name="custom_recipient_siret">
                        <UInput v-model="props.draft.custom_recipient_siret" class="w-full"
                            placeholder="123 456 789 00010" />
                    </UFormField>
                    <UFormField class="md:col-span-2" label="TVA (%)" name="tax_rate" required>
                        <UInput v-model="props.draft.tax_rate" class="w-full" type="number" min="0" step="0.01" />
                    </UFormField>
                    <UFormField label="Adresse" name="custom_recipient_address" class="md:col-span-12">
                        <UTextarea v-model="props.draft.custom_recipient_address" class="w-full" :rows="2"
                            placeholder="10 rue de la Paix, 75002 Paris" />
                    </UFormField>
                </div>
            </UCard>

            <!-- Section ajout de lignes -->
            <UCard>
                <template #header>
                    <div class="flex flex-col md:flex-row md:items-center justify-between">
                        <div class="font-semibold">Lignes de la facture</div>
                        <div class="text-xs text-gray-500">Sélectionnez un produit, saisissez quantité et remise puis
                            ajoutez</div>
                    </div>
                </template>

                <div class="grid grid-cols-1 md:grid-cols-5 gap-3 items-end">
                    <UFormField label="Produit" class="md:col-span-3" required>
                        <USelectMenu v-model="entry.productId" value-key="value" class="w-full"
                            :items="availableProducts.map(p => ({ label: p.name, value: p.id }))"
                            placeholder="Sélectionner un produit" searchable clearable>
                            <template #content-bottom>
                                <UButton icon="i-heroicons-plus" color="neutral" label="Ajouter un produit"
                                    @click.stop="productModal = true" block />
                            </template>
                        </USelectMenu>
                    </UFormField>
                    <UFormField label="Quantité" required>
                        <UInput v-model.number="entry.quantity" class="w-full" type="number" min="1" step="1" />
                    </UFormField>
                    <UFormField label="Remise (%)">
                        <UInput v-model.number="entry.discount_rate" class="w-full" type="number" :min="0" :max="100"
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
            </UCard>

            <UCard>
                <template #header>
                    <div class="font-semibold">Notes (optionnelle)</div>
                </template>
                <UFormField name="notes">
                    <UTextarea class="w-full" v-model="props.draft.notes" :rows="6" />
                </UFormField>
                <template #footer>
                    <div class="flex justify-end">
                        <UButton type="submit" color="primary" :loading="loading" icon="i-heroicons-check-circle"
                            :label="invoice ? 'Modifier la facture' : 'Créer la facture'" />
                    </div>
                </template>
            </UCard>
        </UForm>
    </div>
</template>
