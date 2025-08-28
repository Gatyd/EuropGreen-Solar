<script setup lang="ts">
import Logo from '~/components/Logo.vue'
import type { InstallationForm } from '~/types/installations'

type SignatureInfo = { signer_name?: string; dataUrl?: string | null }

type MandateDraft = {
	client_civility: '' | 'Madame' | 'Monsieur'
	client_birth_date: string
	client_birth_place: string
	client_address: string
	company_name: string
	company_rcs_city: string
	company_siret: string
	company_head_office_address: string
	represented_by: string
	representative_role: string
	client_signature?: SignatureInfo
	installer_signature?: SignatureInfo
	// métadonnées pour l'aperçu
	generated_at?: string
	client_signature_image_url?: string | null
	client_signature_signed_at?: string | null
	installer_signature_image_url?: string | null
	installer_signature_signed_at?: string | null
}

const props = defineProps<{ draft: MandateDraft, form?: InstallationForm | null }>()

const civ = (v: MandateDraft['client_civility']) => v || '—'
const fullName = computed(() => {
	const f = props.form
	if (!f) return '—'
	return `${f.client_last_name ?? ''} ${f.client_first_name ?? ''}`.trim() || '—'
})
</script>


<template>
	<div class="mandate-print-root">
		<!-- En-tête -->
		<div class="flex justify-between items-center mb-6">
			<div>
				<Logo size="sm" />
			</div>
			<div class="text-right">
				<p class="text-2xl text-black font-semibold mb-1">MANDAT DE REPRÉSENTATION</p>
			</div>
		</div>

		<!-- Sous-titre -->
		<div class="mb-5">
			<div class="text-base font-medium text-gray-900">Pour la réalisation de démarches administratives</div>
		</div>

		<!-- Parties -->
		<div class="rounded-md border border-zinc-200">
			<table class="w-full text-[15px] border-collapse">
				<tbody>
					<tr class="odd:bg-zinc-50">
						<td class="w-[30%] p-2 text-gray-600 text-[17px] font-bold align-top">Entre le client</td>
						<td class="p-2">
							<div class="space-y-1">
								<div><span class="font-semibold">{{ civ(props.draft.client_civility) }} :</span> {{
									fullName }}</div>
								<div><span class="font-semibold">Date de naissance :</span> {{
									props.draft.client_birth_date || '—' }}</div>
								<div><span class="font-semibold">Lieu de naissance :</span> {{
									props.draft.client_birth_place || '—' }}</div>
								<div><span class="font-semibold">Adresse :</span> {{ props.draft.client_address || '—'
								}}</div>
								<div class="text-gray-500 italic">Ci-après désigné(e) le « Mandant »</div>
							</div>
						</td>
					</tr>
					<tr class="odd:bg-zinc-50">
						<td class="p-2 text-gray-600 text-[17px] font-bold align-top">Et l’installateur</td>
						<td class="p-2">
							<div class="space-y-1">
								<div><span class="font-semibold">Société :</span> {{ props.draft.company_name || '—' }}
								</div>
								<div><span class="font-semibold">Immatriculé au RCS de :</span> {{
									props.draft.company_rcs_city || '—' }}</div>
								<div><span class="font-semibold">Numéro SIRET :</span> {{ props.draft.company_siret ||
									'—' }}</div>
								<div><span class="font-semibold">Adresse du siège social :</span> {{
									props.draft.company_head_office_address || '—' }}</div>
								<div><span class="font-semibold">Représenté par :</span> {{ props.draft.represented_by
									|| '—' }}</div>
								<div><span class="font-semibold">En sa qualité de :</span> {{
									props.draft.representative_role || '—' }}</div>
								<div class="text-gray-500 italic">Ci-après désigné « le Mandataire »</div>
							</div>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- Préambule -->
		<div class="mt-6 space-y-3">
			<p class="text-gray-800">
				Les Parties sont ci-après individuellement ou collectivement dénommées la ou les « Partie(s) ».
			</p>
			<p>
				<span class="font-semibold">Étant préalablement exposé que</span> le Mandant souhaite donner pouvoir au
				Mandataire pour effectuer en son nom et pour son compte des démarches d’urbanisme et de raccordement
				d’une installation de production solaire photovoltaïque (le « Site ») au réseau public de distribution
				d’électricité, ce que le Mandataire accepte.
			</p>
			<p>
				Les Parties sont convenues, aux termes des présentes, de définir les conditions et modalités du mandat
				(le « Mandat »).
			</p>
		</div>

		<!-- Corps du mandat (page 1) -->
		<div class="mt-6 space-y-5">
			<div>
				<div class="font-semibold text-gray-900 mb-1">1. Objet</div>
				<p>
					Le Mandat a pour objet de définir les conditions dans lesquelles le Mandataire réalisera, au nom et
					pour le compte du Mandant, les démarches visées à l’article « Modalités de réalisation et
					description des Missions ».
				</p>
			</div>

			<div>
				<div class="font-semibold text-gray-900 mb-1">2. Modalités de réalisation et description des Missions
				</div>
				<div class="font-medium text-gray-900">2.1 Description des Missions</div>
				<p class="mt-1">
					Le Mandant donne mandat au Mandataire, ainsi qu’à son sous-traitant, de réaliser en son nom et pour
					son compte les démarches administratives nécessaires à la pose d’une installation photovoltaïque
					dont la maîtrise d’œuvre est assurée par le Mandataire (les « Missions »). À ce titre, le Mandataire
					pourra procéder à toute modification et intervention jugée nécessaire pour la bonne réalisation des
					Missions ou des projets du Mandant.
				</p>
				<p class="mt-3 font-medium text-gray-900">2.1.1 Déclaration préalable et attestation de conformité
					(CONSUEL)</p>
				<ul class="list-disc pl-6 space-y-1">
					<li>Réalisation de la déclaration préalable de travaux auprès des autorités compétentes (mairie).
					</li>
					<li>Envoi ou dépôt du dossier à la mairie.</li>
					<li>Récupération du récépissé de dépôt et de la décision finale.</li>
					<li>Remplissage en ligne du formulaire d’attestation de conformité auprès du CONSUEL.</li>
				</ul>

				<!-- Saut de page après 2.1.1 -->
				<div class="page-break-after"></div>

				<p class="mt-[20mm] font-medium text-gray-900">2.1.2 Démarches de raccordement (Enedis ou ELD)</p>
				<p>
					Par le présent Mandat, le Mandant donne pouvoir au Mandataire, ainsi qu’à tout sous-traitant mandaté
					par ce dernier, pour réaliser, en son nom et pour son compte, les démarches nécessaires auprès
					d’Enedis ou de tout autre gestionnaire de réseau public de distribution d’électricité, conformément
					à sa localisation géographique. Le Mandataire devient l’interlocuteur unique et destinataire de tous
					documents relatifs au raccordement.
				</p>
				<p class="mt-2">Le Mandataire s’engage notamment à :</p>
				<ul class="list-disc pl-6 space-y-1">
					<li>centraliser l’ensemble des pièces techniques et administratives nécessaires ;</li>
					<li>tenir informé le Mandant de toute demande de complément ou d’irrégularité ;</li>
					<li>transmettre sans délai tout document reçu au nom du Mandant pouvant entraîner une incidence pour
						ce dernier.</li>
				</ul>
				<p class="mt-2">Dans le cadre du présent Mandat, le Mandant autorise expressément le Mandataire à signer
					en son nom et pour son compte les documents contractuels nécessaires au raccordement du Site,
					notamment:</p>
				<ul class="list-disc pl-6 space-y-1">
					<li>Proposition de Raccordement Avant Complément,</li>
					<li>Proposition Technique et Financière,</li>
					<li>Convention de Raccordement du Site,</li>
					<li>Convention de Raccordement Directe,</li>
					<li>Contrat de Raccordement et ses annexes,</li>
					<li>Tout avenant relatif à l’échéance ou aux modalités du raccordement.</li>
				</ul>

				<p class="mt-3 font-medium text-gray-900">2.1.3 Facturation, exécution et contrats complémentaires</p>
				<p>Ces documents étant rédigés au nom du Mandant, le Mandataire prend toute disposition nécessaire pour
					assurer la pleine information du Mandant sur les clauses particulières afférentes au projet.</p>
				<p class="mt-2">À ce titre, le Mandataire est habilité à :</p>
				<ul class="list-disc pl-6 space-y-1">
					<li>régler en son nom et pour son compte les frais relatifs au raccordement du Site (factures,
						acomptes, relances), étant entendu que ces documents seront émis au nom du Mandant;</li>
					<li>exécuter le contrat de mandat L.342-6 et ses annexes au nom et pour le compte du Mandant, sous
						réserve de satisfaire aux critères énumérés à l’Annexe 1, le Mandant demeurant responsable de sa
						bonne exécution;</li>
					<li>signer en son nom et pour son compte le Contrat d’accès au réseau (CARD-I, CARD-S).</li>
				</ul>
			</div>
		</div>

		<!-- Signatures -->
		<div class="mt-8">
			<div class="mb-3 text-sm font-semibold text-zinc-700">Signatures</div>
			<div class="signatures-grid grid grid-cols-1 md:grid-cols-2 gap-6">
				<!-- Mandant -->
				<div class="signature-block">
					<div class="text-xs text-gray-600 mb-1">Signature du mandant (client)</div>
					<div
						class="signature-box border rounded-md p-3 inline-flex w-full min-h-[120px] items-center justify-center bg-white">
						<template
							v-if="props.draft.client_signature_image_url || props.draft.client_signature?.dataUrl">
							<img :src="(props.draft.client_signature_image_url || props.draft.client_signature?.dataUrl) || ''"
								alt="Signature client" class="h-20 object-contain" />
						</template>
						<template v-else>
							<div class="text-gray-500 italic">Pas encore signée</div>
						</template>
					</div>
					<div class="mt-2 text-[11px] text-gray-700">
						Signé par <span class="font-semibold">{{ props.draft.client_signature?.signer_name || '—'
						}}</span>
						<span v-if="props.draft.client_signature_signed_at"> • le {{ new
							Date(props.draft.client_signature_signed_at).toLocaleString('fr-FR') }}</span>
					</div>
				</div>

				<!-- Mandataire -->
				<div class="signature-block">
					<div class="text-xs text-gray-600 mb-1">Signature du mandataire (installateur)</div>
					<div
						class="signature-box border rounded-md p-3 inline-flex w-full min-h-[120px] items-center justify-center bg-white">
						<template
							v-if="props.draft.installer_signature_image_url || props.draft.installer_signature?.dataUrl">
							<img :src="(props.draft.installer_signature_image_url || props.draft.installer_signature?.dataUrl) || ''"
								alt="Signature installateur" class="h-20 object-contain" />
						</template>
						<template v-else>
							<div class="text-gray-500 italic">Pas encore signée</div>
						</template>
					</div>
					<div class="mt-2 text-[11px] text-gray-700">
						Signé par <span class="font-semibold">{{ props.draft.installer_signature?.signer_name || '—'
						}}</span>
						<span v-if="props.draft.installer_signature_signed_at"> • le {{ new
							Date(props.draft.installer_signature_signed_at).toLocaleString('fr-FR') }}</span>
					</div>
				</div>
			</div>
		</div>

		<!-- Pied de page (numérotation) -->
		<footer class="pdf-footer" aria-hidden="true">
			<span class="footer-text"> </span>
		</footer>
	</div>
