<script setup lang="ts">
import type { NuxtError } from '#app'

const props = defineProps<{
    error: NuxtError
}>()

const handleError = () => clearError({ redirect: '/' })

const errorMessages: Record<number, { title: string; description: string }> = {
    404: {
        title: 'Page introuvable',
        description: 'Veuillez vérifier l\'adresse ou contacter notre support si vous pensez qu\'il s\'agit d\'une erreur.'
    },
    401: {
        title: 'Authentification requise',
        description: 'Vous devez vous connecter pour accéder à cette page.'
    },
    403: {
        title: 'Accès non autorisé',
        description: 'Vous n\'avez pas les permissions nécessaires pour accéder à cette ressource.'
    },
    500: {
        title: 'Erreur serveur',
        description: 'Une erreur technique s\'est produite. Notre équipe a été notifiée et travaille à résoudre le problème.'
    }
}

const statusCode = computed(() => props.error.statusCode || 500)
const errorInfo = computed(() => errorMessages[statusCode.value] || {
    title: 'Une erreur est survenue',
    description: props.error.message || 'Quelque chose s\'est mal passé. Veuillez réessayer ultérieurement.'
})

const isDev = computed(() => import.meta.dev)

if (import.meta.dev) {
    console.error('Error:', props.error)
}
</script>

<template>
    <UApp>
        <div class="min-h-screen bg-white flex flex-col">

            <!-- Contenu centré -->
            <div class="flex-1 flex flex-col items-center justify-center px-6 pb-20">
                <!-- Logo en haut -->
                <div class="py-8 px-8">
                    <Logo size="md" />
                </div>
                <div class="max-w-2xl w-full text-center space-y-6">
                    <!-- Titre -->
                    <h1 class="text-4xl font-semibold text-gray-900">
                        {{ errorInfo.title }}
                    </h1>

                    <!-- Description -->
                    <p class="text-lg text-gray-600 leading-relaxed">
                        {{ errorInfo.description }}
                    </p>

                    <!-- Bouton retour -->
                    <div class="pt-4">
                        <button @click="handleError"
                            class="inline-flex items-center gap-2 cursor-pointer px-6 py-3 text-base font-medium text-white bg-secondary-900 hover:bg-secondary-800 rounded-lg transition-colors duration-200">
                            Retourner à l'accueil
                        </button>
                    </div>
                </div>

                <!-- Stack trace en dev (discret en bas) -->
                <div v-if="isDev && error.stack" class="mt-16 max-w-4xl w-full">
                    <details class="group">
                        <summary class="cursor-pointer text-xs text-gray-400 hover:text-gray-600 text-center mb-4 select-none">
                            Détails techniques (développement)
                        </summary>
                        <pre class="text-xs text-gray-600 bg-gray-50 p-4 rounded-lg overflow-x-auto border border-gray-200">{{ error.stack }}</pre>
                    </details>
                </div>
            </div>
        </div>
    </UApp>
</template>
