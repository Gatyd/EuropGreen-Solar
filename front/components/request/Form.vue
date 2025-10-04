<script setup lang="ts">
import { useAuthStore } from '~/store/auth';
import type { ProspectRequestPayload, ProspectStatus, ProspectSource, ProspectRequest } from '~/types/requests'

const props = defineProps<{ modelValue?: ProspectRequest | null }>()
const emit = defineEmits(['submit'])

const loading = ref(false)
const auth = useAuthStore()

// Déterminer le type de source selon le rôle de l'utilisateur
const userRoleSourceType = computed(() => {
    if (!auth.user) return null
    if (auth.user.role === 'collaborator') return 'collaborator'
    if (auth.user.role === 'customer') return 'client'
    if (auth.user.role === 'sales') return 'commercial'
    return null
})

// Afficher le select de source uniquement pour les admins
const showSourceTypeSelect = computed(() => auth.user?.is_superuser)

// Afficher le champ source uniquement pour les admins
const showSourceField = computed(() => auth.user?.is_superuser)

// Afficher le champ assigned_to uniquement pour les admins
const showAssignedToField = computed(() => auth.user?.is_superuser)

const sourceItems = [
    {
        value: 'web_form',
        label: 'Formulaire de demande'
    },
    {
        value: 'call_center',
        label: 'Centre d\'appel'
    },
    {
        value: 'client',
        label: 'Client'
    },
    {
        value: 'collaborator',
        label: 'Collaborateur'
    },
    {
        value: 'commercial',
        label: 'Commercial'
    }
]

// Initialiser source_type selon le rôle de l'utilisateur dès le départ
const initialSourceType = computed(() => {
    return userRoleSourceType.value || 'web_form'
})

// Initialiser source_id selon le rôle de l'utilisateur dès le départ
const initialSourceId = computed(() => {
    if (!auth.user) return undefined
    if (auth.user.role === 'collaborator' || auth.user.role === 'customer') {
        return auth.user.id
    }
    return undefined
})

// Initialiser assigned_to_id selon le rôle de l'utilisateur dès le départ
const initialAssignedToId = computed(() => {
    if (!auth.user) return undefined
    if (auth.user.role === 'sales') {
        return auth.user.id
    }
    return undefined
})

const state = reactive<ProspectRequestPayload>({
    last_name: '',
    first_name: '',
    email: '',
    phone: '',
    address: '',
    housing_type: '',
    electricity_bill: null,
    status: 'new' as ProspectStatus,
    source_type: initialSourceType.value as ProspectSource,
    source_id: initialSourceId.value,
    appointment_date: null,
    assigned_to_id: initialAssignedToId.value,
    // notes: ''
})

// Réinitialiser le formulaire quand le modal s'ouvre pour une nouvelle demande
watch([() => auth.user, () => props.modelValue], ([user, model]) => {
    
    // Si c'est une édition, le watcher modelValue s'en occupe
    if (model) {
        return
    }
    
    // Pour une nouvelle demande, réappliquer les valeurs par défaut selon le rôle
    if (!model && user && userRoleSourceType.value) {
        
        state.source_type = userRoleSourceType.value as ProspectSource
        
        // Auto-remplir source_id pour collaborator et customer (client)
        if (user.role === 'collaborator' || user.role === 'customer') {
            state.source_id = user.id
        } else {
            state.source_id = undefined
        }
        
        // Auto-remplir assigned_to_id pour sales
        if (user.role === 'sales') {
            state.assigned_to_id = user.id
        } else if (!user.is_superuser) {
            state.assigned_to_id = undefined
        }
        
    }
})

// Helper: formater une date ISO en valeur d'input datetime-local (YYYY-MM-DDTHH:MM) en heure locale
function isoToLocalInput(iso: string): string {
    const d = new Date(iso)
    const pad = (n: number) => String(n).padStart(2, '0')
    const yyyy = d.getFullYear()
    const mm = pad(d.getMonth() + 1)
    const dd = pad(d.getDate())
    const hh = pad(d.getHours())
    const mi = pad(d.getMinutes())
    return `${yyyy}-${mm}-${dd}T${hh}:${mi}`
}

