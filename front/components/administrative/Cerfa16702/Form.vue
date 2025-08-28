<script setup lang="ts">
import { useAuthStore } from '~/store/auth'
import SignatureField from '~/components/common/SignatureField.vue'
import type { DeclarantType } from '~/types/installations'

type cerfa16702Draft = {
    declarant_type: DeclarantType,
    last_name: string,
    first_name: string,
    birth_date: string,
    birth_place: string,
    birth_department: string,
    birth_country: string,
    address_street: string,
    address_number: string,
    address_lieu_dit: string,
    address_locality: string,
    address_postal_code: string,
    address_bp: string,
    address_cedex: string,
    phone_country_code: string,
    phone: string,
    email: string,
    email_consent: boolean,
    land_street: string,
    land_number: string,
    land_lieu_dit: string,
    land_locality: string,
    land_postal_code: string,
    cadastral_prefix: string,
    cadastral_section: string,
    cadastral_number: string,
    cadastral_surface_m2: number | null,
    project_new_construction: boolean,
    project_existing_works: boolean,
    project_description: string,
    destination_primary_residence: boolean,
    destination_secondary_residence: boolean,
    agrivoltaic_project: boolean,
    electrical_power_text: string,
    peak_power_text: string,
    energy_destination: string,
    protection_site_patrimonial: boolean,
    protection_site_classe_or_instance: boolean,
    protection_monument_abords: boolean,
    engagement_city: string,
    engagement_date: string,
    declarant_signature: { signer_name: string, method: 'draw' | 'upload', dataUrl: string, file: File | null },
    declarant_signature_image_url: string | null,
    declarant_signature_signed_at: string | null,
    dpc1: File | null,
    dpc2: File | null,
    dpc3: File | null,
    dpc4: File | null,
    dpc5: File | null,
    dpc6: File | null,
    dpc7: File | null,
    dpc8: File | null,
    dpc11: File | null,
    dpc11_notice_materiaux: string
}

const props = defineProps<{ draft: cerfa16702Draft, formId?: string }>()
const emit = defineEmits<{
    (e: 'submit'): void
}>()

const state = toRef(props, 'draft')
const loading = ref(false)

const auth = useAuthStore()

// Validation globale
const validate = (s: cerfa16702Draft) => {
    const errors: { name: string; message: string }[] = []

    // Identité du déclarant
    if (!s.declarant_type) errors.push({ name: 'declarant_type', message: 'Type de déclarant requis.' })
    if (!s.last_name.trim()) errors.push({ name: 'last_name', message: 'Nom requis.' })
    if (!s.first_name.trim()) errors.push({ name: 'first_name', message: 'Prénom requis.' })
    if (s.declarant_type === 'individual') {
        if (!s.birth_date) errors.push({ name: 'birth_date', message: 'Date de naissance requise.' })
        if (!s.birth_place.trim()) errors.push({ name: 'birth_place', message: 'Lieu de naissance requis.' })
        if (!s.birth_department.trim()) errors.push({ name: 'birth_department', message: 'Département de naissance requis.' })
        if (!s.birth_country.trim()) errors.push({ name: 'birth_country', message: 'Pays de naissance requis.' })
    }

    // Coordonnées
    if (!s.address_street.trim()) errors.push({ name: 'address_street', message: 'Rue requise.' })
    if (!s.address_locality.trim()) errors.push({ name: 'address_locality', message: 'Localité requise.' })
    if (!s.address_postal_code.trim()) errors.push({ name: 'address_postal_code', message: 'Code postal requis.' })
    if (!s.phone.trim()) errors.push({ name: 'phone', message: 'Téléphone requis.' })

    // Terrain
    if (!s.land_street.trim()) errors.push({ name: 'land_street', message: 'Rue du terrain requise.' })
    if (!s.land_locality.trim()) errors.push({ name: 'land_locality', message: 'Localité du terrain requise.' })
    if (!s.land_postal_code.trim()) errors.push({ name: 'land_postal_code', message: 'Code postal du terrain requis.' })

    // Projet
    if (!s.project_new_construction && !s.project_existing_works) {
        errors.push({ name: 'project_type', message: 'Sélectionnez au moins un type de projet.' })
    }
    if (!s.project_description.trim()) errors.push({ name: 'project_description', message: 'Description du projet requise.' })
    if (!s.destination_primary_residence && !s.destination_secondary_residence) {
        errors.push({ name: 'destination', message: 'Sélectionnez au moins une destination.' })
    }

    // Engagement
    if (!s.engagement_city.trim()) errors.push({ name: 'engagement_city', message: 'Ville d\'engagement requise.' })
    if (!s.engagement_date) errors.push({ name: 'engagement_date', message: 'Date d\'engagement requise.' })

    // Signature
    if (!s.declarant_signature.signer_name.trim()) {
        errors.push({ name: 'declarant_signature.signer_name', message: 'Nom du signataire requis.' })
    }

    return errors
}