</template>

<style scoped>
.mandate-print-root {
	width: 100%;
	min-height: 297mm;
	background: white;
	color: #222;
	font-size: 15px;
	padding: 24px 32px 64px 32px;
	box-sizing: border-box;
	position: relative;
}

.page-break {
	page-break-before: always;
	break-before: page;
}

.page-break-after {
	page-break-after: always;
	break-after: page;
}

.pdf-footer {
	position: fixed;
	left: 0;
	right: 0;
	bottom: 0;
	height: 32px;
	text-align: center;
	font-size: 13px;
	color: #888;
	width: 100vw;
	background: white;
	z-index: 100;
}

.footer-text {
	display: inline-block;
	margin-top: 6px;
}

@media print {
	.mandate-print-root {
		font-size: 14px;
		padding: 24px 40px 64px 40px;
	}

	/* Forcer l'alignement des signatures sur une seule ligne à l'impression */
	.signatures-grid {
		grid-template-columns: 1fr 1fr !important;
		gap: 16px !important;
		align-items: start;
	}

	.signature-block {
		break-inside: avoid !important;
		page-break-inside: avoid !important;
	}

	.signature-box img {
		max-width: 100%;
		height: auto;
	}

	.pdf-footer {
		display: none;
		/* Le pied de page PDF est géré par Playwright */
	}

	.page-break {
		page-break-before: always;
		break-before: page;
	}

	.page-break-after {
		page-break-after: always;
		break-after: page;
	}
}
</style>