watch(() => props.modelValue, (v) => {
    if (v) {
        // Assigner les propriétés connues, préparer appointment_date pour l'input
        Object.assign(state, {
            last_name: v.last_name,
            first_name: v.first_name,
            email: v.email,
            phone: v.phone,
            address: v.address,
            housing_type: v.housing_type || '',
            status: v.status,
            source_type: v.source_type,
            appointment_date: v.appointment_date ? isoToLocalInput(v.appointment_date) : null,
            electricity_bill: null
        })
        state.assigned_to_id = v.assigned_to?.id
        state.source_id = v.source?.id
    }
}, { immediate: true })

const validate = (st: any) => {
    const errors: any[] = []
    if (!st.last_name) errors.push({ name: 'last_name', message: 'Nom obligatoire.' })
    if (!st.first_name) errors.push({ name: 'first_name', message: 'Prénom obligatoire.' })
    if (!st.email) errors.push({ name: 'email', message: 'Email obligatoire.' })
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(st.email)) errors.push({ name: 'email', message: 'Email invalide.' })
    if (!st.phone) errors.push({ name: 'phone', message: 'Téléphone obligatoire.' })
    if (!st.address) errors.push({ name: 'address', message: 'Adresse obligatoire.' })
    if (!st.source_type) errors.push({ name: 'source_type', message: 'Source obligatoire.' })
    else if (st.source_type === 'call_center' && !st.appointment_date) errors.push({ name: 'appointment_date', message: 'Date de rendez-vous obligatoire.' })
    else if ((st.source_type === 'client' || st.source_type === 'collaborator') && !st.source_id && showSourceField.value) errors.push({ name: 'source_id', message: 'Source utilisateur obligatoire.' })
    else if (st.source_type === 'commercial' && !st.assigned_to_id && showAssignedToField.value) errors.push({ name: 'assigned_to_id', message: 'Chargé d\'affaire obligatoire.' })
    return errors
}

const submit = async () => {
    loading.value = true
    const form = new FormData()
    const toast = useToast()
    
    form.append('last_name', state.last_name)
    form.append('first_name', state.first_name)
    form.append('email', state.email)
    form.append('phone', state.phone)
    form.append('address', state.address)
    if (state.housing_type) form.append('housing_type', state.housing_type)
    if (state.electricity_bill) form.append('electricity_bill', state.electricity_bill)
    if (state.status) form.append('status', state.status)
    if (state.appointment_date) {
        // Convertir la valeur locale (YYYY-MM-DDTHH:MM) en ISO string pour l'API
        const iso = new Date(state.appointment_date).toISOString()
        form.append('appointment_date', iso)
    }
    form.append('source_type', state.source_type)
    if (state.source_id) form.append('source_id', state.source_id)
    if (state.assigned_to_id) form.append('assigned_to_id', state.assigned_to_id)
    
    // if (state.notes) form.append('notes', state.notes)
    const res = await apiRequest<ProspectRequest>(
        () => $fetch(`/api/requests/${props.modelValue ? `${props.modelValue.id}/` : ''}`,
            { method: props.modelValue ? 'PATCH' : 'POST', body: form, credentials: 'include' }
        ),
        toast
    )
    if (res) {
        toast.add({ title: `Demande ${props.modelValue ? 'modifiée' : 'créée'} avec succès`, color: 'success', icon: 'i-heroicons-check-circle' })
        emit('submit', form)
    }
    loading.value = false
}
</script>

