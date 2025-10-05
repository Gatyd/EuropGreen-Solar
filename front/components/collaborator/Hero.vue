<script setup lang="ts">
import gsap from 'gsap'

const heroRef = ref<HTMLElement>()

onMounted(() => {
    if (!heroRef.value) return

    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } })

    tl.from('.hero-badge', {
        opacity: 0,
        y: -20,
        duration: 0.6
    })
        .from('.hero-title', {
            opacity: 0,
            y: 30,
            duration: 0.8
        }, '-=0.3')
        .from('.hero-subtitle', {
            opacity: 0,
            y: 20,
            duration: 0.7
        }, '-=0.4')
        .from('.hero-stats', {
            opacity: 0,
            y: 20,
            stagger: 0.1,
            duration: 0.6
        }, '-=0.3')
})
</script>

<template>
    <section ref="heroRef"
        class="relative min-h-[85vh] flex items-center overflow-hidden bg-gradient-to-br from-white via-primary-50/30 to-secondary-50/30">
        <div class="container mx-auto px-4 sm:px-6 lg:px-8 py-20">
            <div class="max-w-4xl mx-auto text-center space-y-8">
                <!-- Badge -->
                <div
                    class="hero-badge inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-100 text-primary-700 text-sm font-semibold">
                    <UIcon name="i-heroicons-users" class="w-4 h-4" />
                    <span>Rejoignez notre réseau</span>
                </div>

                <!-- Titre principal -->
                <h1 class="hero-title text-5xl sm:text-6xl lg:text-7xl font-extrabold text-gray-900 tracking-tight">
                    Devenez
                    <span
                        class="block mt-2 bg-gradient-to-r from-gray-900 to-secondary-600 bg-clip-text text-transparent">
                        Collaborateur Partenaire
                    </span>
                </h1>

                <!-- Sous-titre -->
                <p class="hero-subtitle text-xl sm:text-2xl text-gray-600 leading-relaxed max-w-3xl mx-auto">
                    Développez votre activité avec EUROP' GREEN SOLAR. Apportez des clients, suivez leurs projets
                    et percevez des commissions attractives grâce à nos outils professionnels.
                </p>

                <!-- Stats -->
                <div class="grid grid-cols-1 sm:grid-cols-3 gap-8 pt-8">
                    <div class="hero-stats space-y-2">
                        <div class="text-4xl font-bold text-primary-600">
                            <UIcon name="i-heroicons-currency-euro" class="inline w-10 h-10" />
                        </div>
                        <p class="text-lg font-semibold text-gray-900">Commissions attractives</p>
                        <p class="text-sm text-gray-600">Rémunération compétitive sur chaque projet</p>
                    </div>

                    <div class="hero-stats space-y-2">
                        <div class="text-4xl font-bold text-primary-600">
                            <UIcon name="i-heroicons-chart-bar" class="inline w-10 h-10" />
                        </div>
                        <p class="text-lg font-semibold text-gray-900">Suivi en temps réel</p>
                        <p class="text-sm text-gray-600">Tableaux de bord dédiés à vos clients</p>
                    </div>

                    <div class="hero-stats space-y-2">
                        <div class="text-4xl font-bold text-primary-600">
                            <UIcon name="i-heroicons-wrench-screwdriver" class="inline w-10 h-10" />
                        </div>
                        <p class="text-lg font-semibold text-gray-900">Outils professionnels</p>
                        <p class="text-sm text-gray-600">Plateforme complète pour gérer vos affaires</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Décoration background -->
        <div class="absolute inset-0 -z-10 overflow-hidden pointer-events-none">
            <div
                class="absolute -top-40 -right-40 w-80 h-80 bg-primary-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob">
            </div>
            <div
                class="absolute -bottom-40 -left-40 w-80 h-80 bg-secondary-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-2000">
            </div>
        </div>
    </section>
</template>

<style scoped>
@keyframes blob {

    0%,
    100% {
        transform: translate(0, 0) scale(1);
    }

    33% {
        transform: translate(30px, -50px) scale(1.1);
    }

    66% {
        transform: translate(-20px, 20px) scale(0.9);
    }
}

.animate-blob {
    animation: blob 7s infinite;
}

.animation-delay-2000 {
    animation-delay: 2s;
}
</style>
