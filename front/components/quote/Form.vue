<script setup lang="ts">
import type { Offer } from '~/types/offers'
import type { Product } from '~/types/billing'
import apiRequest from '~/utils/apiRequest'

const props = defineProps<{
    offer: Offer
    draft: {
        title: string
        valid_until: string | null
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
    quote?: any
}>()

const products = ref<Product[]>([])
const productModal = ref(false)
const loading = ref(false)
const loadingReply = ref(false)
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
    // Exemple: titre facultatif, mais on peut ajouter une règle si besoin
    if (!state.valid_until) {
        errors.push({ name: 'valid_until', message: "La date de validité est requise." })
    }
    // Si on est en négociation (pending), exiger une réponse
    if (props.quote && props.quote.status === 'pending' && !reply.value.trim()) {
        errors.push({ name: 'reply', message: "Veuillez entrer une réponse à la négociation." })
    }
    if (state.tax_rate < 0 || state.tax_rate > 100) {
        errors.push({ name: 'tax_rate', message: "Le taux de TVA doit être compris entre 0 et 100%." })
    }
    return errors
}

const emit = defineEmits<{
    (e: 'created', quote: any): void
}>()

async function onSubmit() {
    if (!props.draft.lines.length) {
        toast.add({ title: 'Erreur', description: "Ajoutez au moins une ligne au devis.", color: 'error', icon: 'i-heroicons-exclamation-triangle' })
        return
    }
    // Construire payload pour API
    const payload = {
        offer: props.offer.id,
        title: props.draft.title,
        valid_until: props.draft.valid_until,
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

    // Si on est en phase de négociation ou après envoi (sent), la soumission crée une nouvelle version et envoie la réponse
    if (props.quote && (props.quote.status === 'pending' || props.quote.status === 'sent')) {
        loading.value = true
        const res = await apiRequest<any>(() => $fetch(`/api/quotes/${props.quote!.id}/${props.quote.status === 'pending' ? 'reply-new-version' : 'send-new-version'}/`, {
            method: 'POST', body: props.quote.status === 'pending' ? { ...payload, reply: reply.value } : payload, credentials: 'include'
        }), toast)
        loading.value = false
        if (res) {
            toast.add({ title: 'Nouvelle version envoyée', color: 'success', icon: 'i-heroicons-check-circle' })
            emit('created', res)
        }
        return
    }

    // Sinon, logique standard (création ou patch du brouillon)
    loading.value = true
    const isEdit = !!props.quote
    const url = isEdit ? `/api/quotes/${props.quote.id}/` : '/api/quotes/'
    const method = isEdit ? 'PATCH' : 'POST'
    const res = await apiRequest<any>(() => $fetch(url, { method, body: payload, credentials: 'include' }), toast)
    loading.value = false
    if (res) {
        toast.add({ title: isEdit ? 'Brouillon mis à jour' : 'Devis créé', color: 'success', icon: 'i-heroicons-check-circle' })
        emit('created', res)
    }
}

// Gestion des réponses de négociation
const reply = ref('')

async function submitReplyCurrent() {
    if (!props.quote) return
    if (!reply.value.trim()) {
        toast.add({ title: 'Réponse requise', color: 'warning', icon: 'i-heroicons-exclamation-triangle' })
        return
    }
    loadingReply.value = true
    const res = await apiRequest<any>(() => $fetch(`/api/quotes/${props.quote.id}/reply/`, {
        method: 'POST', body: { reply: reply.value }, credentials: 'include'
    }), toast)
    loadingReply.value = false
    if (res) {
        toast.add({ title: 'Réponse envoyée', color: 'success', icon: 'i-heroicons-check-circle' })
        emit('created', res)
    }
}

</script>

<template>
    <Teleport to="body">
        <ProductModal v-if="productModal" v-model="productModal" @submit="selectNewProduct" />
    </Teleport>
    <div v-bind="$attrs" class="p-4 space-y-4">
        <UForm :state="props.draft" :validate="validate" @submit="onSubmit" class="space-y-6">
            <!-- Section informations générales -->
            <UCard>
                <template #header>
                    <div class="font-semibold">Informations générales</div>
                </template>
                <div class="grid grid-cols-2 md:grid-cols-12 gap-4">
                    <UFormField label="Titre du devis" class="col-span-2 md:col-span-7" name="title">
                        <UInput v-model="props.draft.title" class="w-full"
                            placeholder="Devis pour fourniture et pose d'une installation 8.5kwc" />
                    </UFormField>
                    <UFormField label="Valide jusqu'au" name="valid_until" class="md:col-span-3" required>
                        <UInput v-model="props.draft.valid_until" class="w-full" type="date" />
                    </UFormField>
                    <UFormField label="TVA (%)" name="tax_rate" class="md:col-span-2" required>
                        <UInput v-model="props.draft.tax_rate" class="w-full" type="number" min="0" step="0.01" />
                    </UFormField>
                </div>
            </UCard>

            <!-- Section négociations (si status pending) -->
            <UCard v-if="props.quote && props.quote.status === 'pending'">
                <template #header>
                    <div class="font-semibold">Négociations</div>
                </template>
                <div class="grid grid-cols-2 gap-4">
                    <UFormField name="negociations" label="Message du client">
                        <UTextarea class="w-full" :model-value="props.quote.negociations || ''" :rows="6" readonly
                            disabled />
                    </UFormField>
                    <UFormField name="reply" label="Votre réponse" required>
                        <UTextarea class="w-full" v-model="reply" :rows="6" placeholder="Saisissez votre réponse…" />
                    </UFormField>
                </div>
            </UCard>

            <!-- Section ajout de lignes -->
            <UCard>
                <template #header>
                    <div class="flex flex-col md:flex-row md:items-center justify-between">
                        <div class="font-semibold">Lignes du devis</div>
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
            </UCard>

            <UCard>
                <template #header>
                    <div class="font-semibold">Notes (optionnelle)</div>
                </template>
                <UFormField name="notes">
                    <UTextarea class="w-full" v-model="props.draft.notes" :rows="6" />
                </UFormField>
                <template #footer>
                    <div class="flex flex-col sm:flex-row justify-end gap-2">
                        <UButton v-if="quote && quote.status === 'pending'" color="primary"
                            variant="soft" :loading="loadingReply" icon="i-heroicons-paper-airplane"
                            @click="submitReplyCurrent" label="Envoyer la réponse (version actuelle)" />
                        <UButton type="submit" color="primary" :loading="loading" icon="i-heroicons-check-circle"
                            :label="quote ? quote.status === 'pending' || quote.status === 'sent' ? 'Envoyer (nouvelle version)' : 'Modifier le brouillon' : 'Valider le brouillon'" />
                    </div>
                </template>
            </UCard>
        </UForm>
    </div>
</template>