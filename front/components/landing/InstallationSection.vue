<script setup lang="ts">
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

if (import.meta.client) {
    gsap.registerPlugin(ScrollTrigger)
}

const sectionRef = ref<HTMLElement>()

const steps = [
    {
        icon: 'i-heroicons-clipboard-document-check',
        title: 'Visite technique',
        description: 'Notre technicien se déplace chez vous pour valider la faisabilité du projet. À l\'issue de cette visite, un rapport détaillé est généré et signé électroniquement par le client et l\'installateur.',
        color: 'primary' as const
    },
    {
        icon: 'i-heroicons-document-text',
        title: 'Mandat de représentation',
        description: 'Pour simplifier vos démarches administratives, nous créons ensemble un mandat de représentation. Ce document nous autorise à effectuer les démarches en votre nom.',
        color: 'primary' as const
    },
    {
        icon: 'i-heroicons-shield-check',
        title: 'Validation administrative',
        description: 'Nous nous occupons de toutes les démarches administratives nécessaires : déclaration préalable en mairie, demande de raccordement Enedis, dossier CONSUEL, etc. Vous suivez l\'avancement en temps réel.',
        color: 'primary' as const
    },
    {
        icon: 'i-heroicons-wrench-screwdriver',
        title: 'Installation physique',
        description: 'Nos équipes certifiées procèdent à l\'installation complète de votre système photovoltaïque. Un procès-verbal de fin de travaux est signé à l\'issue de l\'installation.',
        color: 'primary' as const
    },
    {
        icon: 'i-heroicons-check-badge',
        title: 'Visite CONSUEL',
        description: 'Le CONSUEL (Comité National pour la Sécurité des Usagers de l\'Électricité) vérifie la conformité de votre installation électrique. L\'attestation obtenue est indispensable pour le raccordement.',
        color: 'primary' as const
    },
    {
        icon: 'i-heroicons-bolt',
        title: 'Raccordement Enedis',
        description: 'Une fois la conformité CONSUEL validée, Enedis procède au raccordement physique de votre installation au réseau électrique national. Votre compteur est mis à jour ou remplacé.',
        color: 'primary' as const
    },
    {
        icon: 'i-heroicons-rocket-launch',
        title: 'Mise en service',
        description: 'Votre installation est opérationnelle ! Nous remettons le procès-verbal de réception et vous accompagnons pour la prise en main de votre système de production solaire.',
        color: 'primary' as const
    }
]
const active = ref(0)

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
        stagger: 0.2,
        duration: 0.8,
        ease: 'power3.out'
    })

    setInterval(() => {
        active.value = (active.value + 1) % steps.length
    }, 2000)

})
</script>

<template>
    <section id="installation" ref="sectionRef" class="py-20 sm:py-24 bg-gray-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <!-- Header -->
            <div class="text-center mb-16 animate-item">
                <div
                    class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-100 text-primary-700 text-sm font-semibold mb-6">
                    <UIcon name="i-heroicons-wrench-screwdriver" class="w-4 h-4" />
                    <span>Suivi d'installation</span>
                </div>
                <h2 class="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
                    Suivez votre projet
                    <span class="block sm:inline text-primary-600">étape par étape</span>
                </h2>
                <p class="text-lg sm:text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
                    Visualisez en temps réel l'avancement de votre installation photovoltaïque.
                    De la visite technique à la mise en service, chaque étape est documentée et accessible dans votre
                    espace personnel. <em class="text-secondary font-semibold">Vous recevez un email à chaque validation
                        d'étape.</em>
                </p>
            </div>

            <!-- Timeline détaillée -->
            <div class="animate-item max-w-4xl mx-auto">
                <UTimeline v-model="active" size="3xl" :items="steps"
                    :ui="{ title: 'text-lg', description: 'text-md' }" />
            </div>
        </div>
    </section>
</template>
