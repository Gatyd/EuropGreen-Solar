<script setup lang="ts">
import { h, resolveComponent } from 'vue'
import { upperFirst } from 'scule'
import type { TableColumn } from '@nuxt/ui'
import type { Product } from '~/types/billing'
import { formatDate } from '~/utils/formatDate'

const UButton = resolveComponent('UButton')
const UDropdownMenu = resolveComponent('UDropdownMenu')
const UPopover = resolveComponent('UPopover')
const q = ref("")
const formModal = ref(false)
const deleteModal = ref(false)
const selectedProduct = ref<Product | undefined>(undefined)
const toast = useToast()
const loading = ref(false)
const products = ref<Product[] | undefined>([])

const table = useTemplateRef('table')

async function fetchProducts() {
    loading.value = true
    const result = await apiRequest<Product[]>(
        () => $fetch(`/api/products/`, {
            credentials: "include"
        }),
        toast
    );
    products.value = result || undefined
    loading.value = false
}

// Mapping des types techniques -> libellés utilisateurs
const TYPE_LABELS: Record<string, string> = {
    panel: 'Panneau',
    panneau: 'Panneau',
    inverter: 'Onduleur',
    onduleur: 'Onduleur',
    battery: 'Batterie',
    batterie: 'Batterie',
    structure: 'Structure',
    service: 'Service'
}

const typeLabel = (val?: string) => {
    if (!val) return '—'
    const key = String(val).toLowerCase()
    return TYPE_LABELS[key] ?? upperFirst(val)
}

// Utilitaires UI
const truncate = (s: string, n = 30) => {
    if (!s) return '—'
    return s.length > n ? `${s.slice(0, n)}…` : s
}

const columns: TableColumn<Product>[] = [{
    accessorKey: 'name',
    header: 'Nom',
    cell: ({ row }) => row.original.name
}, {
    accessorKey: 'type',
    header: 'Type',
    cell: ({ row }) => typeLabel(row.original.type as unknown as string)
}, {
    accessorKey: 'description',
    header: 'Description',
    cell: ({ row }) => {
        const full = row.original.description || ''
        const short = truncate(full, 30)
        return h(UPopover as any, { trigger: 'click', popper: { placement: 'bottom-start' } }, {
            default: () => h('span', { class: 'cursor-pointer text-gray-700 hover:underline underline-offset-2 decoration-dotted' }, short),
            content: () => h('div', { class: 'max-w-sm whitespace-pre-wrap text-sm p-2' }, full || '—')
        })
    }
}, {
    accessorKey: 'unit_price',
    header: 'Prix unitaire (€)',
    cell: ({ row }) => formatPrice(row.original.unit_price)
}, {
    accessorKey: 'cost_price',
    header: 'Coût (€)',
    cell: ({ row }) => Number(row.original.cost_price) !== 0 ? formatPrice(row.original.cost_price) : 'Non défini'
}, {
    accessorKey: 'created_at',
    header: 'Créé le',
    cell: ({ row }) => formatDate(row.original.created_at as unknown as string)
}, {
    header: 'Actions',
    cell: ({ row }) => {
        return h('div', { class: 'flex gap-2' }, [
            h(UButton, {
                icon: 'i-lucide-pen',
                color: 'secondary',
                variant: 'subtle',
                class: 'rounded-full cursor-pointer',
                size: 'sm',
                onClick: () => {
                    selectedProduct.value = row.original
                    formModal.value = true
                }
            }),
            h(UButton, {
                icon: 'i-lucide-trash',
                color: 'error',
                variant: 'subtle',
                class: 'rounded-full cursor-pointer',
                size: 'sm',
                onClick: () => {
                    selectedProduct.value = row.original
                    deleteModal.value = true
                }
            })
        ])
    }
}]

const CreateNewProduct = () => {
    selectedProduct.value = undefined
    formModal.value = true
}

onMounted(fetchProducts)

</script>

<template>
    <div>
        <ProductModal v-model="formModal" :product="selectedProduct" @submit="fetchProducts" @update:model-value="v => formModal = v" />
        <ProductDelete v-if="selectedProduct" v-model="deleteModal" :product="selectedProduct"
            @submit="fetchProducts" />
        <div class="sticky top-0 z-50 bg-white">
            <UDashboardNavbar title="Produits / Services" class="lg:text-2xl font-semibold"
                :ui="{ root: 'h-12 lg:h-(--ui-header-height)' }">
                <template #trailing>
                    <UBadge v-if="products?.length && products.length > 0" variant="subtle">{{ products.length }}
                    </UBadge>
                </template>
                <template #right>
                    <UButton color="primary" label="Nouveau produit" icon="i-heroicons-plus" class="mx-2"
                        @click="CreateNewProduct" />
                </template>
            </UDashboardNavbar>
            <div class="flex items-center justify-between gap-3 mx-5 py-3 my-1 border-b border-default">
                <SearchInput v-model="q" />
                <UDropdownMenu class="ml-auto" :items="table?.tableApi?.getAllColumns().filter(column => column.getCanHide()).map(column => ({
                    label: typeof column.columnDef?.header === 'string' ? column.columnDef.header : upperFirst(column.id),
                    type: 'checkbox' as const,
                    checked: column.getIsVisible(),
                    onUpdateChecked(checked: boolean) {
                        table?.tableApi?.getColumn(column.id)?.toggleVisibility(!!checked)
                    },
                    onSelect(e?: Event) {
                        e?.preventDefault()
                    }
                }))" :content="{ align: 'end' }">
                    <UButton label="Afficher" color="neutral" variant="outline" trailing-icon="i-lucide-chevron-down"
                        aria-label="Columns select dropdown" />
                </UDropdownMenu>
            </div>
        </div>
        <div class="overflow-auto relative">
            <UTable ref="table" :data="products" :columns="columns" v-model:global-filter="q" sticky
                class="h-full bg-white shadow-lg rounded-lg" :loading="loading" />
        </div>
    </div>
</template>