<script setup lang="ts">
import { useAuthStore } from "~/store/auth";
import type { FormError } from "#ui/types";

const error = ref("");
const store = useAuthStore();
const route = useRoute();
const from = route.query.from as string;

definePageMeta({
    layout: false,
    middleware: 'auth',
    title: "Connexion",
    meta: [
        { name: "description", content: "Connectez-vous à votre compte pour accéder à vos données." }
    ]
})

const fields = [
    {
        name: "email",
        type: "email" as 'text',
        autocomplete: "on",
        icon: "i-heroicons-envelope",
        size: 'xl' as 'xl',
        required: true,
        label: "Email",
        placeholder: "Entrez votre email",
    },
    {
        name: "password",
        icon: "i-heroicons-lock-closed",
        size: 'xl' as 'xl',
        required: true,
        label: "Mot de passe",
        type: "password" as 'password',
        placeholder: "Entrez votre mot de passe",
    }
];

const isValidEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
};

const validate = (state: any) => {
    const errors: FormError[] = [];
    if (!state.email)
        errors.push({ name: "email", message: "Email requis" });
    else if (!isValidEmail(state.email))
        errors.push({ name: "email", message: "Email invalide" });
    if (!state.password)
        errors.push({ name: "password", message: "Mot de passe requis" });
    return errors;
};

const loading = ref(false);

async function onSubmit(event: any) {
    loading.value = true;
    const response = await store.loginUser(event.data);
    if (response.success) {
        navigateTo(from ? from : '/home', { replace: true });
    } else {
        error.value = response.message;
        setTimeout(() => {
            error.value = "";
        }, 5000);
    }
    loading.value = false;
}
</script>
<template>
    <div class="flex min-h-screen items-center justify-center p-8">
        <div class="w-full max-w-md space-y-8">
            <!-- Logo et branding -->
            <div class="text-center space-y-4">
                <Logo class="mx-auto" />
                <div class="hero-title space-y-2">
                    <h2 class="text-2xl font-bold text-gray-900 font-poppins">
                        Bon retour parmi nous
                    </h2>
                    <p class="text-gray-600 font-poppins">
                        Connectez-vous pour accéder à votre compte
                    </p>
                </div>
            </div>

            <!-- Formulaire de connexion -->
            <UCard class="bg-white/90 backdrop-blur-sm border border-blue-200/50 shadow-xl">
                <UAuthForm :loading="loading" :fields="fields" :validate="validate"
                    :submit="{ label: 'Se connecter', color: 'primary', size: 'xl' }"
                    :validate-on="['input', 'blur', 'change']" class="space-y-6" @submit="onSubmit">
                    <template #password-hint>
                        <ULink to="/forgot-password" class="text-primary hover:text-secondary font-medium"
                            tabindex="-1">
                            Mot de passe oublié ?
                        </ULink>
                    </template>
                    <template #validation>
                        <transition name="fade">
                            <UAlert v-if="error" color="error" icon="i-heroicons-exclamation-triangle" :title="error"
                                class="mb-4" />
                        </transition>
                    </template>
                </UAuthForm>
            </UCard>
            <!-- Liens légaux -->
            <div class="text-center space-y-4">
                <div class="text-sm text-gray-600 font-poppins">
                    En vous connectant, vous acceptez nos
                    <ULink to="/terms" class="text-primary hover:text-secondary font-medium">
                        Conditions d'utilisation
                    </ULink>
                    et notre
                    <ULink to="/privacy" class="text-primary hover:text-secondary font-medium">
                        Politique de confidentialité
                    </ULink>
                </div>
            </div>
        </div>
    </div>
</template>
