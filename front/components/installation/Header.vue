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
const openCerfa16702 = ref(false)
const openElectricalDiagram = ref(false)
const openEnedisMandate = ref(false)
const enedisMandateAction = ref<'full' | 'signature' | 'preview'>('full')

const manageCerfa16702 = () => {
    if (!props.item?.cerfa16702?.pdf) {
        openCerfa16702.value = true
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
    <AdministrativeElectricalDiagramModal v-model="openElectricalDiagram" :form-id="item?.id"
        @submit="emit('submit')" />
    <AdministrativeEnedisMandateModal v-model="openEnedisMandate" :action="enedisMandateAction"
        :representation-mandate="item?.representation_mandate" :enedis-mandate="item?.enedis_mandate"
        :form-id="item?.id" :form="item" @submit="emit('submit')" />
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
                        <div class="flex flex-col md:flex-row gap-2">
                            <UButton v-if="props.item?.quote?.pdf" color="primary" variant="subtle"
                                :icon="'i-heroicons-document-check'" :to="props.item.quote.pdf" target="_blank"
                                label="Devis" />
                            <UButton v-if="auth.user?.is_staff"
                                :color="props.item?.cerfa16702?.pdf ? 'primary' : 'neutral'" variant="subtle"
                                :icon="props.item?.cerfa16702?.pdf ? 'i-heroicons-document-check' : 'i-heroicons-plus'"
                                :to="props.item?.cerfa16702?.pdf || undefined" target="_blank" label="CERFA 16702"
                                @click="manageCerfa16702" />
                            <UButton v-if="auth.user?.is_staff"
                                :color="props.item?.electrical_diagram?.file ? 'primary' : 'neutral'" variant="subtle"
                                label="Schéma électrique"
                                :icon="props.item?.electrical_diagram?.file ? 'i-heroicons-document-check' : 'i-heroicons-plus'"
                                :to="props.item?.electrical_diagram?.file || undefined" target="_blank"
                                @click="manageElectricalDiagram" />
                            <UButton v-if="(auth.user?.is_staff && !props.item?.enedis_mandate) || props.item?.enedis_mandate?.pdf"
                                :color="props.item?.enedis_mandate?.pdf ? 'primary' : 'neutral'" variant="subtle"
                                :icon="props.item?.enedis_mandate?.pdf ? 'i-heroicons-document-check' : 'i-heroicons-plus'"
                                :to="props.item?.enedis_mandate?.pdf || undefined" target="_blank" label="Mandat Enedis"
                                @click="manageEnedisMandate" />
                            <UButton v-if="item?.enedis_mandate && !item?.enedis_mandate?.pdf" color="secondary"
                                :icon="`i-heroicons-${(auth.user?.is_staff && !item?.enedis_mandate?.installer_signature) || (!auth.user?.is_staff && !item?.enedis_mandate?.client_signature) ? 'pencil-square' : 'eye'}`"
                                :label="(auth.user?.is_staff && !item?.enedis_mandate?.installer_signature) || (!auth.user?.is_staff && !item?.enedis_mandate?.client_signature) ? 'Signer ENEDIS' : 'Aperçu ENEDIS'"
                                variant="subtle" @click="signEnedisMandate" />
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