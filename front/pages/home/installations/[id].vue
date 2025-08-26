<script setup lang="ts">
import type { InstallationForm } from '~/types/installations'
import apiRequest from '~/utils/apiRequest'

definePageMeta({ layout: 'default' })

const route = useRoute()
const toast = useToast()

const id = computed(() => route.params.id as string)
const loading = ref(true)
const item = ref<InstallationForm | null>(null)

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
const fmtDateTime = (v?: string | null) => v ? new Date(v).toLocaleString('fr-FR', { dateStyle: 'medium', timeStyle: 'short' }) : ''
const fmtDate = (v?: string | null) => v ? new Date(v).toLocaleDateString('fr-FR', { dateStyle: 'medium' }) : ''

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
        : (!tvSignedClient
            ? "En attente de signature du client."
            : !tvSignedInst
                ? "En attente de signature de l'installateur."
                : "En attente d'informations.")

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

    const items = [
        {
            icon: icons.tv,
            title: 'Visite technique',
            description: tv ? tvDesc : "En attente de planification de la visite technique.",
            date: tv ? fmtDate(tv.visit_date) : '',
            color: tvValid ? 'green' : (tv ? 'amber' : 'gray')
        },
        {
            icon: icons.rm,
            title: 'Mandat représentation',
            description: rm ? rmDesc : "En attente de création du mandat de représentation.",
            date: rm ? fmtDateTime(rm.updated_at) : '',
            color: rmValid ? 'green' : (rm ? 'amber' : 'gray')
        },
        {
            icon: icons.av,
            title: 'Validation des démarches administratives',
            description: av ? avDesc : "En attente de lancement des démarches administratives.",
            date: av ? fmtDateTime(av.validated_at) : '',
            color: avValid ? 'green' : (av ? 'amber' : 'gray')
        },
        {
            icon: icons.ic,
            title: 'Installation effectuée',
            description: ic ? icDesc : "Installation non encore réalisée.",
            date: ic ? fmtDateTime(ic.updated_at) : '',
            color: icValid ? 'green' : (ic ? 'amber' : 'gray')
        },
        {
            icon: icons.cv,
            title: 'Visite CONSUEL',
            description: cv ? cvDesc : "Visite CONSUEL non encore planifiée.",
            date: cv ? fmtDateTime(cv.updated_at) : '',
            color: cvValid ? 'green' : (cv ? 'amber' : 'gray')
        },
        {
            icon: icons.ec,
            title: 'Raccordement ENEDIS',
            description: ec ? ecDesc : "Raccordement ENEDIS non encore validé.",
            date: ec ? fmtDateTime(ec.validated_at) : '',
            color: ecValid ? 'green' : (ec ? 'amber' : 'gray')
        },
        {
            icon: icons.cm,
            title: 'Mise en service',
            description: cm ? cmDesc : "Mise en service non encore effectuée.",
            date: cm ? fmtDateTime(cm.updated_at) : '',
            color: cmValid ? 'green' : (cm ? 'amber' : 'gray')
        },
    ]

    return items
})
</script>

<template>
    <div>
        <div class="sticky top-0 z-50 bg-white">
            <UDashboardNavbar title="Détails de l'installation" class="lg:text-2xl font-semibold"
                :ui="{ root: 'h-12 lg:h-(--ui-header-height)' }" />
        </div>

        <div class="px-4 md:px-6 lg:px-8">
            <UCard class="mt-6">
                <template v-if="!loading">
                    <div class="flex flex-col gap-1">
                        <div class="font-semibold">{{ item?.client_last_name }} {{ item?.client_first_name }}</div>
                        <div class="text-sm text-gray-500">{{ item?.client_address }}</div>
                        <div class="text-xs text-gray-400">Puissance: {{ item?.installation_power }} kWc • {{
                            item?.installation_type }}</div>
                    </div>
                </template>
                <template v-else>
                    <div class="space-y-2">
                        <USkeleton class="h-5 w-48" />
                        <USkeleton class="h-4 w-64" />
                        <USkeleton class="h-3 w-56" />
                    </div>
                </template>
            </UCard>

            <div class="mt-8">
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
                    <UTimeline :items="steps" size="xl" icon="i-heroicons-check-circle" orientation="vertical" />
                </template>
            </div>
        </div>
    </div>
</template>