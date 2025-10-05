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
    <section ref="sectionRef" class="py-20 sm:py-24 bg-white">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="max-w-4xl mx-auto">
                <!-- Card principale -->
                <UCard class="animate-item bg-gradient-to-br from-primary-600 via-primary-700 to-secondary-700 text-white shadow-2xl">
                    <div class="p-8 sm:p-12 text-center space-y-8">
                        <!-- Icône -->
                        <div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-white/20 backdrop-blur-sm">
                            <UIcon name="i-heroicons-rocket-launch" class="w-10 h-10 text-white" />
                        </div>

                        <!-- Titre -->
                        <div class="space-y-4">
                            <h2 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold">
                                Prêt à nous rejoindre ?
                            </h2>
                            <p class="text-lg sm:text-xl text-white/90 max-w-2xl mx-auto leading-relaxed">
                                Développez votre activité et bénéficiez d'un système de rémunération transparent
                                avec des outils professionnels à la pointe de la technologie.
                            </p>
                        </div>

                        <!-- Placeholder pour le formulaire futur -->
                        <div class="pt-4">
                            <div class="bg-white/10 backdrop-blur-sm border-2 border-white/30 rounded-2xl p-8 space-y-4">
                                <div class="flex items-center justify-center gap-3 text-white/80">
                                    <UIcon name="i-heroicons-document-text" class="w-6 h-6" />
                                    <p class="text-lg font-semibold">Formulaire de candidature</p>
                                </div>
                                <p class="text-white/70 text-sm">
                                    Le formulaire d'inscription sera disponible prochainement.
                                </p>
                                <div class="pt-4">
                                    <UButton 
                                        disabled 
                                        size="xl" 
                                        color="neutral" 
                                        variant="solid"
                                        class="cursor-not-allowed opacity-60"
                                    >
                                        Bientôt disponible
                                    </UButton>
                                </div>
                            </div>
                        </div>

                        <!-- Contact alternatif -->
                        <div class="pt-4 border-t border-white/20">
                            <p class="text-white/80 text-sm">
                                En attendant, vous pouvez nous contacter directement :
                            </p>
                            <div class="flex flex-col sm:flex-row items-center justify-center gap-4 mt-4">
                                <UButton 
                                    to="mailto:contact@egs-solaire.fr" 
                                    color="neutral" 
                                    variant="outline"
                                    icon="i-heroicons-envelope"
                                    size="lg"
                                    external
                                >
                                    contact@egs-solaire.fr
                                </UButton>
                                <UButton 
                                    to="tel:+33123456789" 
                                    color="neutral" 
                                    variant="outline"
                                    icon="i-heroicons-phone"
                                    size="lg"
                                    external
                                >
                                    01 23 45 67 89
                                </UButton>
                            </div>
                        </div>
                    </div>
                </UCard>

                <!-- Info supplémentaire -->
                <div class="mt-12 animate-item text-center">
                    <p class="text-gray-600 text-sm">
                        Des questions ? Consultez notre
                        <ULink to="https://egs-solaire.fr/faq" target="_blank" class="text-primary-600 hover:underline font-semibold">
                            FAQ
                        </ULink>
                        ou contactez notre équipe pour plus d'informations.
                    </p>
                </div>
            </div>
        </div>
    </section>
</template>