async function onSubmit() {
    const toast = useToast()
    loading.value = true

    if (!props.formId) {
        toast.add({ title: 'Formulaire manquant', description: 'Impossible de soumettre sans ID de fiche.', color: 'error' })
        loading.value = false
        return
    }

    try {
        // Création/MàJ du CERFA 16702
        const s = props.draft
        const hasFiles = s.dpc1 || s.dpc2 || s.dpc3 || s.dpc4 || s.dpc5 || s.dpc6 || s.dpc7 || s.dpc8 || s.dpc11

        if (!hasFiles) {
            // JSON simple
            const payload = {
                declarant_type: s.declarant_type,
                last_name: s.last_name,
                first_name: s.first_name,
                birth_date: s.birth_date,
                birth_place: s.birth_place,
                birth_department: s.birth_department,
                birth_country: s.birth_country,
                address_street: s.address_street,
                address_number: s.address_number,
                address_lieu_dit: s.address_lieu_dit,
                address_locality: s.address_locality,
                address_postal_code: s.address_postal_code,
                address_bp: s.address_bp,
                address_cedex: s.address_cedex,
                phone_country_code: s.phone_country_code,
                phone: s.phone,
                email: s.email,
                email_consent: s.email_consent,
                land_street: s.land_street,
                land_number: s.land_number,
                land_lieu_dit: s.land_lieu_dit,
                land_locality: s.land_locality,
                land_postal_code: s.land_postal_code,
                cadastral_prefix: s.cadastral_prefix,
                cadastral_section: s.cadastral_section,
                cadastral_number: s.cadastral_number,
                cadastral_surface_m2: s.cadastral_surface_m2,
                project_new_construction: s.project_new_construction,
                project_existing_works: s.project_existing_works,
                project_description: s.project_description,
                destination_primary_residence: s.destination_primary_residence,
                destination_secondary_residence: s.destination_secondary_residence,
                agrivoltaic_project: s.agrivoltaic_project,
                electrical_power_text: s.electrical_power_text,
                peak_power_text: s.peak_power_text,
                energy_destination: s.energy_destination,
                protection_site_patrimonial: s.protection_site_patrimonial,
                protection_site_classe_or_instance: s.protection_site_classe_or_instance,
                protection_monument_abords: s.protection_monument_abords,
                engagement_city: s.engagement_city,
                engagement_date: s.engagement_date,
                declarant_signer_name: s.declarant_signature.signer_name,
                declarant_signature_data: s.declarant_signature.dataUrl,
                dpc11_notice_materiaux: s.dpc11_notice_materiaux,
            }
            await $fetch(`/api/installations/forms/${props.formId}/cerfa16702/`, {
                method: 'POST',
                credentials: 'include',
                body: payload,
            })
        } else {
            // FormData si fichiers présents
            const fd = new FormData()
            fd.append('declarant_type', s.declarant_type)
            fd.append('last_name', s.last_name)
            fd.append('first_name', s.first_name)
            if (s.birth_date) fd.append('birth_date', s.birth_date)
            fd.append('birth_place', s.birth_place)
            fd.append('birth_department', s.birth_department)
            fd.append('birth_country', s.birth_country)
            fd.append('address_street', s.address_street)
            fd.append('address_number', s.address_number)
            fd.append('address_lieu_dit', s.address_lieu_dit)
            fd.append('address_locality', s.address_locality)
            fd.append('address_postal_code', s.address_postal_code)
            fd.append('address_bp', s.address_bp)
            fd.append('address_cedex', s.address_cedex)
            fd.append('phone_country_code', s.phone_country_code)
            fd.append('phone', s.phone)
            fd.append('email', s.email)
            fd.append('email_consent', s.email_consent ? '1' : '0')
            fd.append('land_street', s.land_street)
            fd.append('land_number', s.land_number)
            fd.append('land_lieu_dit', s.land_lieu_dit)
            fd.append('land_locality', s.land_locality)
            fd.append('land_postal_code', s.land_postal_code)
            fd.append('cadastral_prefix', s.cadastral_prefix)
            fd.append('cadastral_section', s.cadastral_section)
            fd.append('cadastral_number', s.cadastral_number)
            if (s.cadastral_surface_m2 !== null) fd.append('cadastral_surface_m2', String(s.cadastral_surface_m2))
            fd.append('project_new_construction', s.project_new_construction ? '1' : '0')
            fd.append('project_existing_works', s.project_existing_works ? '1' : '0')
            fd.append('project_description', s.project_description)
            fd.append('destination_primary_residence', s.destination_primary_residence ? '1' : '0')
            fd.append('destination_secondary_residence', s.destination_secondary_residence ? '1' : '0')
            fd.append('agrivoltaic_project', s.agrivoltaic_project ? '1' : '0')
            fd.append('electrical_power_text', s.electrical_power_text)
            fd.append('peak_power_text', s.peak_power_text)
            fd.append('energy_destination', s.energy_destination)
            fd.append('protection_site_patrimonial', s.protection_site_patrimonial ? '1' : '0')
            fd.append('protection_site_classe_or_instance', s.protection_site_classe_or_instance ? '1' : '0')
            fd.append('protection_monument_abords', s.protection_monument_abords ? '1' : '0')
            fd.append('engagement_city', s.engagement_city)
            fd.append('engagement_date', s.engagement_date)
            if (s.declarant_signature.signer_name) {
                fd.append('declarant_signer_name', s.declarant_signature.signer_name)
                if (s.declarant_signature.file) fd.append('declarant_signature_file', s.declarant_signature.file)
                else if (s.declarant_signature.dataUrl) fd.append('declarant_signature_data', s.declarant_signature.dataUrl)
            }
            fd.append('dpc11_notice_materiaux', s.dpc11_notice_materiaux)

            // Pièces jointes
            if (s.dpc1) fd.append('dpc1', s.dpc1)
            if (s.dpc2) fd.append('dpc2', s.dpc2)
            if (s.dpc3) fd.append('dpc3', s.dpc3)
            if (s.dpc4) fd.append('dpc4', s.dpc4)
            if (s.dpc5) fd.append('dpc5', s.dpc5)
            if (s.dpc6) fd.append('dpc6', s.dpc6)
            if (s.dpc7) fd.append('dpc7', s.dpc7)
            if (s.dpc8) fd.append('dpc8', s.dpc8)
            if (s.dpc11) fd.append('dpc11', s.dpc11)

            const res = await $fetch(`/api/installations/forms/${props.formId}/cerfa16702/`, {
                method: 'POST',
                credentials: 'include',
                body: fd,
            })
            if (res) {
                toast.add({ title: 'CERFA 16702 enregistré', color: 'success', icon: 'i-heroicons-check-circle' })
                emit('submit')
                loading.value = false
            }
        }
    } catch (e: any) {
        const msg = e?.data?.detail || e.message || 'Erreur inconnue'
        const toast = useToast()
        toast.add({ title: 'Échec de soumission', description: String(msg), color: 'error' })
    }
}

