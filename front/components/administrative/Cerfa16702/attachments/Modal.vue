<script setup lang="ts">
import type { DeclarantType, InstallationForm } from '~/types/installations'

const model = defineModel({ type: Boolean })

const props = defineProps<{
    form?: InstallationForm | null
    cerfa16702?: InstallationForm['cerfa16702'] | null
    formId?: string
}>()

const emit = defineEmits<{ (e: 'submit'): void }>()

// État partagé du brouillon du mandat
const draft = reactive({

    // Pièces jointes
    dpc1: null,
    dpc1_url: null as string | null,
    dpc2: null,
    dpc2_url: null as string | null,
    dpc3: null,
    dpc3_url: null as string | null,
    dpc4: null,
    dpc4_url: null as string | null,
    dpc5: null,
    dpc5_url: null as string | null,
    dpc6: null,
    dpc6_url: null as string | null,
    dpc7: null,
    dpc7_url: null as string | null,
    dpc8: null,
    dpc8_url: null as string | null,
    dpc11: null,
    dpc11_url: null as string | null,
    dpc11_notice_materiaux: '',
})

// Hydrate le brouillon depuis le CERFA 16702 existant + la fiche
watch(
    () => props.cerfa16702,
    (cf: any) => {
        if (!cf) return
        draft.dpc1 = null
        draft.dpc1_url = cf.dpc1 || null
        draft.dpc2 = null
        draft.dpc2_url = cf.dpc2 || null
        draft.dpc3 = null
        draft.dpc3_url = cf.dpc3 || null
        draft.dpc4 = null
        draft.dpc4_url = cf.dpc4 || null
        draft.dpc5 = null
        draft.dpc5_url = cf.dpc5 || null
        draft.dpc6 = null
        draft.dpc6_url = cf.dpc6 || null
        draft.dpc7 = null
        draft.dpc7_url = cf.dpc7 || null
        draft.dpc8 = null
        draft.dpc8_url = cf.dpc8 || null
        draft.dpc11 = null
        draft.dpc11_url = cf.dpc11 || null
        draft.dpc11_notice_materiaux = cf.dpc11_notice_materiaux || ''
    },
    { immediate: true }
)

const onSubmit = () => {
    emit('submit')
    model.value = false
}
</script>

<template>
    <UModal v-model:open="model" title="Pièces jointes (DPC) CERFA 16702" fullscreen>
        <template #body>
            <div class="flex flex-col xl:flex-row gap-4 h-[85vh] min-h-0 overflow-hidden">
                <div class="xl:basis-1/2 min-h-0 overflow-auto">
                    <AdministrativeCerfa16702AttachmentsForm :draft="draft" :form="props.form"
                        :cerfa16702="props.cerfa16702" :form-id="props.formId" @submit="onSubmit" />
                </div>
                <div class="xl:basis-1/2 min-h-0 overflow-auto">
                    <AdministrativeCerfa16702AttachmentsPreview class="shadow-md rounded-lg" mode="edit"
                        :cerfa16702="props.cerfa16702" :draft="draft" :form="form" />
                </div>
            </div>
        </template>
    </UModal>
</template>
