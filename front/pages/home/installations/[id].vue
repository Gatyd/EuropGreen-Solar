<script setup lang="ts">
import type { InstallationForm } from '~/types/installations'
import apiRequest from '~/utils/apiRequest'
import { useAuthStore } from '~/store/auth'
import InstallationTechnicalVisitModal from '~/components/installation/technicalVisit/Modal.vue'
import InstallationRepresentationMandateModal from '~/components/installation/representationMandate/Modal.vue'

definePageMeta({ layout: 'default' })

const route = useRoute()
const toast = useToast()

const id = computed(() => route.params.id as string)
const loading = ref(true)
const item = ref<InstallationForm | null>(null)
const auth = useAuthStore()
const openTechnicalVisit = ref(false)
const technicalVisitAction = ref<'full' | 'signature' | 'preview'>('full')
const openMandate = ref(false)
const mandateAction = ref<'full' | 'signature' | 'preview'>('full')
const openCompleted = ref(false)
const completedAction = ref<'full' | 'signature' | 'preview'>('full')

const fetchOne = async () => {
    loading.value = true
    const data = await apiRequest<InstallationForm>(
        () => $fetch(`/api/installations/forms/${id.value}/`, { credentials: 'include' }),
        toast
    )
    if (data) item.value = data
    loading.value = false
}

onMounted(fetchOne)

// Helpers d’affichage
const fmtDateTime = (v?: string | null) => v ? new Date(v).toLocaleString('fr-FR', { dateStyle: 'medium', timeStyle: 'short' }) : '';
const fmtDate = (v?: string | null) => v ? new Date(v).toLocaleDateString('fr-FR', { dateStyle: 'medium' }) : '';

