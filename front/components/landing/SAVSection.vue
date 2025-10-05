<script setup lang="ts">
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

if (import.meta.client) {
  gsap.registerPlugin(ScrollTrigger)
}

const sectionRef = ref<HTMLElement>()

const features = [
  {
    icon: 'i-heroicons-bolt',
    title: 'Réponse rapide',
    description: 'Traitement prioritaire de vos demandes avec suivi transparent.'
  },
  {
    icon: 'i-heroicons-shield-check',
    title: 'Suivi personnalisé',
    description: 'Historisation complète de vos échanges et demandes.'
  },
  {
    icon: 'i-heroicons-document-text',
    title: 'Assistance complète',
    description: 'Support sur documents, factures, garanties et démarches.'
  },
  {
    icon: 'i-heroicons-user-group',
    title: 'Support humain',
    description: 'Un expert répond directement, sans automatisation.'
  }
]

const processSteps = [
  {
    number: 1,
    title: 'Décrivez votre besoin',
    description: 'Remplissez le formulaire avec tous les détails nécessaires.'
  },
  {
    number: 2,
    title: 'Analyse par un expert',
    description: 'Un technicien qualifié étudie votre demande en profondeur.'
  },
  {
    number: 3,
    title: 'Réponse par email',
    description: 'Solution détaillée adaptée à votre situation spécifique.'
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
  <section id="sav" ref="sectionRef" class="py-20 sm:py-24 bg-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="text-center mb-16 animate-item">
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-secondary-100 text-secondary-700 text-sm font-semibold mb-6">
          <UIcon name="i-heroicons-chat-bubble-left-right" class="w-4 h-4" />
          <span>Service Après-Vente</span>
        </div>
        <h2 class="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
          Une assistance
          <span class="block sm:inline text-secondary-600">réactive et personnalisée</span>
        </h2>
        <p class="text-lg sm:text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
          Notre équipe dédiée répond à vos questions et résout vos problématiques rapidement,
          avec un suivi humain et professionnel.
        </p>
      </div>

      <!-- Grille des fonctionnalités -->
      <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
        <div v-for="(feature, index) in features" :key="index" class="animate-item">
          <UCard class="h-full hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
            <div class="p-6">
              <div class="w-14 h-14 rounded-xl bg-secondary-100 text-secondary-600 flex items-center justify-center mb-4">
                <UIcon :name="feature.icon" class="w-7 h-7" />
              </div>
              <h3 class="text-lg font-bold text-gray-900 mb-2">{{ feature.title }}</h3>
              <p class="text-gray-600 text-sm leading-relaxed">{{ feature.description }}</p>
            </div>
          </UCard>
        </div>
      </div>

      <!-- Processus -->
      <div class="animate-item mb-12">
        <UCard class="bg-gradient-to-br from-gray-50 to-secondary-50 border-2 border-secondary-200">
          <div class="p-8 sm:p-12">
            <div class="text-center mb-12">
              <h3 class="text-2xl sm:text-3xl font-bold text-gray-900 mb-3">
                Comment ça fonctionne ?
              </h3>
              <p class="text-gray-600">Un processus simple et efficace en 3 étapes</p>
            </div>
            
            <div class="grid sm:grid-cols-3 gap-8 sm:gap-12">
              <div v-for="step in processSteps" :key="step.number" class="text-center">
                <div class="w-16 h-16 rounded-full bg-secondary-600 text-white text-2xl font-bold flex items-center justify-center mx-auto mb-4 shadow-lg">
                  {{ step.number }}
                </div>
                <h4 class="font-bold text-gray-900 mb-2 text-lg">{{ step.title }}</h4>
                <p class="text-gray-600 text-sm leading-relaxed">{{ step.description }}</p>
              </div>
            </div>

            <div class="mt-10 text-center">
              <UButton 
                to="/login" 
                size="xl" 
                color="secondary"
                icon="i-heroicons-paper-airplane"
                trailing
                class="shadow-lg"
              >
                Contacter le support
              </UButton>
            </div>
          </div>
        </UCard>
      </div>

      <!-- Garantie Badge -->
      <div class="text-center animate-item">
        <div class="inline-flex items-center gap-3 px-6 py-4 rounded-xl bg-secondary-100 border-2 border-secondary-300">
          <UIcon name="i-heroicons-shield-check" class="w-8 h-8 text-secondary-600" />
          <div class="text-left">
            <div class="font-bold text-secondary-900 text-lg">Garantie 1 an</div>
            <div class="text-sm text-secondary-700">Sur l'ensemble de votre installation</div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
