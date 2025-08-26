<script setup lang="ts">
import { useAuthStore } from '~/store/auth'
import SignatureField from '~/components/common/SignatureField.vue'

type YesNoUnknown = 'yes' | 'no' | 'unknown'

type TechnicalVisitDraft = {
    visit_date: string
    expected_installation_date: string
    roof_cover: '' | 'Tuile' | 'Tuile écaille' | 'Ardoise' | 'Bac acier' | 'Fibrociment' | 'Toit terrasse'
    spare_tiles: boolean
    roof_shape: '' | '1 pan' | 'Multipan' | 'Toit plat terrasse'
    roof_access: '' | 'R' | 'R1' | 'R2' | 'Autre'
    roof_access_other: string
    nacelle_needed: YesNoUnknown
    truck_access: YesNoUnknown
    truck_access_note: string
    meter_type: '' | 'Linky' | 'Autre'
    meter_type_other: string
    current_type: '' | 'Monophasé' | 'Triphasé'
    reuse_existing_connection: boolean
    meter_position: '' | 'Intérieur' | 'Extérieur' | 'Inconnu'
    panel_to_board_distance_m: number | null
    meter_location_photo: File | null
    extra_required: boolean
    extra_materials: string
    client_signature: { signer_name: string; method: 'draw' | 'upload'; dataUrl: string; file: File | null }
    installer_signature: { signer_name: string; method: 'draw' | 'upload'; dataUrl: string; file: File | null }
}

const props = defineProps<{ draft: TechnicalVisitDraft }>()

const state = toRef(props, 'draft')

const auth = useAuthStore()

// Validation globale
const validate = (s: TechnicalVisitDraft) => {
    const errors: { name: string; message: string }[] = []

    // Informations de base
    if (!s.visit_date) errors.push({ name: 'visit_date', message: 'Date de visite requise.' })
    if (!s.expected_installation_date) errors.push({ name: 'expected_installation_date', message: 'Date d\'installation prévisionnelle requise.' })

    // Toiture
    if (!s.roof_cover) errors.push({ name: 'roof_cover', message: 'Type de couverture requis.' })
    if (!s.roof_shape) errors.push({ name: 'roof_shape', message: 'Forme du toit requise.' })

    // Accessibilité
    if (!s.roof_access) errors.push({ name: 'roof_access', message: 'Accès toiture requis.' })
    if (s.roof_access === 'Autre' && !s.roof_access_other.trim()) {
        errors.push({ name: 'roof_access_other', message: 'Précisez l\'accès toiture.' })
    }
    if (s.truck_access === 'no' && !s.truck_access_note.trim()) {
        errors.push({ name: 'truck_access_note', message: 'Précisez l\'accès camion (>30m).' })
    }

    // Installation électrique
    if (!s.meter_type) errors.push({ name: 'meter_type', message: 'Type de compteur requis.' })
    if (s.meter_type === 'Autre' && !s.meter_type_other.trim()) {
        errors.push({ name: 'meter_type_other', message: 'Précisez le type de compteur.' })
    }
    if (!s.current_type) errors.push({ name: 'current_type', message: 'Type de courant requis.' })
    if (!s.meter_position) errors.push({ name: 'meter_position', message: 'Position du compteur requise.' })
    if (s.panel_to_board_distance_m === null || isNaN(s.panel_to_board_distance_m as any) || (s.panel_to_board_distance_m as number) < 0) {
        errors.push({ name: 'panel_to_board_distance_m', message: 'Distance invalide.' })
    }

    // Matériel supplémentaire
    if (s.extra_required && !s.extra_materials.trim()) {
        errors.push({ name: 'extra_materials', message: 'Listez le matériel et la raison.' })
    }

    // Signature (afficher selon rôle uniquement)
    if (auth.user?.is_staff) {
        // Installateur signe côté installateur
        if (!s.installer_signature.signer_name.trim()) errors.push({ name: 'installer_signature.signer_name', message: 'Nom du signataire requis.' })
    } else {
        if (!s.client_signature.signer_name.trim()) errors.push({ name: 'client_signature.signer_name', message: 'Nom du signataire requis.' })
    }

    return errors
}

