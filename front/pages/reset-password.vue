<script setup lang="ts">
import { ref } from 'vue';
import type { FormError, FormSubmitEvent } from '#ui/types';

definePageMeta({
    layout: false,
    middleware: 'auth',
    title: "Réinitialisation de mot de passe",
    meta: [
        { name: "description", content: "Réinitialisez votre mot de passe en définissant un nouveau mot de passe." }
    ]
});

interface ResetPasswordForm {
    password: string;
    confirmPassword: string;
}

const route = useRoute();

const token = route.query.token as string;

const error = ref("");
const successMessage = ref("");
const loading = ref(false);

const state = ref<ResetPasswordForm>({
    password: '',
    confirmPassword: ''
});

const showPassword = ref(false);
const showConfirmPassword = ref(false);

const togglePassword = () => {
    showPassword.value = !showPassword.value;
};

const toggleConfirmPassword = () => {
    showConfirmPassword.value = !showConfirmPassword.value;
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

const validate = (state: ResetPasswordForm): FormError[] => {
    const errors: FormError[] = [];

    if (!state.password?.trim()) {
        errors.push({ name: 'password', message: "Mot de passe obligatoire" });
    } else {
        const passwordErrors = validatePassword(state.password);
        if (passwordErrors.length > 0) {
            errors.push({ name: 'password', message: passwordErrors[0] });
        }
    }

    if (!state.confirmPassword?.trim()) {
        errors.push({ name: 'confirmPassword', message: "Mot de passe obligatoire" });
    } else if (state.password !== state.confirmPassword) {
        errors.push({ name: 'confirmPassword', message: "Les mots de passe ne correspondent pas" });
    }

    return errors;
};

const onSubmit = async (event: FormSubmitEvent<ResetPasswordForm>) => {
    loading.value = true;
    error.value = "";
    successMessage.value = "";

    try {
        const response = await $fetch('/api/auth/reset-password/', {
            method: 'POST',
            body: {
                token: token,
                new_password: event.data.password,
                confirm_password: event.data.confirmPassword
            }
        });
        successMessage.value = "Votre mot de passe a été réinitialisé avec succès";

        // Redirection vers la page de connexion après 2 secondes
        setTimeout(() => {
            navigateTo('/login');
        }, 1000);

    } catch (err: any) {
        error.value = err.data?.message || "Ce lien de réinitialisation a expiré ou a déjà été utilisé.";
    } finally {
        loading.value = false;
    }
};
</script>

<template>
    <div class="flex min-h-screen items-center justify-center p-8">
        <div class="w-full max-w-md space-y-8">
            <!-- Logo et branding -->
            <div class="text-center space-y-4">
                <Logo class="mx-auto" />
                <div class="hero-title space-y-2">
                    <h2 class="text-2xl font-bold text-gray-900 font-poppins">
                        Réinitialiser le mot de passe
                    </h2>
                    <p class="text-gray-600 font-poppins">
                        Créez un nouveau mot de passe sécurisé
                    </p>
                </div>
            </div>

            <!-- Formulaire de connexion -->
            <UCard class="bg-white/90 backdrop-blur-sm border border-blue-200/50 shadow-xl">
                <UForm :validate="validate" :state="state" class="space-y-4" @submit="onSubmit">
                    <UFormField label="Nouveau mot de passe" name="password" required>
                        <UInput v-model="state.password" placeholder="Entrez votre nouveau mot de passe" size="xl"
                            icon="i-heroicons-lock-closed" :type="showPassword ? 'text' : 'password'" class="w-full">
                            <template #trailing>
                                <UButton :icon="showPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" size="sm"
                                    color="neutral" variant="ghost" @click="togglePassword" />
                            </template>
                        </UInput>
                    </UFormField>

                    <UFormField label="Confirmez le mot de passe" name="confirmPassword" required>
                        <UInput v-model="state.confirmPassword" placeholder="Confirmez votre nouveau mot de passe"
                            :type="showConfirmPassword ? 'text' : 'password'" class="w-full" size="lg"
                            icon="i-heroicons-lock-closed">
                            <template #trailing>
                                <UButton :icon="showConfirmPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'"
                                    size="sm" color="neutral" variant="ghost" @click="toggleConfirmPassword" />
                            </template>
                        </UInput>
                    </UFormField>

                    <div class="text-xs text-gray-500 dark:text-gray-300 space-y-1">
                        <p>Votre mot de passe doit :</p>
                        <ul class="list-disc list-inside space-y-0.5 ml-2">
                            <li>Contenir au moins 8 caractères</li>
                            <li>Inclure au moins un chiffre</li>
                            <li>Inclure au moins une lettre</li>
                        </ul>
                    </div>
                    <transition name="fade">
                        <div>
                            <!-- Message d'erreur -->
                            <UAlert v-if="error" icon="i-heroicons-exclamation-triangle" color="error" variant="soft"
                                :title="error"
                                :close-button="{ icon: 'i-heroicons-x-mark-20-solid', color: 'gray', variant: 'link', padded: false }"
                                @close="error = ''" />

                            <!-- Message de succès -->
                            <UAlert v-if="successMessage" icon="i-heroicons-check-circle" color="success" variant="soft"
                                :title="successMessage" />
                        </div>
                    </transition>

                    <div class="pt-2">
                        <UButton type="submit" label="Réinitialiser le mot de passe" size="lg" block color="primary"
                            class="font-semibold" :loading="loading" />
                    </div>
                </UForm>
                <div class="mt-6">
                    <UButton :to="('/login')" icon="i-heroicons-arrow-small-left" label="Retour à la connexion"
                        color="primary" variant="ghost" />
                </div>
            </UCard>
        </div>
    </div>
</template>
