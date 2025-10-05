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
    }
]

onMounted(() => {
    if (!sectionRef.value) return

    // S'assurer que les éléments sont visibles par défaut
    gsap.set(sectionRef.value.querySelector('.header-animate'), { opacity: 1, y: 0 })
    gsap.set(sectionRef.value.querySelectorAll('.card-animate'), { opacity: 1, y: 0 })
    gsap.set(sectionRef.value.querySelector('.final-card-animate'), { opacity: 1, y: 0 })

    // Animation pour le header
    gsap.fromTo(sectionRef.value.querySelector('.header-animate'),
        { opacity: 0, y: 30 },
        {
            scrollTrigger: {
                trigger: sectionRef.value,
                start: 'top 70%',
                toggleActions: 'play none none none'
            },
            opacity: 1,
            y: 0,
            duration: 0.8,
            ease: 'power3.out'
        }
    )

    // Animation pour les cartes
    gsap.fromTo(sectionRef.value.querySelectorAll('.card-animate'),
        { opacity: 0, y: 40 },
        {
            scrollTrigger: {
                trigger: sectionRef.value.querySelector('.cards-container'),
                start: 'top 70%',
                toggleActions: 'play none none none'
            },
            opacity: 1,
            y: 0,
            stagger: 0.15,
            duration: 0.8,
            ease: 'power3.out'
        }
    )

    // Animation pour la card finale
    gsap.fromTo(sectionRef.value.querySelector('.final-card-animate'),
        { opacity: 0, y: 30 },
        {
            scrollTrigger: {
                trigger: sectionRef.value.querySelector('.final-card-animate'),
                start: 'top 80%',
                toggleActions: 'play none none none'
            },
            opacity: 1,
            y: 0,
            duration: 0.8,
            ease: 'power3.out'
        }
    )
})
</script>

<template>
    <section ref="sectionRef" class="py-20 sm:py-24 bg-white">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <!-- Header -->
            <div class="text-center mb-16 header-animate">
                <div
                    class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-secondary-100 text-secondary-700 text-sm font-semibold mb-6">
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
            <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8 cards-container">
                <UCard v-for="(advantage, index) in advantages" :key="index"
                    class="card-animate hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                    <div class="p-6 space-y-4">
                        <div
                            class="w-14 h-14 rounded-2xl bg-primary-100 text-primary-600 flex items-center justify-center flex-shrink-0">
                            <UIcon :name="advantage.icon" class="w-7 h-7" />
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
        </div>
    </section>
</template>
