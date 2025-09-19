<script setup lang="ts">
import { h, resolveComponent } from 'vue'
import type { TableColumn } from '@nuxt/ui'
import type { Row } from '@tanstack/vue-table'
import type { User } from '~/types'
import { getPaginationRowModel } from '@tanstack/vue-table'

definePageMeta({
    middleware: 'admin'
})

const UButton = resolveComponent('UButton')
const UDropdownMenu = resolveComponent('UDropdownMenu')
const UBadge = resolveComponent('UBadge')
const q = ref("")
const formModal = ref(false)
const deactivateModal = ref(false)
const selectedUser = ref<User | undefined>(undefined)
const toast = useToast()
const loading = ref(true)
const activateLoadig = ref(false)
const users = ref<User[] | undefined>([])
const table = useTemplateRef('table')

const attributLabels: { [key: string]: string } = {
    first_name: 'Prénom',
    last_name: 'Nom',
    email: 'Email',
    role: 'Rôle',
    is_active: 'Compte',
    actions: 'Actions'
}

async function fetchUsers() {
    loading.value = true
    const result = await apiRequest<User[]>(
        () => $fetch(`/api/users/?is_staff=true`, {
            credentials: "include"
        }),
        toast
    );
    users.value = result || undefined
    loading.value = false
}

function getRowItems(row: Row<User>) {
    return [
        {
            type: 'label',
            label: 'Actions'
        },
        {
            type: 'separator'
        },
        {
            label: 'Modifier',
            icon: 'i-heroicons-pencil-square',
            onSelect() {
                selectedUser.value = row.original
                formModal.value = true
            }
        },
        {
            label: row.original.is_active ? 'Désactiver' : 'Réactiver',
            color: row.original.is_active ? 'error' : 'success',
            loading: activateLoadig.value,
            icon: `i-heroicons-${row.original.is_active ? 'x-circle' : 'check-circle'}`,
            onSelect() {
                selectedUser.value = row.original
                if (row.original.is_active) {
                    deactivateModal.value = true
                } else {
                    reactivateUser()
                }
            }
        }
    ]
}

const columns: TableColumn<User>[] = [{
    accessorKey: 'last_name',
    header: 'Nom',
    cell: ({ row }) => row.original.last_name
}, {
    accessorKey: 'first_name',
    header: 'Prénom',
    cell: ({ row }) => row.original.first_name
}, {
    accessorKey: 'email',
    header: 'Email',
    cell: ({ row }) => row.original.email
}, {
    accessorKey: 'role',
    header: 'Rôle',
    cell: ({ row }) => {
        const roleLabels = {
            admin: 'Administrateur',
            employee: 'Employé',
            installer: 'Installateur',
            secretary: 'Secrétaire',
            customer: 'Client',
        }
        return roleLabels[row.original.role] || 'Utilisateur'
    }
}, {
    accessorKey: 'is_active',
    header: 'Compte',
    cell: ({ row }) => {
        return h(UBadge,
            {
                color: (!row.original.accept_invitation && row.original.is_active) ? 'warning' : row.original.is_active ? 'success' : 'error',
                label: (!row.original.accept_invitation && row.original.is_active) ? 'En attente' : row.original.is_active ? 'Actif' : 'Inactif',
                variant: 'subtle'
            }
        )
    }
}, {
    accessorKey: 'access',
    header: 'Accès',
    cell: ({ row }) => {
        const accessCount = row.original.useraccess ? Object.values(row.original.useraccess).filter(value => value === true).length : 0
        return row.original.role === 'admin' ? 'Complet' : accessCount > 0 ? `${accessCount} accès` : 'Aucun'
    }
}, {
    id: 'actions',
    cell: ({ row }) => {
        return row.original.role !== 'admin' ? h(
            'div',
            { class: 'text-right' },
            h(
                UDropdownMenu,
                {
                    items: getRowItems(row),
                    'aria-label': 'Actions dropdown'
                },
                () =>
                    h(UButton, {
                        icon: 'i-lucide-ellipsis-vertical',
                        color: 'neutral',
                        variant: 'ghost',
                        class: 'ml-auto',
                        'aria-label': 'Actions dropdown'
                    })
            )
        ) : null
    }
}]

const reactivateUser = async () => {
    if (!selectedUser.value) return;

    activateLoadig.value = true

    const result = await apiRequest(
        () => $fetch(`/api/users/${selectedUser.value?.id}/reactivate/`, {
            method: 'PATCH'
        }),
        toast
    )

    if (result !== null) {
        toast.add({
            title: 'Utilisateur réactivé',
            description: `Le compte de ${selectedUser.value.first_name.split(" ")[0]} ${selectedUser.value.last_name.split(" ")[0]} a été réactivé avec succès.`,
            icon: 'i-heroicons-x-circle',
            color: 'success'
        })
        fetchUsers()
    }

    activateLoadig.value = false
}

const pagination = ref({
    pageIndex: 0,
    pageSize: 10
})

onMounted(fetchUsers)

</script>

<template>
    <UserModal v-model="formModal" :user="selectedUser" @submit="fetchUsers" />
    <UserDeactivateModal v-model="deactivateModal" v-if="selectedUser" :user="selectedUser" @deactivate="fetchUsers" />
    <div class="sticky top-0 z-50 bg-white">
        <UDashboardNavbar title="Utilisateurs" class="lg:text-2xl font-semibold"
            :ui="{ root: 'h-12 lg:h-(--ui-header-height)' }">
            <template #trailing>
                <UBadge v-if="users?.length as number > 0" :label="users?.length" variant="subtle" />
            </template>
            <template #right>
                <UButton color="primary" label="Inviter un utilisateur" icon="i-heroicons-plus" class="mx-2"
                    @click="selectedUser = undefined; formModal = true" />
            </template>
        </UDashboardNavbar>
    </div>
    <UDashboardToolbar>
        <template #left>
            <SearchInput v-model="q" />
        </template>

        <template #right>
            <UDropdownMenu :items="table?.tableApi
                ?.getAllColumns()
                .filter((column) => column.getCanHide())
                .map((column) => ({
                    label: attributLabels[column.id] || 'Inconnu',
                    type: 'checkbox' as const,
                    checked: column.getIsVisible(),
                    onUpdateChecked(checked: boolean) {
                        table?.tableApi?.getColumn(column.id)?.toggleVisibility(!!checked)
                    },
                    onSelect(e?: Event) {
                        e?.preventDefault()
                    }
                }))
                " :content="{ align: 'end' }">
                <UButton label="Afficher" color="neutral" variant="outline" trailing-icon="i-lucide-chevron-down" />
            </UDropdownMenu>
        </template>
    </UDashboardToolbar>
    <div class="w-full px-2 sm:px-6 space-y-4 pb-4">
        <UTable ref="table" :data="users" :columns="columns" v-model:global-filter="q"
            :ui="{ tr: 'data-[expanded=true]:bg-(--ui-bg-elevated)/50' }" class="flex-1" :loading="loading"
            :pagination-options="{ getPaginationRowModel: getPaginationRowModel() }" v-model:pagination="pagination">
        </UTable>

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
</template>