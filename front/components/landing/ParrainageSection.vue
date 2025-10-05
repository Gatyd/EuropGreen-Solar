<script setup lang="ts">
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

if (import.meta.client) {
    gsap.registerPlugin(ScrollTrigger)
}

const sectionRef = ref<HTMLElement>()

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
    <section id="parrainage" ref="sectionRef" class="py-20 sm:py-24 bg-gray-50">
        <div class="mx-auto px-4 sm:px-6 lg:px-8">
            <div class="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
                <!-- Contenu texte à gauche -->
                <div class="animate-item space-y-6">
                    <div
                        class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-100 text-primary-700 text-sm font-semibold">
                        <UIcon name="i-heroicons-gift" class="w-4 h-4" />
                        <span>Programme de parrainage</span>
                    </div>
                    <h2 class="text-4xl sm:text-5xl font-bold text-gray-900">
                        Parrainez et
                        <span class="block text-primary-600">recevez une récompense</span>
                    </h2>
                    <p class="text-lg text-gray-600 leading-relaxed">
                        Recommandez EUROP' GREEN SOLAR à vos proches. Vous recevez une commission attractive
                        et votre filleul bénéficie d'une réduction sur son installation.
                    </p>
                    <div class="pt-4">
                        <ULink to="https://egs-solaire.fr/a-propos/parrainage" target="_blank"
                            class="inline-flex items-center gap-2 text-secondary-600 hover:text-secondary-700 font-semibold transition-colors">
                            <span>En savoir plus sur le parrainage</span>
                            <UIcon name="i-heroicons-arrow-right" class="w-5 h-5" />
                        </ULink>
                    </div>
                </div>

                <!-- Image à droite -->
                <div class="animate-item">
                    <UCard class="overflow-hidden shadow-xl">
                        <img src="/landing/referral.png" alt="Parrainage de client"
                            class="w-full h-full object-cover" />
                    </UCard>
                </div>
            </div>
        </div>
    </section>
</template>
