<script setup lang="ts">
import type { Role } from '~/types'

// Modèle exposé: l'objet rôle complet sélectionné (ou null)
const model = defineModel<Role | null>({
    default: null
})

const toast = useToast()
const loading = ref(false)
// Map interne id -> rôle
const rolesMap = reactive<Record<string, Role>>({})
// Liste d'items pour le select (value = id interne)
const items = ref<Array<{ label: string; value: string }>>([])
// id sélectionné dans le select
const selectedId = ref<string | null>(null)

// Rôles natifs (affichés même si aucun rôle en base)
// Note: ids préfixés pour éviter collision avec UUID/ids DB
// Les valeurs 'name' doivent correspondre exactement aux UserRoles du backend
const nativeRoles: Role[] = [
    {
        id: 'native:admin',
        name: 'admin',
        installation: true,
        offers: true,
        requests: true,
        administrative_procedures: true,
        created_at: '',
        updated_at: ''
    },
    {
        id: 'native:customer',
        name: 'customer',
        installation: false,
        offers: false,
        requests: false,
        administrative_procedures: false,
        created_at: '',
        updated_at: ''
    },
    {
        id: 'native:collaborator',
        name: 'collaborator',
        installation: true,
        offers: false,
        requests: false,
        administrative_procedures: false,
        created_at: '',
        updated_at: ''
    },
    {
        id: 'native:sales',
        name: 'sales',
        installation: true,
        offers: true,
        requests: true,
        administrative_procedures: false,
        created_at: '',
        updated_at: ''
    },
    {
        id: 'native:installer',
        name: 'installer',
        installation: true,
        offers: false,
        requests: false,
        administrative_procedures: false,
        created_at: '',
        updated_at: ''
    }
]

function buildItems(dynamicRoles: Role[]) {
    rolesMapClear()
    const list: Array<{ label: string; value: string }> = []
        ;[...nativeRoles, ...dynamicRoles].forEach(r => {
            rolesMap[r.id] = r
            list.push({ label: formatLabel(r), value: r.id })
        })
    items.value = list
    // Ré-appliquer sélection si model existe
    if (model.value) {
        if (!rolesMap[model.value.id]) {
            // Si rôle dynamique supprimé, on le perd → reset
            model.value = null
            selectedId.value = null
        } else {
            selectedId.value = model.value.id
        }
    }
}

function rolesMapClear() {
    Object.keys(rolesMap).forEach(k => delete rolesMap[k])
}

const nativeDisplayMap: Record<string, string> = {
    admin: 'Administrateur',
    customer: 'Client',
    collaborator: 'Collaborateur',
    sales: 'Commercial',
    installer: 'Installateur'
}
function formatLabel(r: Role) {
    // Ne montre plus le résumé des accès, uniquement le nom (localisé si natif)
    return nativeDisplayMap[r.name] || r.name
}

async function fetchDynamicRoles() {
    loading.value = true
    const result = await apiRequest<Role[]>(
        () => $fetch('/api/roles/', { credentials: 'include' }),
        toast
    )
    buildItems(result || [])
    loading.value = false
}

function onSelect(newId: string | null) {
    selectedId.value = newId
    model.value = newId ? rolesMap[newId] || null : null
}

watch(model, (val) => {
    if (!val) {
        selectedId.value = null
    } else if (val && selectedId.value !== val.id) {
        // synchronisation externe→interne
        if (!rolesMap[val.id]) {
            // Rôle injecté externe non présent → on reconstruit items
            buildItems([val])
        }
        selectedId.value = val.id
    }
})

onMounted(fetchDynamicRoles)
</script>

<template>
    <USelectMenu :model-value="selectedId || undefined" @update:model-value="onSelect" :items="items" value-key="value"
        label-key="label" :loading="loading" placeholder="Sélectionnez un rôle" class="w-full" />
</template>
