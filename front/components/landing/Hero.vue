<script setup lang="ts">
import gsap from 'gsap'

const emit = defineEmits<{
    (e: 'scrollToSection', id: string): void
}>()

const heroRef = ref<HTMLElement>()

onMounted(() => {
    if (!heroRef.value) return

    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } })

    tl.from('.hero-image', {
        opacity: 0,
        scale: 1.1,
        duration: 1
    })
        .from('.hero-title', {
            opacity: 0,
            x: -40,
            duration: 0.8
        }, '-=0.6')
        .from('.hero-subtitle', {
            opacity: 0,
            x: -30,
            duration: 0.7
        }, '-=0.4')
        .from('.hero-cta', {
            opacity: 0,
            y: 20,
            duration: 0.6
        }, '-=0.3')
        .from('.hero-stat', {
            opacity: 0,
            y: 20,
            stagger: 0.1,
            duration: 0.5
        }, '-=0.2')
})

const scrollTo = (id: string) => {
    emit('scrollToSection', id)
}
</script>

<template>
    <section ref="heroRef" class="relative min-h-screen flex items-center overflow-hidden bg-white">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8">
            <div class="grid lg:grid-cols-2 gap-8 lg:gap-12 items-center min-h-screen py-20 lg:py-0 lg:pb-20">

                <!-- Contenu texte à gauche (ordre 2 sur mobile, ordre 1 sur desktop) -->
                <div class="order-2 lg:order-1 space-y-8">
                    <!-- Titre principal -->
                    <h1
                        class="hero-title text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-extrabold text-gray-900 tracking-tight">
                        Pilotez votre projet solaire
                        <span
                            class="block mt-2 bg-gradient-to-r from-gray-900 to-secondary-600 bg-clip-text text-transparent">
                            en toute simplicité
                        </span>
                    </h1>

                    <!-- Sous-titre -->
                    <p class="hero-subtitle text-lg sm:text-xl text-gray-600 leading-relaxed max-w-xl">
                        Suivi en temps réel, signatures électroniques sécurisées, support dédié. Tout ce dont vous avez
                        besoin, centralisé dans votre espace personnel.
                    </p>

                    <!-- CTA Buttons -->
                    <div class="hero-cta flex flex-col sm:flex-row gap-4">
                        <UButton size="xl" color="primary" variant="solid" icon="i-heroicons-arrow-down"
                            @click="scrollTo('#installation')" class="shadow-lg hover:shadow-xl transition-shadow">
                            Découvrir les fonctionnalités
                        </UButton>
                    </div>

                    <!-- Stats -->
                    <div class="grid grid-cols-3 gap-6 pt-8 border-t border-gray-200">
                        <div class="hero-stat">
                            <div class="text-3xl sm:text-4xl font-bold text-primary-600 mb-1">7</div>
                            <div class="text-gray-600 text-sm">Étapes suivies</div>
                        </div>
                        <div class="hero-stat">
                            <div class="text-3xl sm:text-4xl font-bold text-primary-600 mb-1">100%</div>
                            <div class="text-gray-600 text-sm">Dématérialisé</div>
                        </div>
                        <div class="hero-stat">
                            <div class="text-3xl sm:text-4xl font-bold text-primary-600 mb-1">24/7</div>
                            <div class="text-gray-600 text-sm">Disponible</div>
                        </div>
                    </div>
                </div>

                <!-- Image à droite (ordre 1 sur mobile, ordre 2 sur desktop) -->
                <div class="order-1 lg:order-2 relative">
                    <div
                        class="hero-image relative rounded-2xl overflow-hidden">
                        <img src="/landing/hero.png" alt="Installation solaire" class="w-full h-full" />
                    </div>
                </div>

            </div>
        </div>

        <!-- Indicateur scroll -->
        <div class="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce hidden lg:block">
            <UIcon name="i-heroicons-chevron-down" class="w-8 h-8 text-gray-400" />
        </div>
    </section>
</template>
