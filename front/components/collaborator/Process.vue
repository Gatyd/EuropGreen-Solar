<script setup lang="ts">
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

if (import.meta.client) {
    gsap.registerPlugin(ScrollTrigger)
}

const sectionRef = ref<HTMLElement>()

const steps = [
    {
        icon: 'i-heroicons-user-plus',
        title: 'Apportez des clients',
        description: 'Identifiez des prospects intéressés par une installation photovoltaïque et présentez-les à notre équipe. Vous créez la connexion initiale.',
        color: 'primary' as const
    },
    {
        icon: 'i-heroicons-document-check',
        title: 'Nous gérons le projet',
        description: 'Notre équipe technique prend en charge toutes les étapes : visite technique, démarches administratives, installation et mise en service.',
        color: 'primary' as const
    },
    {
        icon: 'i-heroicons-eye',
        title: 'Suivez l\'avancement',
        description: 'Accédez à votre tableau de bord pour suivre l\'état de chaque projet : clients, prospects, installations en cours et terminées.',
        color: 'primary' as const
    },
    {
        icon: 'i-heroicons-banknotes',
        title: 'Percevez vos commissions',
        description: 'Une fois le projet finalisé et la facturation effectuée, vous recevez votre commission selon les conditions définies dans votre contrat.',
        color: 'primary' as const
    }
]

const active = ref(0)

onMounted(() => {
    if (!sectionRef.value) return

    // Animation pour le header
    gsap.from(sectionRef.value.querySelector('.header-animate'), {
        scrollTrigger: {
            trigger: sectionRef.value,
            start: 'top 70%',
            toggleActions: 'play none none none'
        },
        opacity: 0,
        y: 30,
        duration: 0.8,
        ease: 'power3.out'
    })

    // Animation pour la timeline
    gsap.from(sectionRef.value.querySelector('.timeline-animate'), {
        scrollTrigger: {
            trigger: sectionRef.value.querySelector('.timeline-animate'),
            start: 'top 70%',
            toggleActions: 'play none none none'
        },
        opacity: 0,
        y: 40,
        duration: 0.8,
        ease: 'power3.out'
    })

    // Animation pour la card finale
    gsap.from(sectionRef.value.querySelector('.final-card-animate'), {
        scrollTrigger: {
            trigger: sectionRef.value.querySelector('.final-card-animate'),
            start: 'top 80%',
            toggleActions: 'play none none none'
        },
        opacity: 0,
        y: 30,
        duration: 0.8,
        ease: 'power3.out'
    })

    // Auto-cycle pour la timeline
    setInterval(() => {
        active.value = (active.value + 1) % steps.length
    }, 3000)
})
</script>

<template>
    <section ref="sectionRef" class="py-20 sm:py-24 bg-gray-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <!-- Header -->
            <div class="text-center mb-16 header-animate">
                <div
                    class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-100 text-primary-700 text-sm font-semibold mb-6">
                    <UIcon name="i-heroicons-clipboard-document-list" class="w-4 h-4" />
                    <span>Comment ça fonctionne</span>
                </div>
                <h2 class="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
                    Un processus
                    <span class="text-secondary-600">simple et transparent</span>
                </h2>
                <p class="text-lg sm:text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
                    De l'apport de clients à la perception de vos commissions,
                    découvrez comment fonctionne notre collaboration au quotidien.
                </p>
            </div>

            <!-- Timeline avec animation -->
            <div class="timeline-animate max-w-4xl mx-auto">
                <UTimeline v-model="active" size="3xl" :items="steps"
                    :ui="{ title: 'text-lg', description: 'text-md' }" />
            </div>
        </div>
    </section>
</template>
