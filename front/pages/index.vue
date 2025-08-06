<script lang="ts" setup>

definePageMeta({
    layout: false
})

useSeoMeta({
    title: "Europ'Green Solar Application",
    description: "Logiciel de gestion des projets d'installation solaire visant à optimiser et à centraliser la gestion des différentes étapes du projet."
});

const versions = [
    {
        title: 'Authentification et gestion des utilisateurs',
        description: "Finalisation de l'authentification et de la gestion des utilisateurs en interconnectant l'API et le frontend",
        date: '2025-08-05',
        features: [
            {
                title: 'Interface d\'administration de base',
                description: 'Gestion des utilisateurs',
                badge: ['Users', 'Access'],
                link: {
                    label: 'Gérer les utilisateurs',
                    url: '/home/users'
                }
            },
            {
                title: 'Implémentation de l\'authentification',
                description: 'Interface de connexion et mot de passe oublié',
                link: {
                    label: 'Se connecter',
                    url: '/login'
                }
            },
            {
                title: 'Gestion des utilisateurs',
                description: 'Modèles et API pour la gestion des comptes utilisateurs',
                badge: ['API'],
                link: {
                    label: 'Voir la documentation',
                    url: `${process.env.PROXY_URL || "http://localhost:8000/"}api/docs/#/users`
                }
            }
        ]
    },
    {
        title: 'Configuration initiale du projet',
        description: 'Mise en place de l\'architecture de base avec Django et Nuxt.js pour Europ\'Green Solar',
        date: '2025-08-04',
        features: [
            {
                title: 'Système d\'authentification',
                description: 'Implémentation des mécanismes d\'auth avec cookies sécurisés',
                badge: ['Auth', 'JWT']
            },
            {
                title: 'Frontend Nuxt',
                description: 'Initialisation et configuration de base de l\'application Nuxt et le serveur Nitro'
            },
            {
                title: 'Backend Django',
                description: 'Initialisation et configuration de base du serveur Django avec API REST'
            }
        ]
        // badge: 'v0.1.0',
        // authors: [
        //     {
        //         name: 'Équipe Dev',
        //         description: 'Configuration initiale',
        //         avatar: {
        //             src: 'https://github.com/github.png'
        //         }
        //     }
        // ]
    },
]

</script>

<template>
    <div class="min-h-screen bg-gray-50">
        <div class="max-w-6xl mx-auto px-4 py-8">
            <!-- En-tête -->
            <div class="text-center mb-12">
                <h1 class="text-4xl font-bold text-green-600 mb-4">Europ'Green Solar</h1>
                <p class="text-xl text-gray-600 mb-2">Plateforme d'énergie solaire en développement</p>
                <div class="bg-yellow-100 border border-yellow-400 text-yellow-800 px-4 py-3 rounded-lg inline-block">
                    <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5 inline mr-2" />
                    Projet en cours de développement - Cette page présente l'évolution du projet
                </div>
                <p class="text-gray-500 mt-4 max-w-2xl mx-auto">
                    À la finalisation, cette page contiendra une présentation attrayante des fonctionnalités
                    de l'application destinée aux clients. Pour le moment, suivez notre progression !
                </p>
            </div>

            <!-- Changelog -->
            <div class="bg-white rounded-lg shadow-lg p-8 mb-8">
                <h2 class="text-2xl font-semibold mb-6 text-gray-800">Évolution du projet</h2>
                <UChangelogVersions :versions="versions">
                    <template #body="{ version }">
                        <div class="mt-4">
                            <!-- <h4 class="text-lg font-medium mb-3 text-gray-700">Fonctionnalités implémentées :</h4> -->
                            <div class="grid gap-2">
                                <div v-for="feature in version.features" :key="feature.title"
                                    class="flex items-start px-3 py-2">
                                    <div class="flex-1">
                                        <div class="flex items-center gap-2 mb-1">
                                            <h5 class="font-medium text-gray-900">{{ feature.title }}</h5>
                                            <UBadge v-for="value in feature.badge" :label="value" variant="soft" />
                                        </div>
                                        <p class="text-sm text-gray-600">{{ feature.description }}</p>
                                        <UButton v-if="'link' in feature" :label="feature.link?.label" :to="feature.link?.url"
                                            variant="ghost" target="_blank" trailing-icon="i-heroicons-arrow-top-right-on-square" />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </template>
                </UChangelogVersions>
            </div>

            <!-- Footer temporaire -->
            <div class="text-center">
                <p class="text-gray-500">
                    🚀 Plus de fonctionnalités arrivent bientôt !
                </p>
            </div>
        </div>
    </div>
</template>