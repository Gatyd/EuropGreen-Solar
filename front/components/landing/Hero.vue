<script setup lang="ts">
import gsap from 'gsap'

const emit = defineEmits<{
  (e: 'scrollToSection', id: string): void
}>()

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
    y: 40,
    duration: 0.8
  }, '-=0.3')
  .from('.hero-subtitle', {
    opacity: 0,
    y: 30,
    duration: 0.7
  }, '-=0.4')
  .from('.hero-cta', {
    opacity: 0,
    scale: 0.9,
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
  <section 
    ref="heroRef" 
    class="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-primary-600 via-primary-500 to-secondary-600"
  >
    <!-- Fond animé subtil -->
    <div class="absolute inset-0 overflow-hidden">
      <div class="absolute top-1/4 -left-48 w-96 h-96 bg-primary-400/20 rounded-full blur-3xl animate-pulse"></div>
      <div class="absolute bottom-1/4 -right-48 w-96 h-96 bg-secondary-400/20 rounded-full blur-3xl animate-pulse" style="animation-delay: 1.5s;"></div>
    </div>

    <!-- Contenu principal -->
    <div class="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
      <!-- Badge -->
      <div class="hero-badge inline-flex items-center gap-2 px-5 py-2 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-white mb-8">
        <UIcon name="i-heroicons-bolt" class="w-4 h-4" />
        <span class="text-sm font-medium">Plateforme Client EUROP' GREEN SOLAR</span>
      </div>

      <!-- Titre principal -->
      <h1 class="hero-title text-5xl sm:text-6xl md:text-7xl font-extrabold text-white mb-6 tracking-tight">
        Pilotez votre projet solaire
        <span class="block mt-2 bg-gradient-to-r from-white to-primary-100 bg-clip-text text-transparent">
          en toute simplicité
        </span>
      </h1>

      <!-- Sous-titre -->
      <p class="hero-subtitle text-lg sm:text-xl md:text-2xl text-white/90 mb-10 max-w-3xl mx-auto leading-relaxed">
        Suivi en temps réel, signatures électroniques sécurisées, support dédié.<br class="hidden sm:block" />
        Tout ce dont vous avez besoin, centralisé dans votre espace personnel.
      </p>

      <!-- CTA Buttons -->
      <div class="hero-cta flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
        <UButton 
          size="xl" 
          color="neutral" 
          variant="solid"
          icon="i-heroicons-arrow-down"
          @click="scrollTo('#installation')"
          class="shadow-xl hover:shadow-2xl transition-shadow"
        >
          Découvrir les fonctionnalités
        </UButton>
        <UButton 
          size="xl" 
          color="primary" 
          variant="outline"
          to="/login"
          icon="i-heroicons-arrow-right-end-on-rectangle"
          trailing
          class="border-2 border-white/40 text-white hover:bg-white/10 backdrop-blur-sm"
        >
          Se connecter
        </UButton>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-3 gap-6 sm:gap-8 max-w-3xl mx-auto">
        <div class="hero-stat">
          <div class="text-4xl sm:text-5xl font-bold text-white mb-2">7</div>
          <div class="text-white/80 text-sm sm:text-base">Étapes suivies</div>
        </div>
        <div class="hero-stat">
          <div class="text-4xl sm:text-5xl font-bold text-white mb-2">100%</div>
          <div class="text-white/80 text-sm sm:text-base">Dématérialisé</div>
        </div>
        <div class="hero-stat">
          <div class="text-4xl sm:text-5xl font-bold text-white mb-2">24/7</div>
          <div class="text-white/80 text-sm sm:text-base">Disponible</div>
        </div>
      </div>
    </div>

    <!-- Indicateur scroll -->
    <div class="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
      <UIcon name="i-heroicons-chevron-down" class="w-8 h-8 text-white/50" />
    </div>
  </section>
</template>
