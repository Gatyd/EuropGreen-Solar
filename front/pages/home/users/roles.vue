<template>
    <div>
        <div class="sticky top-0 z-50 bg-white">
            <UDashboardNavbar title="Roles" class="lg:text-2xl font-semibold"
                :ui="{ root: 'h-12 lg:h-(--ui-header-height)' }">
                <template #trailing>
                    <UBadge v-if="roles?.length as number > 0" :label="roles?.length" variant="subtle" />
                </template>
                <template #right>
                    <UButton label="Nouveau rôle" icon="i-heroicons-plus" color="primary" @click="openCreateModal" />
                </template>
            </UDashboardNavbar>
        </div>
        <UDashboardToolbar>
            <template #left>
                <SearchInput v-model="q" />
            </template>
            <template #right>
                <UDropdownMenu :items="table?.tableApi?.getAllColumns().filter(c => c.getCanHide()).map(c => ({
                    label: getColumnLabel(c.id),
                    type: 'checkbox' as const,
                    checked: c.getIsVisible(),
                    onUpdateChecked(checked: boolean) {
                        table?.tableApi?.getColumn(c.id)?.toggleVisibility(!!checked)
                    },
                    onSelect(e?: Event) {
                        e?.preventDefault()
                    }
                }))" :content="{ align: 'end' }">
                    <UButton label="Afficher" color="neutral" variant="outline" trailing-icon="i-lucide-chevron-down"
                        class="ml-2" />
                </UDropdownMenu>
            </template>
        </UDashboardToolbar>

        <div class="w-full px-2 sm:px-6 space-y-4 pb-4">
            <UTable ref="table" :data="roles" :columns="columns" v-model:global-filter="q" :loading="loading"
                :pagination-options="{ getPaginationRowModel: getPaginationRowModel() }"
                v-model:pagination="pagination" />

            <div
                class="flex flex-col md:flex-row justify-center gap-4 md:gap-0 items-center md:justify-between border-t border-(--ui-border) pt-4">
                <UFormField :ui="{ root: 'flex items-center' }" label="Lignes par page : ">
                    <USelectMenu class="w-20 ms-3" :search-input="false" :items="[10, 20, 30, 40, 50]"
                        v-model="pagination.pageSize" @update:model-value="(p) => table?.tableApi?.setPageSize(p)" />
                </UFormField>
                <UPagination :default-page="(table?.tableApi?.getState().pagination.pageIndex || 0) + 1"
                    :items-per-page="table?.tableApi?.getState().pagination.pageSize"
                    :total="table?.tableApi?.getFilteredRowModel().rows.length"
                    @update:page="(p) => table?.tableApi?.setPageIndex(p - 1)" />
            </div>
        </div>

        <!-- Modal création / édition -->
        <UserRoleModal v-model="showModal" :role="selectedRole" @created="onRoleCreated" @updated="onRoleUpdated" />

        <!-- Modal suppression -->
        <UserRoleDeleteModal v-model="showDeleteModal" :role="roleToDelete" @deleted="onRoleDeleted" />
    </div>
</template>

<script setup lang="ts">
import { h, resolveComponent } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import type { Role } from '~/types'
import { getPaginationRowModel } from '@tanstack/vue-table'

const UBadge = resolveComponent('UBadge')
const UButton = resolveComponent('UButton')
const UTooltip = resolveComponent('UTooltip')

const toast = useToast()
const loading = ref(true)
const roles = ref<Role[]>([])
const q = ref("")
const table = useTemplateRef('table')

// État des modals
const showModal = ref(false)
const selectedRole = ref<Role | null>(null)
const showDeleteModal = ref(false)
const roleToDelete = ref<Role | null>(null)

const accessLabels: Record<string, string> = {
    name: 'Nom',
    installation: 'Installations',
    offers: 'Offres',
    requests: 'Demandes',
    administrative_procedures: 'Démarches administratives',
    actions: 'Actions'
}

const getColumnLabel = (columnId: string): string => {
    return accessLabels[columnId] || columnId
}

async function fetchRoles() {
    loading.value = true
    const result = await apiRequest<Role[]>(
        () => $fetch('/api/roles/', { credentials: 'include' }),
        toast
    )
    roles.value = result || []
    loading.value = false
}

function openCreateModal() {
    selectedRole.value = null
    showModal.value = true
}

function openEditModal(role: Role) {
    selectedRole.value = role
    showModal.value = true
}

function openDeleteModal(role: Role) {
    roleToDelete.value = role
    showDeleteModal.value = true
}

function onRoleCreated(role: Role) {
    roles.value.push(role)
}

function onRoleUpdated(updatedRole: Role) {
    const index = roles.value.findIndex(r => r.id === updatedRole.id)
    if (index !== -1) {
        roles.value[index] = updatedRole
    }
}

function onRoleDeleted(deletedRole: Role) {
    const index = roles.value.findIndex(r => r.id === deletedRole.id)
    if (index !== -1) {
        roles.value.splice(index, 1)
    }
}

const columns: TableColumn<Role>[] = [
    {
        accessorKey: 'name',
        header: 'Nom',
        cell: ({ row }) => row.original.name
    },
    {
        id: 'installation',
        header: 'Installations',
        cell: ({ row }) => h(UBadge as any, {
            color: row.original.installation ? 'success' : 'neutral',
            variant: 'subtle',
            label: row.original.installation ? 'Oui' : 'Non'
        })
    },
    {
        id: 'offers',
        header: 'Offres',
        cell: ({ row }) => h(UBadge as any, {
            color: row.original.offers ? 'success' : 'neutral',
            variant: 'subtle',
            label: row.original.offers ? 'Oui' : 'Non'
        })
    },
    {
        id: 'requests',
        header: 'Demandes',
        cell: ({ row }) => h(UBadge as any, {
            color: row.original.requests ? 'success' : 'neutral',
            variant: 'subtle',
            label: row.original.requests ? 'Oui' : 'Non'
        })
    },
    {
        id: 'administrative_procedures',
        header: 'Démarches administratives',
        cell: ({ row }) => h(UBadge as any, {
            color: row.original.administrative_procedures ? 'success' : 'neutral',
            variant: 'subtle',
            label: row.original.administrative_procedures ? 'Oui' : 'Non'
        })
    },
    {
        id: 'actions',
        header: 'Actions',
        cell: ({ row }) => h('div', { class: 'space-x-2' }, [
            h(UTooltip, { text: 'Modifier', delayDuration: 0 }, () =>
                h(UButton as any, {
                    color: 'secondary',
                    variant: 'ghost',
                    icon: 'i-heroicons-pencil-square',
                    onClick: () => openEditModal(row.original)
                })
            ),
            h(UTooltip, { text: 'Supprimer', delayDuration: 0 }, () =>
                h(UButton as any, {
                    color: 'error',
                    variant: 'ghost',
                    icon: 'i-heroicons-trash',
                    onClick: () => openDeleteModal(row.original)
                })
            )
        ])
    }
]

const pagination = ref({ pageIndex: 0, pageSize: 10 })

onMounted(fetchRoles)
</script>