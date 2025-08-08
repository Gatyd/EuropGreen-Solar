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
        title: 'Déploiement des fonctionnalités développées',
        description: "",
        date: '2025-08-07',
        features: [
            {
                title: 'Frontend Nuxt',
                description: "Déploiement continu sur vercel",
                link: {
                    label: 'Page actuelle',
                    url: '#'
                }
            },
            {
                title: "Backend django",
                description: 'Modèles et API pour la gestion des utilisateurs',
                badge: ['API'],
                link: {
                    label: 'Voir la documentation',
                    url: `${process.env.PROXY_URL || "http://localhost:8000/"}api/docs/`
                }
            }
        ],
        badge: 'v0.1.0',
        authors: [
            {
                name: 'Thierry APLOGAN',
                description: 'devgatyd@gmail.com',
                avatar: {
                    src: 'https://avatars.githubusercontent.com/u/131877017',
                    alt: 'Avatar de Thierry APLOGAN'
                },
                // to: 'https://github.com/Gatyd',
                // target: '_blank'
            }
        ]
    },
    {
        title: 'Gestion de base des utilisateurs',
        description: "Création, modification et désactivation de compte utilisateur",
        date: '2025-08-07',
        features: [
            {
                title: 'Implémentation de la page de gestion des utilisateurs',
                description: "Possibilité de modifier les informations et accès de tous les utilisateurs",
                link: {
                    label: 'Gérer les utilisateurs',
                    url: '/home/users'
                }
            },
            {
                title: "Routes de gestion des utilisateurs",
                description: 'Modèles et API pour la gestion des utilisateurs',
                badge: ['API'],
                link: {
                    label: 'Voir la documentation',
                    url: `${process.env.PROXY_URL || "http://localhost:8000/"}api/docs/#/users`
                }
            }
        ]
    },
    {
        title: 'Modification de compte et mot de passe',
        description: "Mise à jour des informations de compte et de sécurité",
        date: '2025-08-06',
        features: [
            {
                title: 'Implémentation de la page des paramètres de compte',
                description: "Possibilité de modifier le nom et le prénom de l'utilisateur connecté",
                link: {
                    label: 'Modifier les informations du compte',
                    url: '/home/settings/account'
                }
            },
            {
                title: 'Implémentation de la page des paramètres de sécurité',
                description: "Possibilité de modifier le mot de passe de l'utilisateur connecté",
                link: {
                    label: 'Modifier les informations de sécurité',
                    url: '/home/settings/security'
                }
            },
        ]
    },
    {
        title: 'Connexion et mot de passe oublié',
        description: "Finalisation de la connexion et de la réinitialisation du mot de passe",
        date: '2025-08-05',
        features: [
            {
                title: 'Implémentation de la page de mot de passe oublié',
                description: 'Réinitialisation du mot de passe à base de l\'adresse email de l\'utilisateur',
                link: {
                    label: 'Mot de passe oublié',
                    url: '/forgot-password'
                }
            },
            {
                title: 'Implémentation de la page de connexion',
                description: 'Connexion avec adresse email et mot de passe',
                link: {
                    label: 'Se connecter',
                    url: '/login'
                }
            },
            {
                title: "Routes d'authentification",
                description: 'Modèles et API pour l\'authentification des utilisateurs',
                badge: ['API'],
                link: {
                    label: 'Voir la documentation',
                    url: `${process.env.PROXY_URL || "http://localhost:8000/"}api/docs/#/auth`
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
                                        <UButton v-if="'link' in feature" :label="feature.link?.label"
                                            :to="feature.link?.url" variant="ghost" target="_blank"
                                            trailing-icon="i-heroicons-arrow-top-right-on-square" />
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