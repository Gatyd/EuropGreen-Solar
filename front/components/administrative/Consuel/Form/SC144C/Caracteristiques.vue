<script setup lang="ts">

defineProps<{ state: any }>()

</script>
<template>
    <div class="grid grid-cols-12 items-start gap-3 px-5 pb-4">
        <p class="col-span-12 font-semibold"><span class="text-sky-500">(1)</span> Module PV :</p>
        <UFormField label="Nombre de chaines" class="col-span-12 md:col-span-6 flex items-center gap-4">
            <UInput v-model="state.pv_module_string_count" type="number" class="w-full" />
        </UFormField>
        <UFormField label="U ocmax en V" class="col-span-12 md:col-span-6 flex items-center gap-4">
            <UInput v-model="state.pv_uocmax" type="number" class="w-full" />
        </UFormField>
        <UFormField label="I scmax-générateur (ou optimiseur) PV" class="col-span-12 flex items-center gap-4">
            <UInput v-model="state.pv_iscmax" type="number" class="w-full" />
        </UFormField>
        <p class="col-span-12 font-semibold"><span class="text-sky-500">(2)</span> Câble principal PV :</p>
        <UFormField label="Section (en mm²)" class="col-span-12 md:col-span-6 flex items-center gap-4">
            <UInput v-model="state.pv_main_cable_section" type="number" class="w-full" />
        </UFormField>
        <UFormField label="U" class="col-span-12 md:col-span-6 flex items-center gap-4">
            <UInput v-model="state.pv_main_cable_voltage" type="number" class="w-full">
                <template #trailing>
                    <UKbd variant="outline" value="V (en courant continu)" />
                </template>
            </UInput>
        </UFormField>
        <UFormField label="Température admissible sur l’âme (en °C)" class="col-span-12 flex items-center gap-4">
            <UInput v-model="state.pv_main_cable_temp_rating" type="number" class="w-full" />
        </UFormField>
        <p class="col-span-12 font-semibold"><span class="text-sky-500">(3a)</span> Interrupteur-Sectionneur général
            D.C.
            (partie générateur PV) :</p>
        <UFormField label="U n (en V)" class="col-span-12 md:col-span-6 flex items-center gap-4">
            <UInput v-model="state.dc_isolator_un" type="number" class="w-full" />
        </UFormField>
        <UFormField label="I n (en A)" class="col-span-12 md:col-span-6 flex items-center gap-4">
            <UInput v-model="state.dc_isolator_in" type="number" class="w-full" />
        </UFormField>
        <UCheckbox v-model="state.dc_isolator_not_applicable" class="col-span-12"
            label="Sans objet (ex : onduleur avec sectionneur intégré)" />
        <p class="col-span-12 font-semibold"><span class="text-sky-500">(3b)</span> Interrupteur-Sectionneur sur le
            câble
            batterie (partie distribution DC) :</p>
        <UFormField label="U n (en V)" class="col-span-12 md:col-span-5 flex items-center gap-4">
            <UInput v-model="state.dc_battery_isolator_un" type="number" class="w-full" />
        </UFormField>
        <UFormField label="I n (en A)" class="col-span-12 md:col-span-5 flex items-center gap-4">
            <UInput v-model="state.dc_battery_isolator_in" type="number" class="w-full" />
        </UFormField>
        <UCheckbox v-model="state.dc_battery_isolator_not_applicable" class="col-span-12 md:col-span-2"
            label="Sans objet" />
        <p class="col-span-12 md:col-span-6 font-medium">Intégré à l’enveloppe comprenant la batterie :</p>
        <UCheckbox v-model="state.dc_battery_isolator_integrated_yes" class="col-span-6 md:col-span-1" label="Non" />
        <UCheckbox v-model="state.dc_battery_isolator_integrated_no" class="col-span-6 md:col-span-1" label="Oui" />
        <p class="col-span-12 font-semibold"><span class="text-sky-500">(3c)</span> Interrupteur-Sectionneur pour
            d’autres
            sources d’alimentation DC :</p>
        <UCheckbox v-model="state.dc_other_isolator_no" class="col-span-6 md:col-span-1" label="Non" />
        <UCheckbox v-model="state.dc_other_isolator_yes" class="col-span-6 md:col-span-1" label="Oui" />
        <UFormField v-if="state.dc_other_isolator_yes" label="U n (en V)"
            class="col-span-6 md:col-span-5 flex items-center gap-4">
            <UInput v-model="state.dc_other_isolator_un" type="number" class="w-full" />
        </UFormField>
        <UFormField v-if="state.dc_other_isolator_yes" label="I n (en A)"
            class="col-span-6 md:col-span-5 flex items-center gap-4">
            <UInput v-model="state.dc_other_isolator_in" type="number" class="w-full" />
        </UFormField>
        <p class="col-span-12 font-semibold"><span class="text-sky-500">(3d)</span> Interrupteur-Sectionneur pour
            circuits
            d’utilisation en DC :</p>
        <UCheckbox v-model="state.dc_circuit_isolator_no" class="col-span-6 md:col-span-1" label="Non" />
        <UCheckbox v-model="state.dc_circuit_isolator_yes" class="col-span-6 md:col-span-1" label="Oui" />
        <UFormField v-if="state.dc_circuit_isolator_yes" label="U n (en V)"
            class="col-span-6 md:col-span-5 flex items-center gap-4">
            <UInput v-model="state.dc_circuit_isolator_un" type="number" class="w-full" />
        </UFormField>
        <UFormField v-if="state.dc_circuit_isolator_yes" label="I n (en A)"
            class="col-span-6 md:col-span-5 flex items-center gap-4">
            <UInput v-model="state.dc_circuit_isolator_in" type="number" class="w-full" />
        </UFormField>
        <p class="col-span-12 font-semibold"><span class="text-sky-500">(3e)</span> Interrupteur-Sectionneur pour
            d’autres sources d’alimentation AC :</p>
        <UCheckbox v-model="state.ac_isolator_no" class="col-span-6 md:col-span-1" label="Non" />
        <UCheckbox v-model="state.ac_isolator_yes" class="col-span-6 md:col-span-1" label="Oui" />
        <UFormField v-if="state.ac_isolator_yes" label="U n (en V)"
            class="col-span-6 md:col-span-5 flex items-center gap-4">
            <UInput v-model="state.ac_isolator_un" type="number" class="w-full" />
        </UFormField>
        <UFormField v-if="state.ac_isolator_yes" label="I n (en A)"
            class="col-span-6 md:col-span-5 flex items-center gap-4">
            <UInput v-model="state.ac_isolator_in" type="number" class="w-full" />
        </UFormField>
        <div class="col-span-12 grid grid-cols-2 md:grid-cols-3 items-center gap-4">
            <p class="col-span-2 md:col-span-1 font-semibold"><span class="text-sky-500">(4)</span> Polarité à la terre*
                :</p>
            <UCheckbox v-model="state.dc_polarity_to_earth_no" label="Non" class="w-full" />
            <UCheckbox v-model="state.dc_polarity_to_earth_yes" label="Oui" class="w-full" />
        </div>
        <p class="col-span-12 font-semibold"><span class="text-sky-500">(5a)</span> Onduleur PV :</p>
        <UFormField label="Nombre d’onduleurs identiques au(x) générateur(s) PV"
            class="col-span-12 flex items-center gap-4">
            <UInput v-model="state.inverter_identical_generator_count" type="number" class="w-full" />
        </UFormField>
        <UFormField label="Marque et modèle" class="col-span-12 flex items-center gap-4">
            <UInput v-model="state.inverter_brand_model" class="w-full" />
        </UFormField>
        <UFormField label="Sys. Découplage" required class="col-span-12 flex items-center gap-4">
            <div class="grid grid-cols-2 items-center gap-4">
                <UCheckbox v-model="state.inverter_ext_decoupling" label="externe" class="w-full" />
                <UCheckbox v-model="state.inverter_int_decoupling" label="intégré à l'onduleur" class="w-full" />
            </div>
        </UFormField>

        <!-- (5b) Inverter - Battery Charger -->
        <p class="col-span-12 font-semibold"><span class="text-sky-500">(5b)</span> Onduleur - chargeur de batterie* :
        </p>
        <UFormField label="Marque / Modèle" class="col-span-12 md:col-span-6 flex items-center gap-4">
            <UInput v-model="state.inverter_charger_brand_model" class="w-full" />
        </UFormField>
        <UFormField label="Référence onduleur-chargeur" class="col-span-12 md:col-span-6 flex items-center gap-4">
            <UInput v-model="state.inverter_charger_reference" class="w-full" />
        </UFormField>
        <UFormField label="Référence sous-ensemble (batterie/convertisseur)"
            class="col-span-12 flex items-center gap-4">
            <UInput v-model="state.battery_converter_subset_reference" class="w-full" />
        </UFormField>
        <div class="col-span-12 grid grid-cols-2 md:grid-cols-4 items-center gap-4">
            <p class="col-span-2 md:col-span-1 font-semibold">Sys. Découplage* :</p>
            <UCheckbox v-model="state.inverter_charger_decoupling_na" label="sans objet" />
            <UCheckbox v-model="state.inverter_charger_decoupling_external" label="externe" />
            <UCheckbox v-model="state.inverter_charger_decoupling_integrated" label="intégré" />
        </div>
        <p class="col-span-12 italic text-xs">Joindre le certificat de conformité à la pré-norme DIN VDE 0126-1-1 si
            applicable.
        </p>

        <!-- (5c) Installations raccordées -->
        <p class="col-span-12 font-semibold"><span class="text-sky-500">(5c)</span> Installations raccordées au réseau :
        </p>
        <UCheckbox v-model="state.decoupling_protection_verified_commitment" class="col-span-12"
            label="Le soussigné s’engage à s’être assuré du fonctionnement de la protection de découplage dans toutes les configurations du système." />

        <!-- (6a) Protection contre contacts indirects DC distribution -->
        <p class="col-span-12 font-semibold"><span class="text-sky-500">(6a)</span> Protection contre les contacts
            indirects (partie distribution DC) :</p>
        <UCheckbox v-model="state.dc_indirect_contact_by_slt" class="col-span-12"
            label="Par la mise en oeuvre d’un Schéma des Liaisons à la Terre (SLT) partie distribution DC" />
        <div class="col-span-12 grid grid-cols-6 md:grid-cols-8 gap-2 pl-2">
            <UCheckbox v-model="state.dc_indirect_contact_slt_tt" label="SLT TT" />
            <UCheckbox v-model="state.dc_indirect_contact_slt_it" label="SLT IT" />
            <UCheckbox v-model="state.dc_indirect_contact_slt_commitment_441" class="col-span-6"
                label="Engagement respect NF C 15-100 partie 4-41" />
            <UCheckbox v-model="state.dc_indirect_contact_tt_no_galvanic_separation_commitment" class="col-span-6"
                label="(TT) Pas de séparation galvanique AC / distribution DC" />
            <UCheckbox v-model="state.dc_indirect_contact_it_with_galvanic_separation_commitment" class="col-span-6"
                label="(IT) Séparation galvanique AC / distribution DC" />
        </div>
        <div class="col-span-12 grid grid-cols-2 md:grid-cols-3 gap-2">
            <UCheckbox v-model="state.dc_indirect_contact_cpi_integrated_yes" label="CPI intégré (NF EN 62109)" />
            <UCheckbox v-model="state.dc_indirect_contact_cpi_integrated_no" label="CPI séparé (NF EN 61557-8)" />
        </div>
        <UCheckbox v-model="state.dc_indirect_contact_tbts_tbtp" class="col-span-12"
            label="Par mise en oeuvre de la TBTS ou TBTP" />
        <UCheckbox v-model="state.dc_indirect_contact_tbts_tbtp_galvanic_separation_commitment" class="col-span-12 pl-4"
            label="Séparation galvanique AC / distribution DC (TBTS/TBTP)" />
        <UCheckbox v-model="state.dc_indirect_contact_electrical_separation" class="col-span-12"
            label="Par mise en oeuvre d’une disposition de séparation électrique" />
        <div class="col-span-12 space-y-1 pl-2">
            <UCheckbox v-model="state.dc_indirect_contact_electrical_separation_charge_regulator_branch"
                label="Régulateur batterie en dérivation champ PV" />
            <UCheckbox v-model="state.dc_indirect_contact_electrical_separation_galvanic_on_battery_input"
                label="Séparation galvanique entrée batterie onduleur" />
            <UCheckbox v-model="state.dc_indirect_contact_electrical_separation_galvanic_regulator_commitment"
                class="col-span-6" label="Séparation galvanique entre DC/batterie et DC générateur PV" />
            <UCheckbox v-model="state.dc_indirect_contact_electrical_separation_article_413_commitment"
                class="col-span-6" label="Respect article 413 NF C 15-100" />
        </div>
        <UCheckbox v-model="state.dc_indirect_contact_intrinsic_microinverter_battery_subset" class="col-span-12"
            label="Assurée intrinsèquement (micro-onduleur + batterie sur bus AC)" />

        <!-- (6b) SLT mode autonome -->
        <p class="col-span-12 font-semibold"><span class="text-sky-500">(6b)</span> SLT en mode autonome :</p>
        <UFormField label="Description SLT (mode autonome)" class="col-span-12 flex items-center gap-4">
            <UInput v-model="state.autonomous_mode_slt_description" class="w-full" />
        </UFormField>
        <UCheckbox v-model="state.autonomous_mode_neutral_contactor_management_commitment" class="col-span-12"
            label="Engagement respect schéma SLT compatible toutes configurations (NF C 15-100 4-41)" />

        <!-- (7a) Distribution DC / Batterie -->
        <p class="col-span-12 font-semibold"><span class="text-sky-500">(7a)</span> Distribution DC ou Batterie :</p>
        <UFormField label="Udc (V)" class="col-span-12 md:col-span-5 flex items-center gap-4">
            <UInput v-model="state.udc_voltage" type="number" class="w-full" />
        </UFormField>

        <!-- (7b) Batterie Plomb -->
        <p class="col-span-12 font-semibold"><span class="text-sky-500">(7b)</span> Batterie Plomb :</p>
        <div class="col-span-12 grid grid-cols-3 gap-2">
            <p class="col-span-3 md:col-span-1 font font-medium">Produit CxU :</p>
            <UCheckbox v-model="state.lead_battery_cxu_le_1000" label="C(Ah) x U(V) ≤ 1000" />
            <UCheckbox v-model="state.lead_battery_cxu_gt_1000" label="C(Ah) x U(V) > 1000" />
        </div>
        <div class="col-span-12 grid grid-cols-4 gap-2">
            <p class="col-span-4 md:col-span-1 font font-medium">Ventilation :</p>
            <UCheckbox v-model="state.lead_battery_ventilation_natural" label="Naturelle" />
            <UCheckbox v-model="state.lead_battery_ventilation_forced" label="Forcée" />
            <UCheckbox v-model="state.lead_battery_ventilation_none" label="Aucune" />
        </div>

        <!-- (7c) Batterie Li-ion -->
        <p class="col-span-12 font-semibold"><span class="text-sky-500">(7c)</span> Batterie Li-ion :</p>
        <UFormField label="Nombre de batteries" class="col-span-12 md:col-span-6 flex items-center gap-4">
            <UInput v-model="state.li_ion_battery_count" type="number" class="w-full" />
        </UFormField>
        <div class="col-span-12 grid grid-cols-1 md:grid-cols-2 gap-2">
            <UCheckbox v-model="state.li_ion_battery_room_yes_commitment" label="Local batterie conforme (§14.6.2.3)" />
            <UCheckbox v-model="state.li_ion_battery_room_no_commitment"
                label="Hors local batterie conforme (§14.6.2.4)" />
        </div>
        <p class="col-span-12 md:col-span-6 font font-medium">Energie de stockage (Si hors local batterie) :</p>
        <UCheckbox class="col-span-6 md:col-span-3" v-model="state.li_ion_battery_outside_room_energy_le_15kwh"
            label="≤ 15 kWh" />
        <UCheckbox class="col-span-6 md:col-span-3" v-model="state.li_ion_battery_outside_room_energy_gt_15kwh"
            label="> 15 kWh" />

        <!-- (7d) Autre type de batterie -->
        <p class="col-span-12 font-semibold"><span class="text-sky-500">(7d)</span> Autre type de batterie :</p>
        <UFormField label="Description" class="col-span-12 md:col-span-6 flex items-center gap-4">
            <UInput v-model="state.other_battery_description" class="w-full" />
        </UFormField>
        <UCheckbox v-model="state.other_battery_norm_and_installation_commitment" class="col-span-12"
            label="Conformes norme sécurité produit & mise en oeuvre (§421.1 NF C 15-100)" />
    </div>
</template>