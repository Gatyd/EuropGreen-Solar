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

const props = defineProps<{ draft: TechnicalVisitDraft, action?: 'full' | 'signature', formId?: string }>()

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

    // Signature
    if (props.action === 'signature') {
        // En mode signature: ne valide que le champ du signataire courant, et uniquement le nom
        if (auth.user?.is_staff) {
            if (!s.installer_signature.signer_name.trim()) errors.push({ name: 'installer_signature.signer_name', message: 'Nom du signataire requis.' })
        } else {
            if (!s.client_signature.signer_name.trim()) errors.push({ name: 'client_signature.signer_name', message: 'Nom du signataire requis.' })
        }
    } else {
        // En mode complet, signatures non obligatoires
    }

    return errors
}

async function onSubmit() {
    const toast = useToast()
    if (!props.formId) {
        toast.add({ title: 'Formulaire manquant', description: 'Impossible de soumettre sans ID de fiche.', color: 'error' })
        return
    }

    try {
        if (props.action === 'signature') {
            // Soumission d'une signature uniquement
            const role = auth.user?.is_staff ? 'installer' : 'client'
            const sig = role === 'installer' ? props.draft.installer_signature : props.draft.client_signature
            const formData = new FormData()
            formData.append('role', role)
            formData.append('signer_name', sig.signer_name)
            if (sig.file) formData.append('signature_file', sig.file)
            else if (sig.dataUrl) formData.append('signature_data', sig.dataUrl)

            const res = await $fetch(`/api/installations/forms/${props.formId}/technical-visit/sign/`, {
                method: 'POST',
                credentials: 'include',
                body: formData,
            })
            toast.add({ title: 'Signature enregistrée', color: 'success' })
            return
        }

        // Création/MàJ de la visite technique
        const s = props.draft
        const roofTypeMap: Record<string, string> = { 'Tuile': 'tile', 'Tuile écaille': 'scale_tile', 'Ardoise': 'slate', 'Bac acier': 'steel', 'Fibrociment': 'fibrocement', 'Toit terrasse': 'flat_terrace' }
        const roofShapeMap: Record<string, string> = { '1 pan': 'one_slope', 'Multipan': 'multi_slope', 'Toit plat terrasse': 'flat' }
        const roofAccessMap: Record<string, string> = { 'R': 'R', 'R1': 'R1', 'R2': 'R2', 'Autre': 'other' }
        const meterTypeMap: Record<string, string> = { 'Linky': 'linky', 'Autre': 'other' }
        const currentTypeMap: Record<string, string> = { 'Monophasé': 'mono', 'Triphasé': 'tri' }
        const meterPosMap: Record<string, string> = { 'Intérieur': 'indoor', 'Extérieur': 'outdoor', 'Inconnu': 'unknown' }

        const hasPhoto = !!s.meter_location_photo
        if (!hasPhoto && !s.installer_signature.file) {
            // JSON simple => vrais booléens
            const payload = {
                visit_date: s.visit_date,
                expected_installation_date: s.expected_installation_date,
                roof_type: s.roof_cover ? roofTypeMap[s.roof_cover] : undefined,
                tiles_spare_provided: !!s.spare_tiles,
                roof_shape: s.roof_shape ? roofShapeMap[s.roof_shape] : undefined,
                roof_access: s.roof_access ? roofAccessMap[s.roof_access] : undefined,
                roof_access_other: s.roof_access === 'Autre' ? (s.roof_access_other || undefined) : undefined,
                nacelle_needed: s.nacelle_needed || undefined,
                truck_access: s.truck_access || undefined,
                truck_access_comment: s.truck_access === 'no' ? (s.truck_access_note || undefined) : undefined,
                meter_type: s.meter_type ? meterTypeMap[s.meter_type] : undefined,
                meter_type_other: s.meter_type === 'Autre' ? (s.meter_type_other || undefined) : undefined,
                current_type: s.current_type ? currentTypeMap[s.current_type] : undefined,
                existing_grid_connection: !!s.reuse_existing_connection,
                meter_position: s.meter_position ? meterPosMap[s.meter_position] : undefined,
                panels_to_board_distance_m: s.panel_to_board_distance_m ?? undefined,
                additional_equipment_needed: !!s.extra_required,
                additional_equipment_details: s.extra_required ? (s.extra_materials || undefined) : undefined,
                // Signature installateur (dataURL uniquement ici)
                installer_signer_name: s.installer_signature.signer_name || undefined,
                installer_signature_data: s.installer_signature.dataUrl || undefined,
            }
            await $fetch(`/api/installations/forms/${props.formId}/technical-visit/`, {
                method: 'POST',
                credentials: 'include',
                body: payload,
            })
        } else {
            // FormData si fichier présent
            const fd = new FormData()
            fd.append('visit_date', s.visit_date)
            fd.append('expected_installation_date', s.expected_installation_date)
            if (s.roof_cover) fd.append('roof_type', roofTypeMap[s.roof_cover])
            fd.append('tiles_spare_provided', String(!!s.spare_tiles))
            if (s.roof_shape) fd.append('roof_shape', roofShapeMap[s.roof_shape])
            if (s.roof_access) fd.append('roof_access', roofAccessMap[s.roof_access])
            if (s.roof_access === 'Autre' && s.roof_access_other) fd.append('roof_access_other', s.roof_access_other)
            if (s.nacelle_needed) fd.append('nacelle_needed', s.nacelle_needed)
            if (s.truck_access) fd.append('truck_access', s.truck_access)
            if (s.truck_access === 'no' && s.truck_access_note) fd.append('truck_access_comment', s.truck_access_note)
            if (s.meter_type) fd.append('meter_type', meterTypeMap[s.meter_type])
            if (s.meter_type === 'Autre' && s.meter_type_other) fd.append('meter_type_other', s.meter_type_other)
            if (s.current_type) fd.append('current_type', currentTypeMap[s.current_type])
            fd.append('existing_grid_connection', String(!!s.reuse_existing_connection))
            if (s.meter_position) fd.append('meter_position', meterPosMap[s.meter_position])
            if (s.panel_to_board_distance_m !== null) fd.append('panels_to_board_distance_m', String(s.panel_to_board_distance_m))
            if (s.meter_location_photo) fd.append('meter_location_photo', s.meter_location_photo)
            fd.append('additional_equipment_needed', String(!!s.extra_required))
            if (s.extra_required && s.extra_materials) fd.append('additional_equipment_details', s.extra_materials)
            if (s.installer_signature.signer_name && (s.installer_signature.file || s.installer_signature.dataUrl)) {
                fd.append('installer_signer_name', s.installer_signature.signer_name)
                if (s.installer_signature.file) fd.append('installer_signature_file', s.installer_signature.file)
                else if (s.installer_signature.dataUrl) fd.append('installer_signature_data', s.installer_signature.dataUrl)
            }
            await $fetch(`/api/installations/forms/${props.formId}/technical-visit/`, {
                method: 'POST',
                credentials: 'include',
                body: fd,
            })
        }
        toast.add({ title: 'Visite technique enregistrée', color: 'success' })
    } catch (e: any) {
        const msg = e?.data?.detail || e.message || 'Erreur inconnue'
        const toast = useToast()
        toast.add({ title: 'Échec de soumission', description: String(msg), color: 'error' })
    }
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

                <div
                    :class="['grid grid-cols-1 md:grid-cols-8 gap-4', { 'md:grid-cols-12': state.meter_type === 'Autre' }]">
                    <UFormField v-if="state.meter_type === 'Autre'" class="md:col-span-4" name="meter_type_other"
                        label="Précisions (Type de compteur)">
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
                <div class="font-semibold">Signature {{ auth.user?.is_staff ? 'installateur' : 'client' }}</div>
            </template>
            <div class="space-y-6">
                <template v-if="props.action === 'signature'">
                    <div v-if="auth.user?.is_staff">
                        <SignatureField v-model="state.installer_signature" :required="true"
                            label="Nom du signataire" />
                    </div>
                    <div v-else>
                        <SignatureField v-model="state.client_signature" :required="true" label="Nom du signataire" />
                    </div>
                </template>
                <template v-else>
                    <!-- <div>
                        <div class="mb-2 font-medium">Signature client</div>
                        <SignatureField v-model="state.client_signature" :required="false" label="Nom du signataire" />
                    </div> -->
                    <div>
                        <SignatureField v-model="state.installer_signature" :required="false"
                            label="Nom du signataire" />
                    </div>
                </template>
            </div>
        </UCard>

        <div class="flex justify-end pt-2">
            <UButton v-if="props.action === 'signature'" color="primary" icon="i-heroicons-pencil-square" type="submit"
                label="Signer" />
            <UButton v-else color="primary" icon="i-heroicons-check-circle" type="submit" label="Enregistrer" />
        </div>
    </UForm>
</template>
