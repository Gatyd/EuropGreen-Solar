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
    description: 'Validation sur site et signature électronique du rapport de visite par le client et l\'installateur.'
  },
  {
    icon: 'i-heroicons-document-text',
    title: 'Mandat de représentation',
    description: 'Signature simplifiée du mandat pour faciliter vos démarches administratives.'
  },
  {
    icon: 'i-heroicons-shield-check',
    title: 'Validation administrative',
    description: 'Suivi transparent de l\'avancement de vos démarches administratives.'
  },
  {
    icon: 'i-heroicons-wrench-screwdriver',
    title: 'Installation réalisée',
    description: 'Pose du matériel et signature du procès-verbal de fin de travaux.'
  },
  {
    icon: 'i-heroicons-check-badge',
    title: 'Visite CONSUEL',
    description: 'Vérification et certification de la conformité de votre installation.'
  },
  {
    icon: 'i-heroicons-bolt',
    title: 'Raccordement ENEDIS',
    description: 'Connexion effective de votre installation au réseau électrique national.'
  },
  {
    icon: 'i-heroicons-rocket-launch',
    title: 'Mise en service',
    description: 'Installation opérationnelle. Remise du procès-verbal de réception finale.'
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
  <section id="installation" ref="sectionRef" class="py-20 sm:py-24 bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="text-center mb-16 animate-item">
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-100 text-primary-700 text-sm font-semibold mb-6">
          <UIcon name="i-heroicons-rocket-launch" class="w-4 h-4" />
          <span>Suivi d'installation</span>
        </div>
        <h2 class="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
          Suivez votre projet
          <span class="block sm:inline text-primary-600">étape par étape</span>
        </h2>
        <p class="text-lg sm:text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
          Visualisez en temps réel l'avancement de votre installation, signez électroniquement vos documents
          et accédez à l'ensemble de vos pièces administratives 24h/24.
        </p>
      </div>

      <!-- Timeline -->
      <div class="max-w-4xl mx-auto space-y-6">
        <div v-for="(step, index) in steps" :key="index" class="animate-item">
          <div class="flex gap-6">
            <!-- Icon -->
            <div class="flex flex-col items-center">
              <div class="flex-shrink-0 w-12 h-12 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center ring-4 ring-white shadow-md">
                <UIcon :name="step.icon" class="w-6 h-6" />
              </div>
              <div v-if="index < steps.length - 1" class="w-px bg-gray-200 flex-1 my-2"></div>
            </div>
            
            <!-- Content -->
            <div class="flex-1 pb-8">
              <UCard class="hover:shadow-lg transition-shadow duration-300">
                <div class="flex items-start gap-4 p-4">
                  <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-primary-50 text-primary-600 flex items-center justify-center font-bold text-sm">
                    {{ index + 1 }}
                  </div>
                  <div class="flex-1">
                    <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ step.title }}</h3>
                    <p class="text-gray-600 text-sm leading-relaxed">{{ step.description }}</p>
                  </div>
                </div>
              </UCard>
            </div>
          </div>
        </div>
      </div>

      <!-- Feature Card -->
      <div class="mt-16 animate-item">
        <UCard class="max-w-4xl mx-auto bg-gradient-to-br from-primary-50 to-secondary-50 border-2 border-primary-200">
          <div class="flex flex-col md:flex-row items-center gap-6 p-6">
            <div class="flex-shrink-0">
              <div class="w-16 h-16 rounded-2xl bg-primary-600 text-white flex items-center justify-center">
                <UIcon name="i-heroicons-finger-print" class="w-8 h-8" />
              </div>
            </div>
            <div class="flex-1 text-center md:text-left">
              <h3 class="text-xl font-bold text-gray-900 mb-2">
                Signature électronique sécurisée
              </h3>
              <p class="text-gray-700">
                Signez tous vos documents depuis n'importe quel appareil. 
                Valeur juridique identique à une signature manuscrite.
              </p>
            </div>
            <UButton 
              to="/login" 
              size="lg" 
              color="primary"
              icon="i-heroicons-document-check"
              trailing
              class="flex-shrink-0"
            >
              Mes documents
            </UButton>
          </div>
        </UCard>
      </div>
    </div>
  </section>
</template>
