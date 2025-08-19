<script setup lang="ts">
import type { Product } from '~/types/billing';

const props = defineProps<{ modelValue: boolean, product?: Product | null }>()
const emit = defineEmits(['update:modelValue','submit'])

const loading = ref(false)
const typeItems = [
    {
        value: 'panel',
        label: 'Panneau'
    },
    {
        value: 'inverter',
        label: 'Onduleur'
    },
    {
        value: 'battery',
        label: 'Batterie'
    },
    {
        value: 'structure',
        label: 'Structure'
    },
    {
        value: 'service',
        label: 'Service'
    },
    {
        value: 'other',
        label: 'Autre'
    }
]

const state = reactive({
    name: '',
    type: '',
    description: '',
    unit_price: 0,
    cost_price: 0
})

const resetForm = () => {
    Object.assign(state, {
        name: '',
        type: '',
        description: '',
        unit_price: 0,
        cost_price: 0
    })
}

watch(() => props.product, (p) => {
    if (p) {
        Object.assign(state, p)
        state.unit_price = Number(p.unit_price)
        state.cost_price = Number(p.cost_price)
    } else {
        resetForm()
    }
}, { immediate: true })

const validate = (st: any) => {
    const errors: any[] = []
    if (!st.name) errors.push({ name: 'name', message: 'Nom obligatoire.' })
    if (!st.type) errors.push({ name: 'type', message: 'Type obligatoire.' })
    if (!st.unit_price) errors.push({ name: 'unit_price', message: 'Prix unitaire obligatoire.' })
    if (!st.description) errors.push({ name: 'description', message: 'Description obligatoire.' })
    return errors
}

const submit = async () => {
    loading.value = true
    const toast = useToast()
    const res = await apiRequest<Product>(
        () => $fetch(`/api/products/${props.product ? `${props.product.id}/` : ''}`,
            { method: props.product ? 'PATCH' : 'POST', body: state, credentials: 'include' }
        ),
        toast
    )
    if (res) {
        toast.add({ title: `Produit / Service ${props.product ? 'modifiée' : 'créée'} avec succès`, color: 'success', icon: 'i-heroicons-check-circle' })
        emit('submit', res)
    }
    loading.value = false
}
</script>

<template>
    <UModal :open="modelValue" :title="product ? 'Modifier Produit / Service' : 'Nouveau Produit / Service'" @update:open="v => emit('update:modelValue', v)"
        :ui="{ title: 'text-xl', content: 'max-w-2xl' }">
        <template #body>
            <UForm :state="state" :validate="validate" @submit="submit" class="w-full">
                <div class="grid grid-cols-2 gap-4 mb-6">
                    <UFormField label="Nom" name="name" required>
                        <UInput v-model="state.name" class="w-full" />
                    </UFormField>
                    <UFormField label="Type" name="type" required>
                        <USelectMenu v-model="state.type" :items="typeItems" value-key="value" class="w-full" />
                    </UFormField>
                    <UFormField label="Prix unitaire (€)" name="unit_price" required>
                        <UInputNumber v-model="state.unit_price" class="w-full" />
                    </UFormField>
                    <UFormField label="Coût (€)" name="cost_price">
                        <UInputNumber v-model="state.cost_price" class="w-full" />
                    </UFormField>
                    <UFormField label="Description" name="description" required class="col-span-2">
                        <UTextarea :rows="5" v-model="state.description" class="w-full" />
                    </UFormField>
                </div>
                <div class="flex justify-end">
                    <UButton type="submit" :loading="loading" icon="i-heroicons-check-circle"
                        :color="product ? 'secondary' : 'primary'" :label="product ? 'Modifier' : 'Créer'" />
                </div>
            </UForm>
        </template>
    </UModal>
</template>