const declarantTypeItems = [
    { label: 'Individu', value: 'individual' },
    { label: 'Entreprise', value: 'company' }
]

const yesNoItems = [
    { label: 'Oui', value: 'yes' },
    { label: 'Non', value: 'no' }
]

// Mapping booléens <-> Oui/Non pour RadioGroup
const agrivoltaicYN = computed<string>({
    get: () => (state.value.agrivoltaic_project ? 'yes' : 'no'),
    set: (v: string) => { state.value.agrivoltaic_project = v === 'yes' }
})
</script>

<template>
    <UForm :state="state" :validate="validate" class="space-y-3" @submit.prevent="onSubmit">
        <div class="space-y-3">
            <!-- 1. Identité du déclarant -->
            <UCard>
                <template #header>
                    <div class="font-semibold">1. Identité du déclarant</div>
                </template>
                <div class="space-y-4">
                    <UFormField name="declarant_type" label="Type de déclarant" required>
                        <URadioGroup v-model="state.declarant_type" :items="declarantTypeItems"
                            orientation="horizontal" />
                    </UFormField>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <UFormField name="last_name" label="Nom" required>
                            <UInput v-model="state.last_name" class="w-full" />
                        </UFormField>
                        <UFormField name="first_name" label="Prénom" required>
                            <UInput v-model="state.first_name" class="w-full" />
                        </UFormField>
                    </div>

                    <div v-if="state.declarant_type === 'individual'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <UFormField name="birth_date" label="Date de naissance" required>
                            <UInput v-model="state.birth_date" type="date" class="w-full" />
                        </UFormField>
                        <UFormField name="birth_place" label="Lieu de naissance" required>
                            <UInput v-model="state.birth_place" class="w-full" />
                        </UFormField>
                        <UFormField name="birth_department" label="Département de naissance" required>
                            <UInput v-model="state.birth_department" class="w-full" />
                        </UFormField>
                        <UFormField name="birth_country" label="Pays de naissance" required>
                            <UInput v-model="state.birth_country" class="w-full" />
                        </UFormField>
                    </div>
                </div>
            </UCard>

            <!-- 2. Coordonnées du déclarant -->
            <UCard>
                <template #header>
                    <div class="font-semibold">2. Coordonnées du déclarant</div>
                </template>
                <div class="space-y-4">
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <UFormField name="address_street" label="Rue" required>
                            <UInput v-model="state.address_street" class="w-full" />
                        </UFormField>
                        <UFormField name="address_number" label="Numéro">
                            <UInput v-model="state.address_number" class="w-full" />
                        </UFormField>
                        <UFormField name="address_lieu_dit" label="Lieu-dit">
                            <UInput v-model="state.address_lieu_dit" class="w-full" />
                        </UFormField>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <UFormField name="address_locality" label="Localité" required>
                            <UInput v-model="state.address_locality" class="w-full" />
                        </UFormField>
                        <UFormField name="address_postal_code" label="Code postal" required>
                            <UInput v-model="state.address_postal_code" class="w-full" />
                        </UFormField>
                        <UFormField name="address_bp" label="BP">
                            <UInput v-model="state.address_bp" class="w-full" />
                        </UFormField>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <UFormField name="address_cedex" label="CEDEX">
                            <UInput v-model="state.address_cedex" class="w-full" />
                        </UFormField>
                        <UFormField name="phone_country_code" label="Code pays téléphone">
                            <UInput v-model="state.phone_country_code" class="w-full" placeholder="+33" />
                        </UFormField>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <UFormField name="phone" label="Téléphone" required>
                            <UInput v-model="state.phone" class="w-full" />
                        </UFormField>
                        <UFormField name="email" label="Adresse électronique">
                            <UInput v-model="state.email" type="email" class="w-full" />
                        </UFormField>
                    </div>

                    <UFormField name="email_consent" label="Consentement à la communication par courrier électronique">
                        <UCheckbox v-model="state.email_consent" />
                    </UFormField>
                </div>
            </UCard>

            <!-- 3. Le terrain -->
            <UCard>
                <template #header>
                    <div class="font-semibold">3. Le terrain</div>
                </template>
                <div class="space-y-4">
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <UFormField name="land_street" label="Rue" required>
                            <UInput v-model="state.land_street" class="w-full" />
                        </UFormField>
                        <UFormField name="land_number" label="Numéro">
                            <UInput v-model="state.land_number" class="w-full" />
                        </UFormField>
                        <UFormField name="land_lieu_dit" label="Lieu-dit">
                            <UInput v-model="state.land_lieu_dit" class="w-full" />
                        </UFormField>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <UFormField name="land_locality" label="Localité" required>
                            <UInput v-model="state.land_locality" class="w-full" />
                        </UFormField>
                        <UFormField name="land_postal_code" label="Code postal" required>
                            <UInput v-model="state.land_postal_code" class="w-full" />
                        </UFormField>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <UFormField name="cadastral_prefix" label="Préfixe cadastral">
                            <UInput v-model="state.cadastral_prefix" class="w-full" />
                        </UFormField>
                        <UFormField name="cadastral_section" label="Section cadastrale">
                            <UInput v-model="state.cadastral_section" class="w-full" />
                        </UFormField>
                        <UFormField name="cadastral_number" label="Numéro cadastral">
                            <UInput v-model="state.cadastral_number" class="w-full" />
                        </UFormField>
                        <UFormField name="cadastral_surface_m2" label="Surface (m²)">
                            <UInput v-model.number="state.cadastral_surface_m2" type="number" min="0" step="0.01"
                                class="w-full" />
                        </UFormField>
                    </div>
                </div>
            </UCard>

            <!-- 4.1 Le projet -->
            <UCard>
                <template #header>
                    <div class="font-semibold">4.1 Le projet</div>
                </template>
                <div class="space-y-4">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <UFormField name="project_new_construction" label="Nouvelle construction">
                            <UCheckbox v-model="state.project_new_construction" />
                        </UFormField>
                        <UFormField name="project_existing_works" label="Travaux sur une construction existante">
                            <UCheckbox v-model="state.project_existing_works" />
                        </UFormField>
                    </div>

                    <UFormField name="project_description" label="Description du projet" required>
                        <UTextarea v-model="state.project_description" :rows="4" class="w-full" />
                    </UFormField>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <UFormField name="destination_primary_residence" label="Résidence principale">
                            <UCheckbox v-model="state.destination_primary_residence" />
                        </UFormField>
                        <UFormField name="destination_secondary_residence" label="Résidence secondaire">
                            <UCheckbox v-model="state.destination_secondary_residence" />
                        </UFormField>
                    </div>

                    <UFormField name="agrivoltaic_project" label="Projet agrivoltaïque">
                        <URadioGroup v-model="agrivoltaicYN" :items="yesNoItems" orientation="horizontal" />
                    </UFormField>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <UFormField name="electrical_power_text"
                            label="Puissance électrique (si > 12kVA mono ou 36kVA tri)">
                            <UInput v-model="state.electrical_power_text" class="w-full" />
                        </UFormField>
                        <UFormField name="peak_power_text" label="Puissance crête (si sol ou ombrières)">
                            <UInput v-model="state.peak_power_text" class="w-full" />
                        </UFormField>
                    </div>

                    <UFormField name="energy_destination" label="Destination principale de l'énergie produite">
                        <UTextarea v-model="state.energy_destination" :rows="3" class="w-full" />
                    </UFormField>
                </div>
            </UCard>

            <!-- 5. Périmètres de protection -->
            <UCard>
                <template #header>
                    <div class="font-semibold">5. Périmètres de protection</div>
                </template>
                <div class="space-y-3">
                    <UFormField name="protection_site_patrimonial" label="Site patrimonial">
                        <UCheckbox v-model="state.protection_site_patrimonial" />
                    </UFormField>
                    <UFormField name="protection_site_classe_or_instance" label="Site classé/instance de classement">
                        <UCheckbox v-model="state.protection_site_classe_or_instance" />
                    </UFormField>
                    <UFormField name="protection_monument_abords" label="Abords d'un monument historique">
                        <UCheckbox v-model="state.protection_monument_abords" />
                    </UFormField>
                </div>
            </UCard>

            <!-- 8. Engagement du déclarant -->
            <UCard>
                <template #header>
                    <div class="font-semibold">8. Engagement du déclarant</div>
                </template>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <UFormField name="engagement_city" label="Ville" required>
                        <UInput v-model="state.engagement_city" class="w-full" />
                    </UFormField>
                    <UFormField name="engagement_date" label="Date" required>
                        <UInput v-model="state.engagement_date" type="date" class="w-full" />
                    </UFormField>
                </div>
            </UCard>

            <!-- Pièces jointes DPC -->
            <UCard>
                <template #header>
                    <div class="font-semibold">Pièces jointes (DPC)</div>
                </template>
                <div class="space-y-4">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <UFormField name="dpc1" label="DPC1 - Plan de masse des constructions à édifier">
                            <UFileUpload v-model="state.dpc1" icon="i-lucide-file-text" label="Importer un document"
                                description="PDF, PNG, JPG ou JPEG" accept=".pdf,image/*" />
                        </UFormField>
                        <UFormField name="dpc2" label="DPC2 - Plan en coupe du terrain et des constructions">
                            <UFileUpload v-model="state.dpc2" icon="i-lucide-file-text" label="Importer un document"
                                description="PDF, PNG, JPG ou JPEG" accept=".pdf,image/*" />
                        </UFormField>
                        <UFormField name="dpc3" label="DPC3 - Notice descriptive">
                            <UFileUpload v-model="state.dpc3" icon="i-lucide-file-text" label="Importer un document"
                                description="PDF, PNG, JPG ou JPEG" accept=".pdf,image/*" />
                        </UFormField>
                        <UFormField name="dpc4" label="DPC4 - Plan des façades et des toitures">
                            <UFileUpload v-model="state.dpc4" icon="i-lucide-file-text" label="Importer un document"
                                description="PDF, PNG, JPG ou JPEG" accept=".pdf,image/*" />
                        </UFormField>
                        <UFormField name="dpc5" label="DPC5 - Document graphique du terrain">
                            <UFileUpload v-model="state.dpc5" icon="i-lucide-file-text" label="Importer un document"
                                description="PDF, PNG, JPG ou JPEG" accept=".pdf,image/*" />
                        </UFormField>
                        <UFormField name="dpc6" label="DPC6 - Photographie du terrain nu et de son environnement">
                            <UFileUpload v-model="state.dpc6" icon="i-lucide-file-text" label="Importer un document"
                                description="PDF, PNG, JPG ou JPEG" accept=".pdf,image/*" />
                        </UFormField>
                        <UFormField name="dpc7" label="DPC7 - Photographie du terrain nu et de son environnement">
                            <UFileUpload v-model="state.dpc7" icon="i-lucide-file-text" label="Importer un document"
                                description="PDF, PNG, JPG ou JPEG" accept=".pdf,image/*" />
                        </UFormField>
                        <UFormField name="dpc8" label="DPC8 - Photographie du terrain nu et de son environnement">
                            <UFileUpload v-model="state.dpc8" icon="i-lucide-file-text" label="Importer un document"
                                description="PDF, PNG, JPG ou JPEG" accept=".pdf,image/*" />
                        </UFormField>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <UFormField name="dpc11" label="DPC11 - Notice descriptive des matériaux">
                            <UFileUpload v-model="state.dpc11" icon="i-lucide-file-text" label="Importer un document"
                                description="PDF, PNG, JPG ou JPEG" accept=".pdf,image/*" />
                        </UFormField>
                        <UFormField name="dpc11_notice_materiaux" label="Notice descriptive des matériaux (texte)">
                            <UTextarea v-model="state.dpc11_notice_materiaux" :rows="3" class="w-full" />
                        </UFormField>
                    </div>
                </div>
            </UCard>
        </div>

        <!-- Signature -->
        <UCard>
            <template #header>
                <div class="font-semibold">Signature du déclarant : Datée et précédée de la mention "Lu et approuvé"
                </div>
            </template>
            <div class="space-y-6">
                <SignatureField v-model="state.declarant_signature" :required="true" label="Nom du signataire" />
            </div>
        </UCard>

        <div class="flex justify-end pt-2">
            <UButton :loading="loading" icon="i-heroicons-check-circle" type="submit"
                label="Enregistrer" />
        </div>
    </UForm>
</template>
