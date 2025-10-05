<script setup lang="ts">
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

if (import.meta.client) {
    gsap.registerPlugin(ScrollTrigger)
}

const sectionRef = ref<HTMLElement>()

const advantages = [
    {
        icon: 'i-heroicons-currency-euro',
        title: 'Rémunération attractive',
        description: 'Percevez des commissions compétitives sur chaque projet client que vous apportez. Plus vous développez votre réseau, plus vos revenus augmentent.',
        color: 'primary' as const
    },
    {
        icon: 'i-heroicons-users',
        title: 'Gestion de votre portefeuille',
        description: 'Visualisez tous vos clients et prospects dans un tableau de bord dédié. Suivez l\'évolution de chaque dossier en temps réel.',
        color: 'primary' as const
    },
    {
        icon: 'i-heroicons-chart-bar',
        title: 'Suivi des installations',
        description: 'Accédez aux détails de chaque installation de vos clients : état d\'avancement, documents, planning. Vous restez informé à chaque étape.',
        color: 'primary' as const
    },
    {
        icon: 'i-heroicons-document-text',
        title: 'Outils professionnels',
        description: 'Bénéficiez d\'une plateforme complète avec génération de devis, suivi administratif, signature électronique et gestion documentaire.',
        color: 'primary' as const
    },
    {
        icon: 'i-heroicons-bell-alert',
        title: 'Notifications en temps réel',
        description: 'Recevez des alertes par email à chaque validation d\'étape, nouveau client ou mise à jour importante sur vos dossiers.',
        color: 'primary' as const
    },
    {
        icon: 'i-heroicons-shield-check',
        title: 'Accompagnement personnalisé',
        description: 'Notre équipe vous accompagne dans le développement de votre activité : formation, support technique et commercial.',
        color: 'primary' as const
    }
]

onMounted(() => {
    if (!sectionRef.value) return

    gsap.from(sectionRef.value.querySelectorAll('.animate-item'), {
        scrollTrigger: {
            trigger: sectionRef.value,
            start: 'top 70%',
            toggleActions: 'play none none none'
        },
        opacity: 0,
        y: 40,
        stagger: 0.15,
        duration: 0.8,
        ease: 'power3.out'
    })
})
</script>

<template>
    <section ref="sectionRef" class="py-20 sm:py-24 bg-white">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <!-- Header -->
            <div class="text-center mb-16 animate-item">
                <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-secondary-100 text-secondary-700 text-sm font-semibold mb-6">
                    <UIcon name="i-heroicons-sparkles" class="w-4 h-4" />
                    <span>Avantages collaborateur</span>
                </div>
                <h2 class="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
                    Ce que vous
                    <span class="text-primary-600">gagnez réellement</span>
                </h2>
                <p class="text-lg sm:text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
                    En rejoignant notre réseau de collaborateurs, vous accédez à des outils professionnels
                    et un système de rémunération transparent basé sur vos performances.
                </p>
            </div>

            <!-- Grille d'avantages -->
            <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                <UCard v-for="(advantage, index) in advantages" :key="index"
                    class="animate-item hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                    <div class="space-y-4">
                        <div class="flex items-start justify-between">
                            <div class="w-14 h-14 rounded-2xl bg-primary-100 text-primary-600 flex items-center justify-center flex-shrink-0">
                                <UIcon :name="advantage.icon" class="w-7 h-7" />
                            </div>
                        </div>
                        <div>
                            <h3 class="text-xl font-bold text-gray-900 mb-2">
                                {{ advantage.title }}
                            </h3>
                            <p class="text-gray-600 leading-relaxed">
                                {{ advantage.description }}
                            </p>
                        </div>
                    </div>
                </UCard>
            </div>

            <!-- Call-out supplémentaire -->
            <div class="mt-16 animate-item">
                <UCard class="bg-gradient-to-br from-primary-50 to-secondary-50 border-2 border-primary-200">
                    <div class="flex flex-col md:flex-row items-center gap-6 p-6">
                        <div class="flex-shrink-0">
                            <div class="w-16 h-16 rounded-2xl bg-primary-600 text-white flex items-center justify-center">
                                <UIcon name="i-heroicons-rocket-launch" class="w-8 h-8" />
                            </div>
                        </div>
                        <div class="flex-1 text-center md:text-left">
                            <h3 class="text-xl font-bold text-gray-900 mb-2">
                                Développez votre activité en toute autonomie
                            </h3>
                            <p class="text-gray-700">
                                Vous gérez votre temps, vos clients et votre stratégie commerciale.
                                Nous vous fournissons les outils, vous créez les opportunités.
                            </p>
                        </div>
                    </div>
                </UCard>
            </div>
        </div>
    </section>
</template>
