<script setup lang="ts">
import { useAuthStore } from '~/store/auth';
import type { InstallationForm } from '~/types/installations';

const props = defineProps<{
    item: InstallationForm | null
    loading: boolean
}>()
const emit = defineEmits<{
    (e: 'submit'): void
}>()

const route = useRoute()
const auth = useAuthStore()
const invoiceLoading = ref(false)
const openCerfa16702 = ref(false)
const openCerfa16702Attachments = ref(false)
const openElectricalDiagram = ref(false)
const openEnedisMandate = ref(false)
const enedisMandateAction = ref<'full' | 'signature' | 'preview'>('full')
const openInvoice = ref(false)

// Historique des devis: tri et affichage
const sortDirection = ref<'desc' | 'asc'>('desc') // backend renvoie du plus récent au plus ancien
const sortedQuotes = computed(() => {
    const quotes = props.item?.quotes ?? []
    return sortDirection.value === 'desc' ? quotes : [...quotes].reverse()
})
const quoteGridCols = computed(() => Math.min(3, sortedQuotes.value.length || 1))

const manageCerfa16702 = () => {
    if (!props.item?.cerfa16702?.pdf) {
        openCerfa16702.value = true
    }
}

const manageCerfa16702Attachments = () => {
    if (!props.item?.cerfa16702?.attachements_pdf) {
        openCerfa16702Attachments.value = true
    }
}

const manageElectricalDiagram = () => {
    if (!props.item?.electrical_diagram?.file) {
        openElectricalDiagram.value = true
    }
}

const manageEnedisMandate = () => {
    if (!props.item?.enedis_mandate?.pdf) {
        openEnedisMandate.value = true
        enedisMandateAction.value = 'full'
    }
}

const manageInvoice = async () => {
    const toast = useToast()
    if (!props.item?.invoice) {
        invoiceLoading.value = true
        const res = await apiRequest(
            () => $fetch('/api/invoices/', {
                method: 'POST',
                credentials: 'include',
                body: {
                    installation: props.item?.id,
                },
            }), toast
        )
        if (res) {
            emit('submit')
            toast.add({
                title: 'Facture créée avec succès',
                color: 'success'
            })
        }
        invoiceLoading.value = false
    } else {
        openInvoice.value = true
    }
}

const signEnedisMandate = () => {
    openEnedisMandate.value = true
    if (
        (auth.user?.is_staff && !props.item?.enedis_mandate?.installer_signature) ||
        (!auth.user?.is_staff && !props.item?.enedis_mandate?.client_signature)
    ) {
        enedisMandateAction.value = 'signature'
    } else {
        enedisMandateAction.value = 'preview'
    }
}

// Affichage conditionnel de la section "Documents administratifs"
const showAdminDocs = computed(() => !!(auth.user?.is_superuser || (auth.user?.is_staff && auth.user?.useraccess?.administrative_procedures) || !auth.user?.is_staff))