function onSubmit() {
    // Pour l'instant, pas d\'appel API; simple toast
    const toast = useToast()
    toast.add({ title: 'Brouillon enregistré localement', description: 'La soumission complète sera branchée plus tard.', color: 'neutral' })
}

const roofCoverItems = [
    'Tuile', 'Tuile écaille', 'Ardoise', 'Bac acier', 'Fibrociment', 'Toit terrasse'
].map(v => ({ label: v, value: v }))
const roofShapeItems = [
    '1 pan', 'Multipan', 'Toit plat terrasse'
].map(v => ({ label: v, value: v }))
const roofAccessItems = ['R', 'R1', 'R2', 'Autre'].map(v => ({ label: v, value: v }))
const meterTypeItems = ['Linky', 'Autre'].map(v => ({ label: v, value: v }))
const currentTypeItems = ['Monophasé', 'Triphasé'].map(v => ({ label: v, value: v }))
const meterPositionItems = ['Intérieur', 'Extérieur', 'Inconnu'].map(v => ({ label: v, value: v }))

const yesNoUnknownItems = [
    { label: 'Oui', value: 'yes' },
    { label: 'Non', value: 'no' },
    { label: 'Inconnu', value: 'unknown' },
]

// Mapping booléens <-> Oui/Non pour RadioGroup
const yesNoItems = [
    { label: 'Oui', value: 'yes' },
    { label: 'Non', value: 'no' }
]

const spareTilesYN = computed<string>({
    get: () => (state.value.spare_tiles ? 'yes' : 'no'),
    set: (v: string) => { state.value.spare_tiles = v === 'yes' }
})

const reuseExistingYN = computed<string>({
    get: () => (state.value.reuse_existing_connection ? 'yes' : 'no'),
    set: (v: string) => { state.value.reuse_existing_connection = v === 'yes' }
})
</script>

