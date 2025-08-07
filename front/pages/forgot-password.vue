<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";
import type { FormError } from "#ui/types";

definePageMeta({
    layout: false,
    middleware: 'auth',
    title: "Mot de passe oublié",
    meta: [
        { name: "description", content: "Réinitialisez votre mot de passe en utilisant votre adresse e-mail." }
    ]
});

const error = ref("");
const successMessage = ref("");
const loading = ref(false);
const countdown = ref(0);
const hasBeenSent = ref(false);
const lastEmail = ref("");
let countdownInterval: NodeJS.Timeout | null = null;

const fields = [
    {
        name: "email",
        type: "text" as 'text',
        autocomplete: "on",
        icon: "i-heroicons-envelope",
        size: 'xl' as 'xl',
        required: true,
        label: 'Email',
        placeholder: 'Entrez votre adresse email',
    },
];

// Computed properties
const isButtonDisabled = computed(() => loading.value || countdown.value > 0);

const buttonLabel = computed(() => {
    if (countdown.value > 0) {
        const minutes = Math.floor(countdown.value / 60);
        const seconds = countdown.value % 60;
        return `Renvoyer dans ${minutes}:${seconds.toString().padStart(2, '0')}`;
    }

    if (hasBeenSent.value) {
        return 'Renvoyer le lien';
    }

    return 'Envoyer le lien';
});

const endpoint = computed(() => {
    return hasBeenSent.value ? '/api/auth/resend-reset-email/' : '/api/auth/forgot-password/';
});

// Functions
const isValidEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
};

const validate = (state: any) => {
    const errors: FormError[] = [];
    if (!state.email?.trim()) {
        errors.push({ name: "email", message: 'Adresse email obligatoire' });
    } else if (!isValidEmail(state.email)) {
        errors.push({ name: "email", message: "Veuillez entrer un email valide" });
    }
    return errors;
};

const startCountdown = () => {
    countdown.value = 120; // 2 minutes en secondes

    countdownInterval = setInterval(() => {
        countdown.value--;
        if (countdown.value <= 0) {
            clearInterval(countdownInterval!);
            countdownInterval = null;
        }
    }, 1000);
};

const clearCountdown = () => {
    if (countdownInterval) {
        clearInterval(countdownInterval);
        countdownInterval = null;
    }
    countdown.value = 0;
};

async function onSubmit(event: any) {
    loading.value = true;
    error.value = "";
    successMessage.value = "";

    try {
        const res = await $fetch(endpoint.value, {
            method: 'POST',
            body: { email: event.data.email }
        });

        successMessage.value = res.message || "Un email de réinitialisation a été envoyé à votre adresse.";
        lastEmail.value = event.data.email;
        hasBeenSent.value = true;
        startCountdown();

    } catch (err: any) {
        error.value = err.data?.message || "Une erreur s'est produite lors de la réinitialisation du mot de passe.";
    } finally {
        loading.value = false;
    }
}

// Lifecycle hooks
onMounted(() => {
    // Vérifier s'il y a un décompte en cours dans le localStorage
    const savedCountdown = localStorage.getItem('passwordResetCountdown');
    const savedEmail = localStorage.getItem('passwordResetEmail');
    const savedTimestamp = localStorage.getItem('passwordResetTimestamp');

    if (savedCountdown && savedEmail && savedTimestamp) {
        const elapsed = Math.floor((Date.now() - parseInt(savedTimestamp)) / 1000);
        const remaining = parseInt(savedCountdown) - elapsed;

        if (remaining > 0) {
            countdown.value = remaining;
            lastEmail.value = savedEmail;
            hasBeenSent.value = true;
            startCountdown();
        } else {
            // Nettoyer le localStorage si le délai est expiré
            localStorage.removeItem('passwordResetCountdown');
            localStorage.removeItem('passwordResetEmail');
            localStorage.removeItem('passwordResetTimestamp');
        }
    }
});

onUnmounted(() => {
    clearCountdown();

    // Sauvegarder l'état dans le localStorage
    if (countdown.value > 0) {
        localStorage.setItem('passwordResetCountdown', countdown.value.toString());
        localStorage.setItem('passwordResetEmail', lastEmail.value);
        localStorage.setItem('passwordResetTimestamp', Date.now().toString());
    }
});
</script>
<template>
    <div class="flex min-h-screen items-center justify-center p-8">
        <div class="w-full max-w-md space-y-8">
            <!-- Logo et branding -->
            <div class="text-center space-y-4">
                <Logo class="mx-auto" />
                <div class="hero-title space-y-2">
                    <h2 class="text-2xl font-bold text-gray-900 font-poppins">
                        Mot de passe oublié
                    </h2>
                    <p class="text-gray-600 font-poppins">
                        Entrez votre adresse email pour recevoir un lien de réinitialisation
                    </p>
                </div>
            </div>

            <!-- Formulaire de connexion -->
            <UCard class="bg-white/90 backdrop-blur-sm border border-blue-200/50 shadow-xl">
                <UAuthForm :loading="loading" :fields="fields" :validate="validate" :submit="{
                    label: buttonLabel,
                    color: countdown > 0 ? 'neutral' : 'primary',
                    size: 'xl',
                    disabled: isButtonDisabled
                }" :validate-on="['input', 'blur', 'change']" class="space-y-6" @submit="onSubmit">
                    <template #validation>
                        <transition name="fade">
                            <div>
                                <!-- Message d'erreur -->
                                <UAlert v-if="error" icon="i-heroicons-exclamation-triangle" color="error"
                                    variant="soft" :title="error"
                                    :close-button="{ icon: 'i-heroicons-x-mark-20-solid', color: 'gray', variant: 'link', padded: false }"
                                    @close="error = ''" />

                                <!-- Message de succès -->
                                <UAlert v-if="successMessage" icon="i-heroicons-check-circle" color="success"
                                    variant="soft" :title="successMessage" />

                                <!-- Information sur le décompte -->
                                <!-- <UAlert v-if="countdown > 0" icon="i-heroicons-clock" color="info" variant="soft"
                                    :title="`Vous pourrez renvoyer l'email dans ${Math.floor(countdown / 60)}:${(countdown % 60).toString().padStart(2, '0')}`"
                                    description="Cette limitation évite l'envoi excessif d'emails." /> -->
                            </div>
                        </transition>
                    </template>
                </UAuthForm>
                <div class="mt-6">
                    <UButton :to="('/login')" icon="i-heroicons-arrow-small-left" label="Retour à la connexion"
                        color="primary" variant="ghost" />
                </div>
            </UCard>
        </div>
    </div>
</template>
