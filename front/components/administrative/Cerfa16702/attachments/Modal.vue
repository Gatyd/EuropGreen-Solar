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
const draft = reactive<any>({
    dpc1: [], dpc1_url: null as string | null,
    dpc2: [], dpc2_url: null as string | null,
    dpc3: [], dpc3_url: null as string | null,
    dpc4: [], dpc4_url: null as string | null,
    dpc5: [], dpc5_url: null as string | null,
    dpc6: [], dpc6_url: null as string | null,
    dpc7: [], dpc7_url: null as string | null,
    dpc8: [], dpc8_url: null as string | null,
    dpc11: [], dpc11_url: null as string | null,
    dpc11_notice_materiaux: '',
})

// Hydrate le brouillon depuis le CERFA 16702 existant + la fiche
watch(
    () => props.cerfa16702,
    (cf: any) => {
        if (!cf) return
                // Reset arrays
                draft.dpc1 = []; draft.dpc2 = []; draft.dpc3 = []; draft.dpc4 = []
                draft.dpc5 = []; draft.dpc6 = []; draft.dpc7 = []; draft.dpc8 = []
                draft.dpc11 = []
                draft.dpc1_url = cf.dpc1 || null
                draft.dpc2_url = cf.dpc2 || null
                draft.dpc3_url = cf.dpc3 || null
                draft.dpc4_url = cf.dpc4 || null
                draft.dpc5_url = cf.dpc5 || null
                draft.dpc6_url = cf.dpc6 || null
                draft.dpc7_url = cf.dpc7 || null
                draft.dpc8_url = cf.dpc8 || null
                draft.dpc11_url = cf.dpc11 || null
        draft.dpc11_notice_materiaux = cf.dpc11_notice_materiaux || ''

                // Hydrate via attachments_grouped si disponible (privilégie multi-urls)
                const grouped = cf.attachments_grouped || {}
                for (const key of Object.keys(grouped)) {
                    const list = grouped[key] as any[]
                    if (list && list.length) {
                        // On pousse seulement les URLs dans un champ virtuel *_urls pour affichage éventuel (Preview s'en sert via attachments_grouped directement)
                        // ici on n'ajoute pas de File car pas de re-download
                        // single legacy url déjà set ci-dessus pour fallback
                    }
                }
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
                        :cerfa16702="props.cerfa16702" :cerfa-id="props.cerfa16702?.id" @submit="onSubmit" />
                </div>
                <div class="xl:basis-1/2 min-h-0 overflow-auto">
                    <AdministrativeCerfa16702AttachmentsPreview class="shadow-md rounded-lg" mode="edit"
                        :cerfa16702="props.cerfa16702" :draft="draft" :form="form" />
                </div>
            </div>
        </template>
    </UModal>
</template>
