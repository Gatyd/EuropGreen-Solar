<script setup lang="ts">
import type { Payment } from '~/types/billing'
import { formatPrice } from '~/utils/formatPrice'
import { useAuthStore } from '~/store/auth'

const props = defineProps<{ payment: Payment }>()

const emit = defineEmits<{
    (e: 'update', item: Payment): void
    (e: 'delete', item: Payment): void
}>()

const auth = useAuthStore()
</script>

<template>
    <div class="rounded-md border border-gray-200 bg-white shadow-sm p-3 text-sm flex flex-col gap-1">
        <div class="flex justify-between items-start gap-2">
            <span class="font-medium">Paiement</span>
            <UBadge color="primary" variant="subtle" size="sm">{{ payment.date }}</UBadge>
        </div>
        <div class="flex items-center justify-between">
            <div class="flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-600 dark:text-gray-400">
                <span>{{ formatPrice(Number(payment.amount)) }}</span>
                <span v-if="payment.method">{{ payment.method }}</span>
                <span v-if="payment.reference">Ref: {{ payment.reference }}</span>
                <span v-if="payment.installment">Lié échéance</span>
                <UPopover v-if="payment.notes" mode="hover" :popper="{ placement: 'bottom-start' }">
                    <template #default>
                        <span class="cursor-pointer text-gray-700 hover:underline underline-offset-2 decoration-dotted">
                            {{ payment.notes.length > 20 ? `${payment.notes.slice(0, 20)}…` : payment.notes }}
                        </span>
                    </template>
                    <template #content>
                        <div class="max-w-sm whitespace-pre-wrap text-sm p-2">{{ payment.notes || '—' }}</div>
                    </template>
                </UPopover>
            </div>
            <div v-if="auth.user?.is_superuser" class="flex items-center gap-1 ml-1">
                <UButton size="xs" variant="ghost" icon="i-heroicons-pencil-square" color="secondary"
                    aria-label="Modifier" @click="emit('update', payment)" />
                <UButton size="xs" variant="ghost" icon="i-heroicons-trash" color="error" aria-label="Supprimer"
                    @click="emit('delete', payment)" />
            </div>
        </div>
    </div>
</template>