onMounted(() => {
    if (route.query.action === 'sign-enedis-mandate' && props.item?.enedis_mandate) {
        signEnedisMandate()
    }
})
</script>
<template>
    <AdministrativeCerfa16702Modal v-model="openCerfa16702" :form-id="item?.id" @submit="emit('submit')" />
    <AdministrativeCerfa16702AttachmentsModal v-model="openCerfa16702Attachments" :cerfa16702="item?.cerfa16702"
        :form-id="item?.id" @submit="emit('submit')" />
    <AdministrativeElectricalDiagramModal v-model="openElectricalDiagram" :form-id="item?.id"
        @submit="emit('submit')" />
    <AdministrativeEnedisMandateModal v-model="openEnedisMandate" :action="enedisMandateAction"
        :representation-mandate="item?.representation_mandate" :enedis-mandate="item?.enedis_mandate"
        :form-id="item?.id" :form="item" @submit="emit('submit')" />
    <InvoiceModal v-if="item?.offer" v-model="openInvoice" :offer="item?.offer" />
    <UCard class="mt-6">
        <template v-if="!loading">
            <div class="flex flex-col md:flex-row items-start justify-between gap-6">
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
                        <div class="flex flex-col md:flex-row gap-y-4 md:gap-y-2 gap-x-4">
                            <div
                                class="flex flex-row md:flex-col gap-y-2 gap-x-4 md:pr-4 md:border-r-2 md:border-default">
                                <UButton v-if="item?.quotes?.length === 1 && item?.quotes[0]?.pdf" color="primary"
                                    variant="subtle" :icon="'i-heroicons-document-check'" :to="item.quotes[0].pdf"
                                    target="_blank" label="Devis" block />
                                <UPopover v-else mode="hover">
                                    <UButton color="primary" variant="subtle" :icon="'i-heroicons-document-check'"
                                        label="Devis" block />

                                    <template #content>
                                        <div class="p-3">
                                            <div class="flex items-center justify-between mb-2">
                                                <span class="text-sm font-medium">Historique des devis</span>
                                                <div class="flex items-center gap-1">
                                                    <UTooltip text="Plus ancien en premier">
                                                        <UButton size="xs" variant="ghost"
                                                            :color="sortDirection === 'asc' ? 'primary' : 'neutral'"
                                                            icon="i-heroicons-arrow-up"
                                                            @click="sortDirection = 'asc'" />
                                                    </UTooltip>
                                                    <UTooltip text="Plus récent en premier">
                                                        <UButton size="xs" variant="ghost"
                                                            :color="sortDirection === 'desc' ? 'primary' : 'neutral'"
                                                            icon="i-heroicons-arrow-down"
                                                            @click="sortDirection = 'desc'" />
                                                    </UTooltip>
                                                </div>
                                            </div>

                                            <div v-if="sortedQuotes.length" class="grid gap-2"
                                                :style="{ gridTemplateColumns: `repeat(${quoteGridCols}, minmax(0, 1fr))` }">
                                                <a v-for="q in sortedQuotes" :key="q.id" :href="q.pdf || undefined"
                                                    target="_blank"
                                                    class="group flex flex-col items-center justify-center rounded-md border border-default hover:border-primary-500 hover:bg-primary-50/50 transition px-3 py-3 text-xs">
                                                    <UIcon name="i-heroicons-document-text"
                                                        class="mb-1 h-6 w-6 text-gray-500 group-hover:text-primary-500" />
                                                    <span class="truncate max-w-[8rem]">{{ q.number }}</span>
                                                </a>
                                            </div>
                                            <div v-else class="text-xs text-gray-500 px-1 py-2">Aucun devis disponible
                                            </div>
                                        </div>
                                    </template>
                                </UPopover>
                                <UButton :color="item?.invoice ? 'primary' : 'neutral'" variant="subtle"
                                    :icon="item?.invoice ? 'i-heroicons-document-check' : 'i-heroicons-plus'"
                                    label="Facture" block :loading="invoiceLoading" @click="manageInvoice" />
                            </div>
                            <div
                                class="flex flex-row md:flex-col gap-y-2 gap-x-4 md:pr-4 md:border-r-2 md:border-default">
                                <UButton v-if="auth.user?.is_staff" block
                                    :color="props.item?.cerfa16702?.pdf ? 'primary' : 'neutral'" variant="subtle"
                                    :icon="props.item?.cerfa16702?.pdf ? 'i-heroicons-document-check' : 'i-heroicons-plus'"
                                    :to="props.item?.cerfa16702?.pdf || undefined" target="_blank" label="CERFA 16702"
                                    @click="manageCerfa16702" />
                                <UButton v-if="auth.user?.is_staff" block :disabled="!props.item?.cerfa16702"
                                    :color="props.item?.cerfa16702?.attachements_pdf ? 'primary' : 'neutral'"
                                    variant="subtle"
                                    :icon="props.item?.cerfa16702?.attachements_pdf ? 'i-heroicons-document-check' : 'i-heroicons-plus'"
                                    :to="props.item?.cerfa16702?.attachements_pdf || undefined" target="_blank"
                                    label="Pièces jointes" @click="manageCerfa16702Attachments" />
                            </div>
                            <div
                                class="flex flex-row md:flex-col gap-y-2 gap-x-4 md:pr-4 md:border-r-2 md:border-default">
                                <UButton color="neutral" variant="subtle" :icon="'i-heroicons-plus'" label="CONSUEL PDF"
                                    block />
                                <UButton block
                                    v-if="(auth.user?.is_staff && !props.item?.enedis_mandate) || props.item?.enedis_mandate?.pdf"
                                    :color="props.item?.enedis_mandate?.pdf ? 'primary' : 'neutral'" variant="subtle"
                                    :icon="props.item?.enedis_mandate?.pdf ? 'i-heroicons-document-check' : 'i-heroicons-plus'"
                                    :to="props.item?.enedis_mandate?.pdf || undefined" target="_blank"
                                    label="Mandat Enedis" @click="manageEnedisMandate" />
                                <UButton v-if="item?.enedis_mandate && !item?.enedis_mandate?.pdf" color="secondary"
                                    block
                                    :icon="`i-heroicons-${(auth.user?.is_staff && !item?.enedis_mandate?.installer_signature) || (!auth.user?.is_staff && !item?.enedis_mandate?.client_signature) ? 'pencil-square' : 'eye'}`"
                                    :label="(auth.user?.is_staff && !item?.enedis_mandate?.installer_signature) || (!auth.user?.is_staff && !item?.enedis_mandate?.client_signature) ? 'Signer ENEDIS' : 'Aperçu ENEDIS'"
                                    variant="subtle" @click="signEnedisMandate" />
                            </div>
                            <UButton v-if="auth.user?.is_staff" block
                                :color="props.item?.electrical_diagram?.file ? 'primary' : 'neutral'" variant="subtle"
                                label="Schéma électrique"
                                :icon="props.item?.electrical_diagram?.file ? 'i-heroicons-document-check' : 'i-heroicons-plus'"
                                :to="props.item?.electrical_diagram?.file || undefined" target="_blank"
                                @click="manageElectricalDiagram" />

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
                    <div class="flex flex-col md:flex-row gap-2">
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