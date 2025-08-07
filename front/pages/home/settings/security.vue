<script setup lang="ts">
import { USeparator } from '#components';
import type { FormError, FormSubmitEvent } from '#ui/types'

const toast = useToast()
const loading = ref(false)

interface SecurityForm {
    old_password: string;
    new_password: string;
    new_password2: string;
}

const state = ref<SecurityForm>({
    old_password: '',
    new_password: '',
    new_password2: ''
});

const showCurrentPassword = ref(false);
const showPassword1 = ref(false);
const showPassword2 = ref(false);

const toggleCurrentPassword = () => {
    showCurrentPassword.value = !showCurrentPassword.value;
};

const togglePassword1 = () => {
    showPassword1.value = !showPassword1.value;
};

const togglePassword2 = () => {
    showPassword2.value = !showPassword2.value;
};

const validatePassword = (password: string): string[] => {
    const errors: string[] = [];

    if (password.length < 8) {
        errors.push('Le mot de passe doit contenir au moins 8 caractères');
    }

    if (!/\d/.test(password)) {
        errors.push('Le mot de passe doit contenir au moins un chiffre');
    }

    if (!/[a-zA-Z]/.test(password)) {
        errors.push('Le mot de passe doit contenir au moins une lettre');
    }

    return errors;
};

const validate = (state: SecurityForm): FormError[] => {
    const errors: FormError[] = [];

    if (!state.old_password?.trim()) {
        errors.push({ name: 'old_password', message: 'Mot de passe actuel obligatoire' });
    }

    if (!state.new_password?.trim()) {
        errors.push({ name: 'new_password', message: 'Nouveau mot de passe obligatoire' });
    } else {
        const passwordErrors = validatePassword(state.new_password);
        if (passwordErrors.length > 0) {
            errors.push({ name: 'new_password', message: passwordErrors[0] });
        }
    }

    if (!state.new_password2?.trim()) {
        errors.push({ name: 'new_password2', message: 'Confirmation du nouveau mot de passe obligatoire' });
    } else if (state.new_password !== state.new_password2) {
        errors.push({ name: 'new_password2', message: 'Les mots de passe ne correspondent pas' });
    }

    return errors;
};

async function onSubmit(event: FormSubmitEvent<SecurityForm>) {
    loading.value = true

    const res = await apiRequest(
        () => $fetch(`/api/users/me/change_password/`, {
            method: "PATCH",
            body: event.data,
            credentials: "include"
        }),
        toast
    )
    if (res) {
        // Réinitialiser le formulaire
        state.value.old_password = ""
        state.value.new_password = ""
        state.value.new_password2 = ""

        toast.add({
            title: "Votre mot de passe a été modifié avec succès",
            color: 'success',
            icon: 'i-heroicons-check-circle'
        });
    }
    loading.value = false
}
</script>
<template>
    <div>
        <div class="p-4">
            <div class="mx-auto">
                <UForm :state="state" :validate="validate" @submit="onSubmit" class="p-4 lg:p-0 space-y-8">

                    <!-- Mot de passe actuel -->
                    <UFormField name="old_password" label="Mot de passe actuel" required
                        description="Requis pour des raisons de sécurité avant de modifier votre mot de passe"
                        class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6 items-start"
                        :ui="{ container: 'lg:col-span-1' }">
                        <UInput v-model="state.old_password" placeholder="Entrez votre mot de passe actuel" size="lg"
                            icon="i-heroicons-lock-closed" :type="showCurrentPassword ? 'text' : 'password'"
                            class="w-full">
                            <template #trailing>
                                <UButton :icon="showCurrentPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'"
                                    size="sm" color="neutral" variant="ghost" @click="toggleCurrentPassword" />
                            </template>
                        </UInput>
                    </UFormField>
                    <USeparator />

                    <!-- Nouveau mot de passe -->
                    <UFormField name="new_password" label="Nouveau mot de passe" required
                        description="Choisissez un mot de passe sécurisé selon les critères ci-dessous"
                        class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6 items-start"
                        :ui="{ container: 'lg:col-span-1' }">
                        <UInput v-model="state.new_password" placeholder="Entrez votre nouveau mot de passe" size="lg"
                            icon="i-heroicons-lock-closed" :type="showPassword1 ? 'text' : 'password'" class="w-full">
                            <template #trailing>
                                <UButton :icon="showPassword1 ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" size="sm"
                                    color="neutral" variant="ghost" @click="togglePassword1" />
                            </template>
                        </UInput>
                    </UFormField>

                    <!-- Exigences du mot de passe -->
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6 items-start">
                        <div></div>
                        <div class="text-xs text-gray-500 dark:text-gray-300 space-y-1">
                            <p>Votre mot de passe doit :</p>
                            <ul class="list-disc list-inside space-y-0.5 ml-2">
                                <li>Contenir au moins 8 caractères</li>
                                <li>Inclure au moins un chiffre</li>
                                <li>Inclure au moins une lettre</li>
                            </ul>
                        </div>
                    </div>

                    <USeparator />

                    <!-- Confirmation du nouveau mot de passe -->
                    <UFormField name="new_password2" label="Confirmer le nouveau mot de passe" required
                        description="Retapez votre nouveau mot de passe pour confirmer"
                        class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6 items-start"
                        :ui="{ container: 'lg:col-span-1' }">
                        <UInput v-model="state.new_password2" placeholder="Confirmez votre nouveau mot de passe"
                            size="lg" icon="i-heroicons-lock-closed" :type="showPassword2 ? 'text' : 'password'"
                            class="w-full">
                            <template #trailing>
                                <UButton :icon="showPassword2 ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" size="sm"
                                    color="neutral" variant="ghost" @click="togglePassword2" />
                            </template>
                        </UInput>
                    </UFormField>

                    <div class="flex justify-end items-start">
                        <UButton type="submit" color="neutral" size="xl" :loading="loading" class="w-full lg:w-auto">
                            <UIcon v-if="!loading" name="i-heroicons-key" class="w-4 h-4 mr-2" />
                            Changer le mot de passe
                        </UButton>
                    </div>

                </UForm>
            </div>
        </div>
    </div>
</template>