<template>
    <UForm :state="state" :validate="validate" class="space-y-3" @submit.prevent="onSubmit">
        <!-- Informations de base -->
        <UCard>
            <template #header>
                <div class="font-semibold">Informations de base</div>
            </template>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <UFormField name="visit_date" label="Date de la visite technique" required>
                    <UInput v-model="state.visit_date" type="date" class="w-full" />
                </UFormField>
                <UFormField name="expected_installation_date" label="Date d'installation prévisionnelle" required>
                    <UInput v-model="state.expected_installation_date" type="date" class="w-full" />
                </UFormField>
            </div>
        </UCard>

        <!-- Informations sur la toiture -->
        <UCard>
            <template #header>
                <div class="font-semibold">Informations sur la toiture</div>
            </template>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <UFormField name="roof_cover" label="Type de couverture" required>
                    <USelect v-model="state.roof_cover" :items="roofCoverItems" class="w-full"
                        placeholder="Sélectionner" />
                </UFormField>
                <UFormField name="spare_tiles" label="Tuiles de rechange">
                    <URadioGroup v-model="spareTilesYN" :items="yesNoItems" orientation="horizontal" />
                </UFormField>
                <UFormField name="roof_shape" label="Forme du toit" required>
                    <USelect v-model="state.roof_shape" :items="roofShapeItems" class="w-full"
                        placeholder="Sélectionner" />
                </UFormField>
            </div>
        </UCard>

        <!-- Accessibilité -->
        <UCard>
            <template #header>
                <div class="font-semibold">Accessibilité</div>
            </template>
            <div class="space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <UFormField name="roof_access" label="Accès toiture" required>
                        <USelect v-model="state.roof_access" :items="roofAccessItems" class="w-full"
                            placeholder="Sélectionner" />
                    </UFormField>
                    <UFormField name="nacelle_needed" label="Nacelle nécessaire">
                        <URadioGroup v-model="state.nacelle_needed" :items="yesNoUnknownItems"
                            class="flex flex-wrap gap-3" />
                    </UFormField>
                    <UFormField name="truck_access" label="Accès camion">
                        <URadioGroup v-model="state.truck_access" :items="yesNoUnknownItems"
                            class="flex flex-wrap gap-3" />
                    </UFormField>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <UFormField v-if="state.roof_access === 'Autre'" name="roof_access_other"
                        label="Précisions (Accès toiture)">
                        <UInput v-model="state.roof_access_other" class="w-full"
                            placeholder="Décrivez l'accès toiture" />
                    </UFormField>
                    <UFormField class="md:col-start-3" v-if="state.truck_access === 'no'" name="truck_access_note"
                        label="Précisions (Accès camion)">
                        <UInput v-model="state.truck_access_note" class="w-full" placeholder="Précisez la contrainte" />
                    </UFormField>
                </div>
            </div>
        </UCard>

        <!-- Installation électrique existante -->
        <UCard>
            <template #header>
                <div class="font-semibold">Installation électrique existante</div>
            </template>
            <div class="space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <UFormField name="meter_type" label="Type de compteur" required>
                        <USelect v-model="state.meter_type" :items="meterTypeItems" class="w-full"
                            placeholder="Sélectionner" />
                    </UFormField>
                    <UFormField name="current_type" label="Type de courant" required>
                        <USelect v-model="state.current_type" :items="currentTypeItems" class="w-full"
                            placeholder="Sélectionner" />
                    </UFormField>
                    <UFormField name="reuse_existing_connection" label="Raccordement au réseau existant">
                        <URadioGroup v-model="reuseExistingYN" :items="yesNoItems" orientation="horizontal" />
                    </UFormField>
                </div>

                <div :class="['grid grid-cols-1 md:grid-cols-8 gap-4', { 'md:grid-cols-12': state.meter_type === 'Autre' }]">
                    <UFormField v-if="state.meter_type === 'Autre'" class="md:col-span-4" name="meter_type_other" label="Précisions (Type de compteur)">
                        <UInput v-model.number="state.meter_type_other" class="w-full" />
                    </UFormField>
                    <UFormField class="md:col-span-3" name="meter_position" label="Position du compteur" required>
                        <USelect v-model="state.meter_position" :items="meterPositionItems" class="w-full"
                            placeholder="Sélectionner" />
                    </UFormField>
                    <UFormField class="md:col-span-5" name="panel_to_board_distance_m"
                        label="Distance panneaux → tableau (m)" required>
                        <UInput class="w-full" v-model.number="state.panel_to_board_distance_m" type="number" min="0"
                            step="0.1" />
                    </UFormField>
                </div>

                <UFormField name="meter_location_photo" label="Photo localisation du compteur">
                    <UFileUpload v-model="state.meter_location_photo" icon="i-lucide-image"
                        label="Importez la photo depuis la galerie" description="SVG, PNG, JPG ou JPEG" accept="image/*"
                        class="h-[180px]" />
                </UFormField>
            </div>
        </UCard>

        <!-- Matériel supplémentaire nécessaire -->
        <UCard>
            <template #header>
                <div class="flex gap-4">
                    <div class="font-semibold">Matériel supplémentaire nécessaire</div>
                    <USwitch v-model="state.extra_required" />
                </div>
            </template>
            <div>
                <UFormField v-if="state.extra_required" name="extra_materials"
                    label="Liste du matériel supplémentaire à prévoir"
                    description="Aller à la ligne pour chaque élément à ajouter et indiquer pour chaque élément la raison de l'ajout">
                    <UTextarea v-model="state.extra_materials" :rows="5" class="w-full" />
                </UFormField>
            </div>
        </UCard>

        <!-- Signatures -->
        <UCard>
            <template #header>
                <div class="font-semibold">Signature</div>
            </template>
            <div class="space-y-6">
                <div v-if="auth.user?.is_staff">
                    <div class="mb-2 font-medium">Signature installateur</div>
                    <SignatureField v-model="state.installer_signature" :required="true" label="Nom du signataire" />
                </div>
                <div v-else>
                    <div class="mb-2 font-medium">Signature client</div>
                    <SignatureField v-model="state.client_signature" :required="true" label="Nom du signataire" />
                </div>
            </div>
        </UCard>

        <div class="flex justify-end pt-2">
            <UButton color="primary" icon="i-heroicons-check-circle" type="submit" label="Enregistrer" />
        </div>
    </UForm>
</template>
