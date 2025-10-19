<script setup lang="ts">
import { h, resolveComponent } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import type { Invoice } from '~/types/billing'
import { formatPrice } from '~/utils/formatPrice'
import { upperFirst } from 'scule'

definePageMeta({
    middleware: 'admin'
})

const UButton = resolveComponent('UButton')
const UBadge = resolveComponent('UBadge')

const toast = useToast()
const invoices = ref<Invoice[]>([])
const loading = ref(false)
const showCreateModal = ref(false)
const selectedInvoice = ref<Invoice | undefined>(undefined)

const table = useTemplateRef('table')

const statusItems = ref([
    { value: 'all', label: 'Tous les statuts' },
    { value: 'draft', label: 'Brouillon' },
    { value: 'issued', label: 'Émise' },
    { value: 'partially_paid', label: 'Partiellement payée' },
    { value: 'paid', label: 'Payée' },
    { value: 'cancelled', label: 'Annulée' },
])
const filters = reactive({
    status: 'all',
    search: '',
})

const statusColors: Record<string, string> = {
    draft: 'gray',
    issued: 'blue',
    partially_paid: 'orange',
    paid: 'green',
    cancelled: 'red',
}

const statusLabels: Record<string, string> = {
    draft: 'Brouillon',
    issued: 'Émise',
    partially_paid: 'Part. payée',
    paid: 'Payée',
    cancelled: 'Annulée',
}

const filteredInvoices = computed(() => {
    let result = invoices.value

    if (filters.status !== 'all') {
        result = result.filter(i => i.status === filters.status)
    }

    if (filters.search) {
        const search = filters.search.toLowerCase()
        result = result.filter(i =>
            i.number?.toLowerCase().includes(search) ||
            i.custom_recipient_name?.toLowerCase().includes(search) ||
            i.custom_recipient_company?.toLowerCase().includes(search)
        )
    }

    return result
})

const columns: TableColumn<Invoice>[] = [{
    accessorKey: 'number',
    header: 'N° Facture',
    cell: ({ row }) => h('span', { class: 'font-mono font-semibold' }, row.original.number)
}, {
    accessorKey: 'recipient',
    header: 'Destinataire',
    cell: ({ row }) => {
        const name = row.original.custom_recipient_name || ''
        const company = row.original.custom_recipient_company || ''
        const display = (name && company) ? `${name} (${company})` : (name || company || '—')
        return h('p', { class: 'font-medium' }, display)
    }
}, {
    accessorKey: 'issue_date',
    header: 'Date',
    cell: ({ row }) => h('span', { class: 'text-sm' }, new Date(row.original.issue_date).toLocaleDateString('fr-FR'))
}, {
    accessorKey: 'total',
    header: 'Montant TTC',
    cell: ({ row }) => h('span', { class: 'font-semibold' }, `${formatPrice(parseFloat(row.original.total), true)} €`)
}, {
    accessorKey: 'status',
    header: 'Statut',
    cell: ({ row }) => {
        return h(UBadge, {
            color: statusColors[row.original.status],
            label: statusLabels[row.original.status],
            variant: 'subtle'
        })
    }
}, {
    id: 'actions',
    cell: ({ row }) => {
        return h(
            'div',
            { class: 'flex items-center gap-1' },
            [
                h(UButton, {
                    icon: 'i-heroicons-eye',
                    color: 'neutral',
                    variant: 'ghost',
                    onClick: () => viewDetails(row.original)
                }),
                (row.original.status === 'draft' || row.original.status === 'issued') ? h(UButton, {
                    icon: 'i-heroicons-pencil',
                    color: 'neutral',
                    variant: 'ghost',
                    onClick: () => openEditModal(row.original)
                }) : null
            ].filter(Boolean)
        )
    }
}]

async function fetchInvoices() {
    try {
        loading.value = true
        // Filtrage côté backend pour les factures standalone uniquement
        const res = await $fetch<Invoice[]>('/api/invoices/?installation__isnull=true', { credentials: 'include' })
        invoices.value = res || []
    } catch (e: any) {
        toast.add({ title: 'Erreur', description: 'Impossible de charger les factures', color: 'error' })
    } finally {
        loading.value = false
    }
}

function openCreateModal() {
    selectedInvoice.value = undefined
    showCreateModal.value = true
}

function openEditModal(invoice: Invoice) {
    selectedInvoice.value = invoice
    showCreateModal.value = true
}

function onInvoiceCreated(invoice: Invoice) {
    navigateTo(`/home/invoices/${invoice.id}`)
}

function onInvoiceUpdated() {
    fetchInvoices()
}

function viewDetails(invoice: Invoice) {
    navigateTo(`/home/invoices/${invoice.id}`)
}

onMounted(() => {
    fetchInvoices()
})
</script>

<template>
    <div>
        <InvoiceStandaloneModal v-model="showCreateModal" :invoice="selectedInvoice" @created="onInvoiceCreated"
            @updated="onInvoiceUpdated" />

        <div class="sticky top-0 z-50 bg-white">
            <UDashboardNavbar title="Facturation" class="lg:text-2xl font-semibold"
                :ui="{ root: 'h-12 lg:h-(--ui-header-height)' }">
                <template #trailing>
                    <UBadge v-if="invoices?.length && invoices.length > 0" variant="subtle">{{ invoices.length }}
                    </UBadge>
                </template>
                <template #right>
                    <UButton color="primary" label="Nouvelle facture" icon="i-heroicons-plus" class="mx-2"
                        @click="openCreateModal" />
                </template>
            </UDashboardNavbar>
            <div class="flex items-center justify-between gap-3 mx-5 py-3 my-1 border-b border-default">
                <div class="flex items-center gap-3">
                    <SearchInput v-model="filters.search" />
                    <USelect v-model="filters.status" :items="statusItems" />
                </div>
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

        <!-- Tableau -->
        <div class="overflow-auto relative mx-5">
            <UTable ref="table" :data="filteredInvoices" :columns="columns" sticky
                class="h-full bg-white shadow-lg rounded-lg" :loading="loading" />
        </div>
    </div>
</template>
