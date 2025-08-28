<script setup lang="ts">
import { useAuthStore } from '~/store/auth';
import type { InstallationForm } from '~/types/installations';

const props = defineProps<{
    item: InstallationForm | null
    loading: boolean
}>()

const auth = useAuthStore()

// Affichage conditionnel de la section "Documents administratifs"
const showAdminDocs = computed(() => !!(auth.user?.is_superuser || auth.user?.useraccess?.administrative_procedures))

const administrativeButtons = computed(() => [
    {
        label: 'Devis',
        document: props.item?.quote ? { pdf: props.item.quote.pdf } : undefined,
        createAction: () => console.log('create-quote')
    },
    {
        label: 'CERFA 16702',
        document: props.item?.cerfa16702 ? { pdf: props.item.cerfa16702.pdf } : undefined,
        createAction: () => console.log('create-cerfa')
    },
    {
        label: 'Schéma électrique',
        document: props.item?.electrical_diagram ? { file: props.item.electrical_diagram.file } : undefined,
        createAction: () => console.log('create-diagram')
    },
    {
        label: 'Mandat Enedis',
        document: props.item?.enedis_mandate ? { pdf: props.item.enedis_mandate.pdf } : undefined,
        createAction: () => console.log('create-enedis-mandate')
    },
])
</script>
<template>
    <UCard class="mt-6">
        <template v-if="!loading">
            <div class="flex items-start justify-between gap-6">
                <!-- Infos installation (gauche) -->
                <div class="flex flex-col gap-1">
                    <div class="font-semibold">{{ item?.client_last_name }} {{ item?.client_first_name }}</div>
                    <div class="text-sm text-gray-500">{{ item?.client_address }}</div>
                    <div class="text-xs text-gray-400">Puissance: {{ item?.installation_power }} kWc • {{
                        item?.installation_type }}</div>
                </div>

                <!-- Documents administratifs (droite, boutons sur une ligne) -->
                <div v-if="showAdminDocs" class="w-full sm:w-auto">
                    <div class="flex flex-col">
                        <div class="text-sm font-semibold mb-2">Documents administratifs</div>
                        <div class="flex flex-row gap-2">
                            <UButton v-for="button in administrativeButtons" :key="button.label"
                                :color="button.document?.pdf || button.document?.file ? 'primary' : 'neutral'"
                                variant="subtle"
                                :icon="button.document?.pdf || button.document?.file ? 'i-heroicons-document-check' : 'i-heroicons-plus'"
                                :to="button.document?.pdf || button.document?.file || undefined" target="_blank"
                                @click="button.createAction">
                                {{ button.label }}
                            </UButton>
                        </div>
                    </div>
                </div>
            </div>
        </template>
        <template v-else>
            <div class="flex items-start justify-between gap-6">
                <div class="space-y-2">
                    <USkeleton class="h-5 w-48" />
                    <USkeleton class="h-4 w-64" />
                    <USkeleton class="h-3 w-56" />
                </div>
                <div v-if="showAdminDocs" class="w-full sm:w-64">
                    <div class="text-sm font-semibold mb-2">Documents administratifs</div>
                    <div class="flex flex-col gap-2">
                        <USkeleton class="h-9 w-full" />
                        <USkeleton class="h-9 w-full" />
                        <USkeleton class="h-9 w-full" />
                        <USkeleton class="h-9 w-full" />
                    </div>
                </div>
            </div>
        </template>
    </UCard>
</template>