const steps = computed(() => {
    const f = item.value
    const tv = f?.technical_visit
    const rm = f?.representation_mandate
    const av = f?.administrative_validation
    const ic = f?.installation_completed
    const cv = f?.consuel_visit
    const ec = f?.enedis_connection
    const cm = f?.commissioning

    const tvSignedClient = !!tv?.client_signature
    const tvSignedInst = !!tv?.installer_signature
    const tvValid = tvSignedClient && tvSignedInst
    const tvDesc = tvValid
        ? "Enregistrement et validation des informations collectées lors de la visite technique sur site."
        : (!tvSignedClient && !tvSignedInst)
            ? "En attente de signature du client et de l'installateur."
            : !tvSignedClient
                ? "En attente de signature du client."
                : !tvSignedInst
                    ? "En attente de signature de l'installateur."
                    : "En attente d'informations."

    const rmSignedClient = !!rm?.client_signature
    const rmSignedInst = !!rm?.installer_signature
    const rmValid = rmSignedClient && rmSignedInst
    const rmDesc = rmValid
        ? "Facilitation de la création, du remplissage et de la signature du mandat de représentation pour les démarches administratives."
        : (!rmSignedClient
            ? "En attente de signature du client."
            : !rmSignedInst
                ? "En attente de signature de l'installateur."
                : "En attente d'informations.")

    const avValid = !!av?.validated_at
    const avDesc = "Suivi de l'état d'avancement des démarches administratives."

    const icSignedClient = !!ic?.client_signature
    const icSignedInst = !!ic?.installer_signature
    const icValid = icSignedClient && icSignedInst
    const icDesc = icValid
        ? "Confirmation de l'installation physique du matériel sur site."
        : (!icSignedClient
            ? "En attente de signature du client."
            : !icSignedInst
                ? "En attente de signature de l'installateur."
                : "En attente d'informations.")

    const cvValid = cv?.passed === true
    const cvDesc = "Suivi du résultat de la visite de conformité CONSUEL."

    const ecValid = !!ec?.validated_at
    const ecDesc = "Suivi de l'état du raccordement au réseau ENEDIS."

    const cmValid = cm?.handover_receipt_given === true
    const cmDesc = cm?.handover_receipt_given
        ? "Procès-verbal de réception remis au client."
        : "Procès-verbal de réception non encore remis au client."

    // Icônes Nuxt UI (Heroicons)
    const icons = {
        tv: 'i-heroicons-clipboard-document-check',
        rm: 'i-heroicons-document-text',
        av: 'i-heroicons-shield-check',
        ic: 'i-heroicons-wrench-screwdriver',
        cv: 'i-heroicons-check-badge',
        ec: 'i-heroicons-bolt',
        cm: 'i-heroicons-rocket-launch',
    }

    // Helper de couleur par statut → applique des classes au composant (indicator + separator)
    const colorUI = (status: 'green' | 'amber' | 'gray') => {
        const map = {
            green: 'bg-green-500 text-white',
            amber: 'bg-amber-500 text-white',
            gray: 'bg-gray-300'
        } as const
        const c = map[status]
        return { indicator: c, separator: c }
    }

    const items = [
        {
            icon: icons.tv,
            title: 'Visite technique',
            description: tv ? tvDesc : "En attente de planification de la visite technique.",
            date: tv ? fmtDate(tv.visit_date) : '',
            ui: colorUI(tvValid ? 'green' : (tv ? 'amber' : 'gray')),
            slot: 'technical-visit'
        },
        {
            icon: icons.rm,
            title: 'Mandat représentation',
            description: rm ? rmDesc : "En attente de création du mandat de représentation.",
            date: rm ? fmtDateTime(rm.updated_at) : '',
            ui: colorUI(rmValid ? 'green' : (rm ? 'amber' : 'gray')),
            slot: 'representation-mandate'
        },
        {
            icon: icons.av,
            title: 'Validation des démarches administratives',
            description: av ? avDesc : "En attente de lancement des démarches administratives.",
            date: av ? fmtDateTime(av.validated_at) : '',
            ui: colorUI(avValid ? 'green' : (av ? 'amber' : 'gray')),
            slot: 'administrative-validation'
        },
        {
            icon: icons.ic,
            title: 'Installation effectuée',
            description: ic ? icDesc : "Installation non encore réalisée.",
            date: ic ? fmtDateTime(ic.updated_at) : '',
            ui: colorUI(icValid ? 'green' : (ic ? 'amber' : 'gray')),
            slot: 'installation-completed'
        },
        {
            icon: icons.cv,
            title: 'Visite CONSUEL',
            description: cv ? cvDesc : "Visite CONSUEL non encore planifiée.",
            date: cv ? fmtDateTime(cv.updated_at) : '',
            ui: colorUI(cvValid ? 'green' : (cv ? 'amber' : 'gray'))
        },
        {
            icon: icons.ec,
            title: 'Raccordement ENEDIS',
            description: ec ? ecDesc : "Raccordement ENEDIS non encore validé.",
            date: ec ? fmtDateTime(ec.validated_at) : '',
            ui: colorUI(ecValid ? 'green' : (ec ? 'amber' : 'gray'))
        },
        {
            icon: icons.cm,
            title: 'Mise en service',
            description: cm ? cmDesc : "Mise en service non encore effectuée.",
            date: cm ? fmtDateTime(cm.updated_at) : '',
            ui: colorUI(cmValid ? 'green' : (cm ? 'amber' : 'gray'))
        },
    ]

    return items
});

</script>

