<script setup lang="ts">
import Logo from '~/components/Logo.vue'
import type { Civility, ClientType, ConnectionNature, InstallationForm, MandateType } from '~/types/installations'

type SignatureInfo = { signer_name?: string; dataUrl?: string | null }

type MandateDraft = {
	// Mandant (client)
    client_type: ClientType
    client_civility: Civility | string
    client_address: string
    client_company_name: string
    client_company_siret: string
    client_company_represented_by: string
    // Entreprise en charge
    contractor_company_name: string
    contractor_company_siret: string
    contractor_represented_by_name: string
    contractor_represented_by_role: string
    //Mandat
    mandate_type: MandateType
    authorize_signature: boolean
    authorize_payment: boolean
    authorize_l342: boolean
    authorize_network_access: boolean
    // Localisation
    geographic_area: string
    connection_nature: ConnectionNature
	// métadonnées pour l'aperçu
	generated_at?: string
	client_signature_image_url?: string | null
	client_signature_signed_at?: string | null
	installer_signature_image_url?: string | null
	installer_signature_signed_at?: string | null
	// champs additionnels utilisés par le template
	client_birth_date?: string
	client_birth_place?: string
	company_name?: string
	company_rcs_city?: string
	company_siret?: string
	company_head_office_address?: string
	represented_by?: string
	representative_role?: string
	client_signature?: SignatureInfo
	installer_signature?: SignatureInfo
}

const props = defineProps<{ draft: MandateDraft, form?: InstallationForm | null, mode?: 'print' | 'edit' }>()

const currentMode = computed(() => props.mode || 'print')
const isPrint = computed(() => currentMode.value === 'print')
const isEdit = computed(() => currentMode.value === 'edit')

const civ = (v: MandateDraft['client_civility']) => v === 'mr' ? 'Monsieur' : v === 'mme' ? 'Madame' : '—'
const fullName = computed(() => {
	const f = props.form
	if (!f) return '—'
	return `${f.client_last_name ?? ''} ${f.client_first_name ?? ''}`.trim() || '—'
})
const natureRaccordement = (n: ConnectionNature) => {
    if(n === 'indiv_or_group_housing') return "Raccordement de logements individuels ou groupés"
    if(n === 'commercial_or_production') return "Locaux commerciaux/professionnels ou installation de production"
    if(n === 'branch_modification') return "Modification de branchement"
    if(n === 'power_change_or_ev') return "Modification de la puissance de raccordement / IRVE"
}

const yn = (v: boolean) => (v ? 'Oui' : 'Non')
</script>