<template>
    <UForm :state="state" :validate="validate" @submit="submit" class="w-full">
        <div class="grid grid-cols-2 gap-4 mb-6">
            <UFormField label="Nom" name="last_name" required>
                <UInput v-model="state.last_name" class="w-full" />
            </UFormField>
            <UFormField label="Prénom" name="first_name" required>
                <UInput v-model="state.first_name" class="w-full" />
            </UFormField>
            <UFormField label="Email" name="email" required>
                <UInput v-model="state.email" type="email" class="w-full" />
            </UFormField>
            <UFormField label="Téléphone" name="phone" required>
                <UInput v-model="state.phone" class="w-full" />
            </UFormField>
            <UFormField label="Adresse" name="address" required class="col-span-2">
                <UInput v-model="state.address" class="w-full" />
            </UFormField>
            <div class="space-y-4 col-span-2 md:col-span-1">
                <!-- Source type : uniquement pour admin -->
                <UFormField v-if="showSourceTypeSelect" label="Source de la demande" name="source_type" required>
                    <USelect v-model="state.source_type" :items="sourceItems" class="w-full" />
                </UFormField>

                <!-- Date RDV pour call_center -->
                <UFormField v-if="state.source_type === 'call_center'" label="Date de Rendez-vous"
                    name="appointment_date" required>
                    <UInput v-model="state.appointment_date" type="datetime-local" class="w-full" />
                </UFormField>

                <!-- Source utilisateur : uniquement pour admin quand source = client/collaborator -->
                <UFormField v-if="showSourceField && state.source_type === 'client'" label="Client source"
                    name="source_id" required>
                    <UserSelectMenu v-model="state.source_id" role-filter="customer" class="w-full" />
                </UFormField>
                <UFormField v-if="showSourceField && state.source_type === 'collaborator'" label="Collaborateur source"
                    name="source_id" required>
                    <UserSelectMenu v-model="state.source_id" role-filter="collaborator" class="w-full" />
                </UFormField>

                <!-- Employé chargé d'affaire : uniquement pour admin -->
                <UFormField v-if="showAssignedToField" label="Employé chargé d'affaire" name="assigned_to_id" :required="state.source_type === 'commercial'">
                    <UserSelectMenu v-model="state.assigned_to_id" role-filter="sales" class="w-full" />
                </UFormField>

                <!-- Type de logement si pas admin -->
                <UFormField v-if="!auth.user?.is_superuser" label="Type de logement (optionnel)" name="housing_type">
                    <UInput v-model="state.housing_type" class="w-full" />
                </UFormField>
            </div>
            <div class="space-y-3 col-span-2 md:col-span-1">
                <UFormField label="Facture d'électricité (optionnelle)" description="JPG, PNG ou PDF"
                    name="electricity_bill">
                    <!-- Affichage du fichier existant en mode édition -->
                    <div v-if="props.modelValue?.electricity_bill" class="mb-3">
                        <div class="text-sm text-gray-600 mb-2">Fichier actuel :</div>
                        <UButton as="a" :href="props.modelValue.electricity_bill" target="_blank"
                            icon="i-heroicons-document" variant="soft" color="primary" label="Voir la facture actuelle"
                            class="mb-2" />
                        <div class="text-xs text-gray-500 mb-3">Téléchargez un nouveau fichier pour remplacer l'actuel
                        </div>
                    </div>
                    <UFileUpload icon="i-heroicons-arrow-up-tray-16-solid" v-model="state.electricity_bill"
                        class="w-full" />
                </UFormField>
                <UFormField v-if="auth.user?.is_superuser" label="Type de logement (optionnel)" name="housing_type">
                    <UInput v-model="state.housing_type" class="w-full" />
                </UFormField>
            </div>
            <!-- <UFormField label="Notes" name="notes" class="col-span-2">
				<UTextarea v-model="state.notes" :rows="3" />
			</UFormField> -->
        </div>
        <div class="flex justify-center">
            <UButton type="submit" :loading="loading" icon="i-heroicons-check-circle" label="Valider" />
        </div>
    </UForm>
</template>
