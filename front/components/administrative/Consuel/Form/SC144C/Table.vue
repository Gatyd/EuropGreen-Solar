<script setup lang="ts">
defineProps<{ state: any }>()
</script>

<template>
    <div class="px-3 md:px-5 pb-4 space-y-4">
        <p class="text-xs font-semibold">Tableau 1 : Paramètres / Caractéristiques de chaque groupe PV ou chaîne PV</p>
        <div class="overflow-auto">
            <table class="min-w-full border border-gray-300 text-[12px]">
                <thead>
                    <tr class="bg-gray-100">
                        <th class="border border-gray-300 p-1 text-left w-[390px] align-bottom">
                            Paramètre
                        </th>
                        <th v-for="i in 5" :key="'col-head-' + i" class="border border-gray-300 p-1 w-20 text-center">
                            {{ i }}
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <!-- A -->
                    <tr>
                        <td class="border border-gray-300 p-1">A. Nombre de chaînes</td>
                        <td v-for="i in 5" :key="'a_' + i" class="border border-gray-300 p-0">
                            <UInput v-model="(state as any)['a_number_of_strings_' + i]"
                                :ui="{ base: 'rounded-none border-0 focus:ring-0' }" />
                        </td>
                    </tr>
                    <!-- B -->
                    <tr>
                        <td class="border border-gray-300 p-1">B. Type & courant (In) dispositif protection
                            chaîne (d)</td>
                        <td v-for="i in 5" :key="'b_' + i" class="border border-gray-300 p-0">
                            <UInput v-model="(state as any)['b_chain_protection_type_in_' + i]"
                                :ui="{ base: 'rounded-none border-0 focus:ring-0' }" />
                        </td>
                    </tr>
                    <!-- C -->
                    <tr>
                        <td class="border border-gray-300 p-1">C. Type & courant (In) dispositif protection
                            groupes (d)</td>
                        <td v-for="i in 5" :key="'c_' + i" class="border border-gray-300 p-0">
                            <UInput v-model="(state as any)['c_group_protection_type_in_' + i]"
                                :ui="{ base: 'rounded-none border-0 focus:ring-0' }" />
                        </td>
                    </tr>
                    <!-- D -->
                    <tr>
                        <td class="border border-gray-300 p-1">
                            D. Protection câble principal PV* (e)
                        </td>
                        <td colspan="5" class="border border-gray-300 p-1 text-center text-base">
                            <div class="mt-1 space-y-1">
                                <div class="flex items-center gap-4">
                                    <UCheckbox v-model="state.d_main_pv_cable_not_applicable"
                                        label="Sans objet" />
                                    <UCheckbox v-model="state.d_main_pv_cable_yes" label="Oui" />
                                    <div v-if="state.d_main_pv_cable_yes" class="flex items-center gap-2">
                                        <span>In :</span>
                                        <UInput v-model="state.d_main_pv_cable_in" class="w-20" size="xs" />
                                        <span>A</span>
                                    </div>
                                </div>
                                <div v-if="state.d_main_pv_cable_yes" class="space-y-1 pl-1">
                                    <div class="flex items-center gap-2">
                                        <span>Assuré par :</span>
                                        <UInput v-model="state.d_main_pv_cable_assured_by" class="w-40"
                                            size="xs" />
                                    </div>
                                </div>
                            </div>
                        </td>
                    </tr>
                    <!-- E -->
                    <tr>
                        <td class="border border-gray-300 p-1">
                            E. Protection câble batterie (e)
                        </td>
                        <td colspan="5" class="border border-gray-300 p-1 text-center text-base">
                            <div class="mt-1 space-y-1 pl-1">
                                <div class="flex items-center gap-2">
                                    <span>In :</span>
                                    <UInput v-model="state.e_battery_cable_in" class="w-20" size="xs" />
                                    <span>A</span>
                                </div>
                                <UCheckbox v-model="state.e_battery_cable_integrated_enclosure"
                                    label="Intégré à une enveloppe contenant la batterie" />
                            </div>
                        </td>
                    </tr>
                    <!-- F -->
                    <tr>
                        <td class="border border-gray-300 p-1">
                            F. Protection câble régulateur (e)
                        </td>
                        <td colspan="5" class="border border-gray-300 p-1 text-center text-base">
                            <div class="mt-1 space-y-1">
                                <div class="flex items-center gap-4">
                                    <UCheckbox v-model="state.f_regulator_cable_not_applicable"
                                        label="Sans objet" />
                                    <UCheckbox v-model="state.f_regulator_cable_yes" label="Oui" />
                                    <div v-if="state.f_regulator_cable_yes" class="flex items-center gap-2 pl-1">
                                        <span>In :</span>
                                        <UInput v-model="state.f_regulator_cable_in" class="w-20" size="xs" />
                                        <span>A</span>
                                    </div>
                                </div>
                            </div>
                        </td>
                    </tr>
                    <!-- G -->
                    <tr>
                        <td class="border border-gray-300 p-1">
                            G. Protection câble utilisation DC* (e)
                        </td>
                        <td colspan="5" class="border border-gray-300 p-1 text-center text-base">
                            <div class="mt-1 space-y-1">
                                <div class="flex items-center gap-4">
                                    <UCheckbox v-model="state.g_dc_usage_cable_not_applicable"
                                        label="Sans objet" />
                                    <UCheckbox v-model="state.g_dc_usage_cable_yes" label="Oui" />
                                    <div v-if="state.g_dc_usage_cable_yes" class="flex items-center gap-2 pl-1">
                                        <span>In :</span>
                                        <UInput v-model="state.g_dc_usage_cable_in" class="w-20" size="xs" />
                                        <span>A</span>
                                    </div>
                                </div>
                            </div>
                        </td>
                    </tr>
                    <!-- H -->
                    <tr>
                        <td class="border border-gray-300 p-1">
                            H. Protection câble DC onduleur* (e)
                        </td>
                        <td colspan="5" class="border border-gray-300 p-1 text-center text-base">
                            <div class="mt-1 space-y-1">
                                <div class="flex items-center gap-4">
                                    <UCheckbox v-model="state.h_inverter_dc_cable_not_applicable"
                                        label="Sans objet" />
                                    <UCheckbox v-model="state.h_inverter_dc_cable_yes" label="Oui" />
                                    <div v-if="state.h_inverter_dc_cable_yes"
                                        class="flex items-center gap-2 pl-1">
                                        <span>In :</span>
                                        <UInput v-model="state.h_inverter_dc_cable_in" class="w-20" size="xs" />
                                        <span>A</span>
                                    </div>
                                </div>
                            </div>
                        </td>
                    </tr>
                    <!-- I -->
                    <tr>
                        <td class="border border-gray-300 p-1">
                            I. Protection coffret distribution DC* (e)
                        </td>
                        <td colspan="5" class="border border-gray-300 p-1 text-center text-base">
                            <div class="mt-1 space-y-1">
                                <div class="flex items-center gap-4">
                                    <UCheckbox v-model="state.i_dc_distribution_box_not_applicable"
                                        label="Sans objet" />
                                    <UCheckbox v-model="state.i_dc_distribution_box_yes" label="Oui" />
                                    <div v-if="state.i_dc_distribution_box_yes"
                                        class="flex items-center gap-2 pl-1">
                                        <span>In :</span>
                                        <UInput v-model="state.i_dc_distribution_box_in" class="w-20"
                                            size="xs" />
                                        <span>A</span>
                                    </div>
                                </div>
                            </div>
                        </td>
                    </tr>
                    <!-- J -->
                    <tr>
                        <td class="border border-gray-300 p-1">
                            J. Protection câble DC autre source AC* (e)
                        </td>
                        <td colspan="5" class="border border-gray-300 p-1 text-center text-base">
                            <div class="mt-1 space-y-1">
                                <div class="flex items-center gap-4">
                                    <UCheckbox v-model="state.j_other_ac_source_dc_cable_not_applicable"
                                        label="Sans objet" />
                                    <UCheckbox v-model="state.j_other_ac_source_dc_cable_yes" label="Oui" />
                                    <div v-if="state.j_other_ac_source_dc_cable_yes"
                                        class="flex items-center gap-2 pl-1">
                                        <span>In :</span>
                                        <UInput v-model="state.j_other_ac_source_dc_cable_in" class="w-20"
                                            size="xs" />
                                        <span>A</span>
                                    </div>
                                </div>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>