<template>
    <div class="inline-block w-full xl:min-h-[1122.66px] xl:mx-auto bg-white text-xs px-6 py-4">
        <!-- En-tête -->
        <div class="flex justify-between items-center mb-6">
            <div>
                <Logo size="sm" />
            </div>
            <div class="text-right">
                <p class="text-2xl text-black font-normal mb-1">MANDAT ENEDIS</p>
                <!-- <p class="text-[11px] text-gray-500">Pour les démarches Enedis</p>
                <p class="text-[11px] text-gray-500">Généré le {{
                    props.draft.generated_at ? new Date(props.draft.generated_at).toLocaleDateString('fr-FR') : new Date().toLocaleDateString('fr-FR')
                }}</p> -->
            </div>
        </div>

        <!-- 1. Informations du mandant (client) -->
        <div class="mb-4">
            <div class="text-sm font-semibold text-zinc-700 mb-2">1.1. Informations du client</div>
            <div class="overflow-hidden rounded-md border border-zinc-200">
                <table class="w-full text-sm border-collapse">
                    <tbody>
                        <tr class="odd:bg-zinc-50">
                            <td class="w-[45%] p-2 text-gray-600">Type de client</td>
                            <td class="p-2">{{ props.draft.client_type === 'individual' ? 'Particulier' : 'Professionnel' }}</td>
                        </tr>
                        <tr v-if="props.draft.client_type === 'individual'" class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Civilité</td>
                            <td class="p-2">{{ civ(props.draft.client_civility) }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Nom / Prénom</td>
                            <td class="p-2">{{ fullName }}</td>
                        </tr>
                        <tr v-if="props.draft.client_birth_date" class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Date de naissance</td>
                            <td class="p-2">{{ props.draft.client_birth_date || '—' }}</td>
                        </tr>
                        <tr v-if="props.draft.client_birth_place" class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Lieu de naissance</td>
                            <td class="p-2">{{ props.draft.client_birth_place || '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Adresse</td>
                            <td class="p-2">{{ props.draft.client_address || '—' }}</td>
                        </tr>
                        <tr v-if="props.draft.client_type !== 'individual'" class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Nom de la société</td>
                            <td class="p-2">{{ props.draft.client_company_name || '—' }}</td>
                        </tr>
                        <tr v-if="props.draft.client_type !== 'individual'" class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">N° SIRET</td>
                            <td class="p-2">{{ props.draft.client_company_siret || '—' }}</td>
                        </tr>
                        <tr v-if="props.draft.client_type !== 'individual'" class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Représenté par</td>
                            <td class="p-2">{{ props.draft.client_company_represented_by || '—' }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 2. Informations du mandataire (entreprise en charge) -->
        <div class="mb-4">
            <div class="text-sm font-semibold text-zinc-700 mb-2">1.2. Informations de l'entreprise qui prend en charge</div>
            <div class="overflow-hidden rounded-md border border-zinc-200">
                <table class="w-full text-sm border-collapse">
                    <tbody>
                        <tr class="odd:bg-zinc-50">
                            <td class="w-[45%] p-2 text-gray-600">Nom de la société</td>
                            <td class="p-2">{{ props.draft.contractor_company_name || '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">N° SIRET</td>
                            <td class="p-2">{{ props.draft.contractor_company_siret || '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Représentée par</td>
                            <td class="p-2">{{ props.draft.contractor_represented_by_name || '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">En sa qualité de</td>
                            <td class="p-2">{{ props.draft.contractor_represented_by_role || '—' }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 3. Type de mandat et localisation -->
        <div class="mb-4">
            <div class="text-sm font-semibold text-zinc-700 mb-2">2. Le mandat</div>
            <div class="overflow-hidden rounded-md border border-zinc-200">
                <table class="w-full text-sm border-collapse">
                    <tbody>
                        <tr class="odd:bg-zinc-50">
                            <td class="w-[45%] p-2 text-gray-600">Type de mandat</td>
                            <td class="p-2">{{ props.draft.mandate_type || '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="w-[45%] p-2 text-gray-600">Signature du client</td>
                            <td class="p-2">{{ yn(props.draft.authorize_signature) }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Paiement du client</td>
                            <td class="p-2">{{ yn(props.draft.authorize_payment) }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">L342</td>
                            <td class="p-2">{{ yn(props.draft.authorize_l342) }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Accès réseau</td>
                            <td class="p-2">{{ yn(props.draft.authorize_network_access) }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 3. Localisation -->
        <div class="mb-4">
            <div class="text-sm font-semibold text-zinc-700 mb-2">3. Localisation</div>
            <div class="overflow-hidden rounded-md border border-zinc-200">
                <table class="w-full text-sm border-collapse">
                    <tbody>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Zone géographique</td>
                            <td class="p-2">{{ props.draft.geographic_area || '—' }}</td>
                        </tr>
                        <tr class="odd:bg-zinc-50">
                            <td class="p-2 text-gray-600">Nature de raccordement</td>
                            <td class="p-2">{{ natureRaccordement(props.draft.connection_nature) || '—' }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Signatures -->
        <div class="mt-8">
            <div class="mb-3 text-sm font-semibold text-zinc-700">Signatures</div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Mandant -->
                <div class="signature-block">
                    <div class="text-xs text-gray-600 mb-1">Signature du mandant (client)</div>
                    <div class="border rounded-md p-3 inline-flex w-full min-h-[120px] items-center justify-center bg-white">
                        <template v-if="props.draft.client_signature_image_url || props.draft.client_signature?.dataUrl">
                            <img :src="(props.draft.client_signature_image_url || props.draft.client_signature?.dataUrl) || ''" 
                                 alt="Signature client" class="h-20 object-contain" />
                        </template>
                        <template v-else>
                            <div class="text-gray-500 italic">Pas encore signée</div>
                        </template>
                    </div>
                    <div class="mt-2 text-[11px] text-gray-700">
                        Signé par <span class="font-semibold">{{ props.draft.client_signature?.signer_name || '—' }}</span>
                        <span v-if="props.draft.client_signature_signed_at"> • le {{ new Date(props.draft.client_signature_signed_at).toLocaleString('fr-FR') }}</span>
                    </div>
                </div>

                <!-- Mandataire -->
                <div class="signature-block">
                    <div class="text-xs text-gray-600 mb-1">Signature du mandataire (installateur)</div>
                    <div class="border rounded-md p-3 inline-flex w-full min-h-[120px] items-center justify-center bg-white">
                        <template v-if="props.draft.installer_signature_image_url || props.draft.installer_signature?.dataUrl">
                            <img :src="(props.draft.installer_signature_image_url || props.draft.installer_signature?.dataUrl) || ''" 
                                 alt="Signature installateur" class="h-20 object-contain" />
                        </template>
                        <template v-else>
                            <div class="text-gray-500 italic">Pas encore signée</div>
                        </template>
                    </div>
                    <div class="mt-2 text-[11px] text-gray-700">
                        Signé par <span class="font-semibold">{{ props.draft.installer_signature?.signer_name || '—' }}</span>
                        <span v-if="props.draft.installer_signature_signed_at"> • le {{ new Date(props.draft.installer_signature_signed_at).toLocaleString('fr-FR') }}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
@media print {
    .signature-block {
        break-inside: avoid;
        page-break-inside: avoid;
    }
}
</style>
