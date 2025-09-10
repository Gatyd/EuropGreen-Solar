<script setup lang="ts">
import type { Installment } from '~/types/billing'
import { formatPrice } from '~/utils/formatPrice'
import { useAuthStore } from '~/store/auth'

const props = defineProps<{ installment: Installment }>()

const auth = useAuthStore()

const typeLabel: Record<string, string> = {
    deposit: 'Acompte',
    milestone: 'Échéance',
    balance: 'Solde'
}

</script>

<template>
    <div class="rounded-md border border-gray-200 bg-white shadow-sm p-3 text-sm flex flex-col gap-1">
        <div class="flex justify-between items-start gap-2">
            <span class="font-medium truncate" :title="installment.label">{{ installment.label }}</span>
            <UBadge :color="installment.is_paid ? 'success' : 'warning'" variant="subtle" size="sm">
                {{ installment.is_paid ? 'Payée' : 'Non payée' }}
            </UBadge>
        </div>
        <div class="flex items-center justify-between">
            <div class="flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-600 dark:text-gray-400">
                <span v-if="installment.percentage">{{ installment.percentage }}%</span>
                <span v-if="installment.amount">{{ formatPrice(Number(installment.amount)) }}</span>
                <span v-if="installment.due_date">Échéance: {{ installment.due_date }}</span>
                <span class="uppercase tracking-wide text-[10px] text-gray-400">{{ typeLabel[installment.type] ||
                    installment.type }}</span>
            </div>
            <div v-if="auth.user?.is_superuser" class="flex items-center gap-1 ml-1">
                <UButton size="xs" variant="ghost" icon="i-heroicons-pencil-square" color="secondary"
                    aria-label="Modifier" />
                <UButton size="xs" variant="ghost" icon="i-heroicons-trash" color="error" aria-label="Supprimer" />
            </div>
        </div>
    </div>
</template>
