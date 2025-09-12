<script setup lang="ts">
const model = defineModel<any>({ default: {} })
</script>

<template>
	<div class="space-y-3">
		<div class="grid grid-cols-2 gap-3">
			<UFormGroup label="Nom du client">
				<UInput v-model="model.nom_du_client" placeholder="Jean Dupont" />
			</UFormGroup>
			<UFormGroup label="Téléphone du client">
				<UInput v-model="model.telephone_du_client" placeholder="01 23 45 67 89" />
			</UFormGroup>
		</div>
		<UFormGroup label="Adresse du site">
			<UInput v-model="model.adresse_du_site" placeholder="12 Rue du Soleil, Paris" />
		</UFormGroup>
		<div class="grid grid-cols-3 gap-3">
			<UFormGroup label="Code postal">
				<UInput v-model="model.code_postal_du_client" placeholder="75001" />
			</UFormGroup>
			<UFormGroup label="Commune">
				<UInput v-model="model.commune_du_client" placeholder="Paris" />
			</UFormGroup>
			<UFormGroup label="Décalage Y (mm)">
				<UInput v-model.number="model.y_offset_mm" type="number" step="0.5" />
			</UFormGroup>
		</div>
		<div>
			<UCheckbox v-model="model.raccordement_au_reseau_public_de_distribution_par_l_installation_de_consommation" label="Raccordement via installation de consommation" />
		</div>
	</div>
</template>