<template>
    <div>
        <div class="sticky top-0 z-50 bg-white">
            <UDashboardNavbar title="Détails de l'installation" class="lg:text-2xl font-semibold"
                :ui="{ root: 'h-12 lg:h-(--ui-header-height)' }" />
        </div>

        <div class="px-4 md:px-6 lg:px-8">
            <InstallationHeader :item="item" :loading="loading" @submit="fetchOne" />
            <div class="xl:me-40 mt-8">
                <template v-if="loading">
                    <div class="flex flex-col gap-6">
                        <div v-for="i in 7" :key="i" class="flex gap-4 items-start">
                            <div class="flex flex-col items-center">
                                <USkeleton class="w-10 h-10 rounded-full" />
                                <div class="w-px bg-gray-200 grow mt-2"></div>
                            </div>
                            <div class="flex-1">
                                <USkeleton class="h-5 w-64 mb-2" />
                                <USkeleton class="h-4 w-96 mb-1" />
                                <USkeleton class="h-3 w-52" />
                            </div>
                        </div>
                    </div>
                </template>
                <template v-else>
                    <UTimeline :items="steps" size="xl" icon="i-heroicons-check-circle" :ui="{ date: 'text-gray-500' }"
                        orientation="vertical">
                        <!-- Slots personnalisés pour la visite technique -->
                        <template #technical-visit-title="{ item: s }">
                            <div class="flex items-center justify-between gap-4">
                                <span class="font-medium">{{ s.title }}</span>
                                <div class="flex items-center gap-2">
                                    <UButton v-if="!item?.technical_visit && auth.user?.is_staff"
                                        icon="i-heroicons-clipboard-document-list" color="primary" size="xs"
                                        label="Effectuer la visite technique"
                                        @click="technicalVisitAction = 'full'; openTechnicalVisit = true" />
                                    <UButton
                                        v-else-if="item?.technical_visit && (auth.user?.is_staff ? !item?.technical_visit?.installer_signature : !item?.technical_visit?.client_signature)"
                                        icon="i-heroicons-pencil-square" color="secondary" size="xs"
                                        :label="auth.user?.is_staff ? 'Signer le rapport (installateur)' : 'Signer le rapport (client)'"
                                        @click="technicalVisitAction = 'signature'; openTechnicalVisit = true" />
                                </div>
                            </div>
                        </template>
                        <template #technical-visit-description="{ item: s }">
                            <div class="flex flex-col md:flex-row gap-4 md:items-center">
                                <span class="text-sm text-gray-600">{{ s.description }}</span>
                                <div class="flex items-center gap-3 md:ml-auto">
                                    <UButton v-if="item?.technical_visit && !item?.technical_visit?.report_pdf"
                                        variant="ghost" size="xs" color="neutral" icon="i-heroicons-eye" label="Aperçu"
                                        @click="technicalVisitAction = 'preview'; openTechnicalVisit = true" />
                                    <UButton v-else-if="item?.technical_visit?.report_pdf" variant="ghost" size="xs"
                                        color="neutral" icon="i-heroicons-clipboard-document-check" target="_blank"
                                        label="Voir le rapport" :to="item.technical_visit.report_pdf" />
                                </div>
                            </div>
                        </template>

                        <!-- Slots personnalisés pour le mandat de représentation -->
                        <template #representation-mandate-title="{ item: s }">
                            <div class="flex items-center justify-between gap-4">
                                <span class="font-medium">{{ s.title }}</span>
                                <div class="flex items-center gap-2">
                                    <UButton
                                        v-if="item?.technical_visit && !item?.representation_mandate && auth.user?.is_staff"
                                        icon="i-heroicons-document-plus" color="primary" size="xs"
                                        label="Créer le mandat" @click="mandateAction = 'full'; openMandate = true" />
                                    <UButton
                                        v-else-if="item?.technical_visit && item?.representation_mandate && (auth.user?.is_staff ?
                                            !item?.representation_mandate?.installer_signature : !item?.representation_mandate?.client_signature)"
                                        icon="i-heroicons-pencil-square" color="secondary" size="xs"
                                        :label="auth.user?.is_staff ? 'Signer le mandat (installateur)' : 'Signer le mandat (client)'"
                                        @click="mandateAction = 'signature'; openMandate = true" />
                                </div>
                            </div>
                        </template>
                        <template #representation-mandate-description="{ item: s }">
                            <div class="flex flex-col md:flex-row gap-4 md:items-center">
                                <span class="text-sm text-gray-600">{{ s.description }}</span>
                                <div class="flex items-center gap-3 md:ml-auto">
                                    <UButton
                                        v-if="item?.representation_mandate && !item?.representation_mandate?.mandate_pdf"
                                        variant="ghost" size="xs" color="neutral" icon="i-heroicons-eye" label="Aperçu"
                                        @click="mandateAction = 'preview'; openMandate = true" />
                                    <UButton v-else-if="item?.representation_mandate?.mandate_pdf" variant="ghost"
                                        size="xs" color="neutral" icon="i-heroicons-clipboard-document" target="_blank"
                                        label="Voir le mandat" :to="item.representation_mandate.mandate_pdf" />
                                </div>
                            </div>
                        </template>

                        <!-- Slots personnalisés pour la validation des documents administratifs -->
                        <template #administrative-validation-title="{ item: s }">
                            <div class="flex flex-col md:flex-row md:items-center justify-between md:gap-4">
                                <span class="font-medium">{{ s.title }}</span>
                                <div class="flex items-center py-2 md:py-0 gap-2">
                                    <InstallationAdministrativeValidationPopover :form-id="item?.id" @submit="fetchOne"
                                        v-if="((item?.representation_mandate && !item?.administrative_validation) ||
                                            (item?.representation_mandate && item?.administrative_validation &&
                                                !item?.administrative_validation.is_validated)) && auth.user?.is_staff" />
                                </div>
                            </div>
                        </template>

                        <!-- Slots personnalisés pour l'installation effectuée -->
                        <template #installation-completed-title="{ item: s }">
                            <div class="flex items-center justify-between gap-4">
                                <span class="font-medium">{{ s.title }}</span>
                                <div class="flex items-center gap-2">
                                    <UButton
                                        v-if="item?.administrative_validation && !item.installation_completed && auth.user?.is_staff"
                                        icon="i-heroicons-clipboard-document-list" color="primary" size="xs"
                                        label="Effectuer l'installation"
                                        @click="completedAction = 'full'; openCompleted = true" />
                                    <UButton
                                        v-else-if="item?.installation_completed && (auth.user?.is_staff ? !item?.installation_completed?.installer_signature : !item?.installation_completed?.client_signature)"
                                        icon="i-heroicons-pencil-square" color="secondary" size="xs"
                                        :label="auth.user?.is_staff ? 'Signer le rapport (installateur)' : 'Signer le rapport (client)'"
                                        @click="completedAction = 'signature'; openCompleted = true" />
                                </div>
                            </div>
                        </template>
                        <template #installation-completed-description="{ item: s }">
                            <div class="flex flex-col md:flex-row gap-4 md:items-center">
                                <span class="text-sm text-gray-600">{{ s.description }}</span>
                                <div class="flex items-center gap-3 md:ml-auto">
                                    <UButton
                                        v-if="item?.installation_completed && !item?.installation_completed?.report_pdf"
                                        variant="ghost" size="xs" color="neutral" icon="i-heroicons-eye" label="Aperçu"
                                        @click="completedAction = 'preview'; openCompleted = true" />
                                    <UButton v-else-if="item?.installation_completed?.report_pdf" variant="ghost"
                                        size="xs" color="neutral" icon="i-heroicons-clipboard-document-check"
                                        target="_blank" label="Voir le rapport"
                                        :to="item.installation_completed.report_pdf" />
                                </div>
                            </div>
                        </template>
                    </UTimeline>
                </template>
            </div>
            <InstallationTechnicalVisitModal v-model="openTechnicalVisit" :form-id="item?.id" @submit="fetchOne"
                :action="technicalVisitAction" :technical-visit="item?.technical_visit" />
            <InstallationRepresentationMandateModal v-model="openMandate" :form-id="item?.id" @submit="fetchOne"
                :action="mandateAction" :form="item" :mandate="item?.representation_mandate" />
            <InstallationCompletedModal v-model="openCompleted" :form-id="item?.id" @submit="fetchOne"
                :action="completedAction" :installation-completed="item?.installation_completed" />
        </div>
    </div>
</template>