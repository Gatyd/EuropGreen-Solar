<script setup lang="ts">
import { USeparator } from '#components';
import type { FormSubmitEvent } from '#ui/types'
import { useAuthStore } from '~/store/auth';
import type { User } from '~/types';

const auth = useAuthStore()
const toast = useToast()
const loading = ref(false)
const showDeleteModal = ref(false)

const { user } = storeToRefs(useAuthStore());

const state = reactive({
    first_name: user.value?.first_name,
    last_name: user.value?.last_name,
    email: user.value?.email
})

function validate(state: any) {
    const errors = []
    if (!state.first_name) errors.push({ name: 'first_name', message: 'Prénom(s) obligatoire(s).' })
    if (!state.last_name) errors.push({ name: 'last_name', message: 'Nom obligatoire.' })
    if (!state.email) errors.push({ name: 'email', message: 'Adresse email obligatoire.' })
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(state.email))
        errors.push({ name: 'email', message: 'Adresse email invalide' })
    return errors
}

async function onSubmit(event: FormSubmitEvent<any>) {
    loading.value = true
    const updatedUser = await apiRequest<User>(
        () => $fetch(`/api/users/me/`, {
            method: "PATCH",
            body: event.data,
            credentials: "include"
        }),
        toast
    )
    if (updatedUser) {
        auth.setUser(updatedUser)
        toast.add({
            title: "Votre compte a été mis à jour avec succès",
            color: 'success',
            icon: 'i-heroicons-check-circle'
        })
    }
    loading.value = false
}
</script>
<template>
    <div class="overflow-auto">
        <div class="p-4">
            <div class="mx-auto">
                <UForm :state="state" :validate="validate" @submit="onSubmit" class="p-4 lg:p-0 space-y-8">

                    <!-- Nom -->
                    <UFormField name="last_name" label="Nom" required description="Apparaîtra dans les communications"
                        class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6 items-start"
                        :ui="{ container: 'lg:col-span-1' }">
                        <UInput v-model="state.last_name" autocomplete="last_name" icon="i-heroicons-user" size="lg"
                            placeholder="Entrez votre prénom" class="w-full" />
                    </UFormField>
                    <USeparator />

                    <!-- Prénom -->
                    <UFormField name="first_name" label="Prénom" required
                        description="Apparaîtra dans les communications"
                        class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6 items-start"
                        :ui="{ container: 'lg:col-span-1' }">
                        <UInput v-model="state.first_name" autocomplete="first_name" icon="i-heroicons-user-16-solid"
                            size="lg" placeholder="Entrez votre prénom" class="w-full" />
                    </UFormField>
                    <USeparator />

                    <!-- Email -->
                    <UFormField name="email" label="Email" description="Utilisée pour la connexion et les notifications"
                        required class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6 items-start"
                        :ui="{ container: 'lg:col-span-1' }">
                        <UInput v-model="state.email" type="email" autocomplete="email" icon="i-heroicons-envelope"
                            size="lg" placeholder="Entrez votre adresse email" class="w-full" :disabled="user?.role !== 'admin' && user?.role !== 'customer'" />
                    </UFormField>
                    <USeparator />

                    <!-- Section actions avec notice et bouton -->
                    <div class="pt-4 space-y-6">
                        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
                            <!-- Notice de sécurité -->
                            <div
                                class="p-4 bg-blue-50 dark:bg-blue-950/30 rounded-lg border border-blue-200 dark:border-blue-800">
                                <div class="flex items-start gap-3">
                                    <UIcon name="i-heroicons-information-circle"
                                        class="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
                                    <div class="text-sm text-blue-800 dark:text-blue-200">
                                        <p class="font-medium mb-1">Protection de vos données</p>
                                        <p class="text-blue-600 dark:text-blue-300">
                                            Vos informations personnelles sont sécurisées et ne seront jamais partagées
                                            avec des tiers sans votre consentement.
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <!-- Bouton de sauvegarde -->
                            <div class="flex justify-end items-start">
                                <UButton type="submit" color="neutral" size="xl" :loading="loading"
                                    class="w-full lg:w-auto">
                                    <UIcon v-if="!loading" name="i-heroicons-check" class="w-4 h-4 mr-2" />
                                    Sauvegarder les modifications
                                </UButton>
                            </div>
                        </div>
                    </div>

                </UForm>

                <!-- Section Dangereuse -->
                <!-- <div class="mt-8 p-6 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800 rounded-lg">
                    <h3 class="text-lg font-semibold text-red-900 dark:text-red-100 mb-2 flex items-center gap-2">
                        <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5 text-red-600 dark:text-red-400" />
                        Section dangereuse
                    </h3>
                    <p class="text-sm text-red-700 dark:text-red-300 mb-4">
                        Si vous ne souhaitez plus utiliser notre service, vous avez la possibilité de supprimer
                        définitivement votre compte. Cette action est irréversible et entraînera la perte de toutes vos
                        données personnelles et de votre historique.
                    </p>
                    <UButton color="error" variant="outline" size="lg" @click="showDeleteModal = true"
                        class="w-full sm:w-auto">
                        <UIcon name="i-heroicons-trash" class="w-4 h-4 mr-2" />
                        Désactiver mon compte
                    </UButton>
                </div> -->
            </div>
        </div>

        <!-- Modal de suppression de compte -->
        <!-- <SettingAccountDelete v-model="showDeleteModal" /> -->
    </div>
</template>