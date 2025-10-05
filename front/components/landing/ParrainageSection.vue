<script setup lang="ts">
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

if (import.meta.client) {
  gsap.registerPlugin(ScrollTrigger)
}

const sectionRef = ref<HTMLElement>()

const advantages = [
  {
    title: 'Pour vous',
    icon: 'i-heroicons-gift',
    color: 'primary',
    benefits: [
      'Récompense versée dès la finalisation du projet',
      'Suivi en temps réel de vos filleuls',
      'Visibilité sur le statut de paiement',
      'Aucune limite de parrainages'
    ]
  },
  {
    title: 'Pour votre filleul',
    icon: 'i-heroicons-star',
    color: 'secondary',
    benefits: [
      'Réduction immédiate sur son installation',
      'Même qualité de service et matériel',
      'Accompagnement personnalisé',
      'Garantie et SAV identiques'
    ]
  }
]

const dashboardSteps = [
  {
    icon: 'i-heroicons-user-plus',
    title: 'Demande',
    description: 'Nouveau prospect parrainé'
  },
  {
    icon: 'i-heroicons-clipboard-document-list',
    title: 'Offre',
    description: 'Devis en cours'
  },
  {
    icon: 'i-heroicons-banknotes',
    title: 'Commission',
    description: 'Statut de paiement'
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
  <section id="parrainage" ref="sectionRef" class="py-20 sm:py-24 bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="text-center mb-16 animate-item">
        <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-100 text-primary-700 text-sm font-semibold mb-6">
          <UIcon name="i-heroicons-gift" class="w-4 h-4" />
          <span>Programme de parrainage</span>
        </div>
        <h2 class="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
          Parrainez et
          <span class="block sm:inline text-primary-600">recevez une récompense</span>
        </h2>
        <p class="text-lg sm:text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
          Recommandez EUROP' GREEN SOLAR à vos proches. Vous recevez une commission attractive
          et votre filleul bénéficie d'une réduction sur son installation.
        </p>
      </div>

      <!-- Avantages comparatifs -->
      <div class="grid md:grid-cols-2 gap-8 mb-16">
        <div v-for="(advantage, index) in advantages" :key="index" class="animate-item">
          <UCard :class="[
            'h-full border-2',
            advantage.color === 'primary' ? 'border-primary-200 bg-gradient-to-br from-primary-50 to-primary-100' : 'border-secondary-200 bg-gradient-to-br from-secondary-50 to-secondary-100'
          ]">
            <div class="p-8">
              <div class="flex items-center gap-3 mb-6">
                <div :class="[
                  'w-14 h-14 rounded-xl flex items-center justify-center',
                  advantage.color === 'primary' ? 'bg-primary-600 text-white' : 'bg-secondary-600 text-white'
                ]">
                  <UIcon :name="advantage.icon" class="w-7 h-7" />
                </div>
                <h3 class="text-2xl font-bold text-gray-900">{{ advantage.title }}</h3>
              </div>
              <ul class="space-y-3">
                <li v-for="(benefit, idx) in advantage.benefits" :key="idx" class="flex items-start gap-3">
                  <UIcon name="i-heroicons-check-circle" :class="[
                    'w-6 h-6 flex-shrink-0 mt-0.5',
                    advantage.color === 'primary' ? 'text-primary-600' : 'text-secondary-600'
                  ]" />
                  <span class="text-gray-700 leading-relaxed">{{ benefit }}</span>
                </li>
              </ul>
            </div>
          </UCard>
        </div>
      </div>

      <!-- Tableau de bord -->
      <div class="animate-item">
        <UCard class="bg-white border-2 border-primary-200">
          <div class="p-8 sm:p-12">
            <!-- Header -->
            <div class="flex flex-col sm:flex-row items-start sm:items-center gap-4 mb-10">
              <div class="w-16 h-16 rounded-xl bg-primary-100 text-primary-600 flex items-center justify-center flex-shrink-0">
                <UIcon name="i-heroicons-chart-bar" class="w-8 h-8" />
              </div>
              <div>
                <h3 class="text-2xl font-bold text-gray-900 mb-1">Tableau de bord de parrainage</h3>
                <p class="text-gray-600">Suivez l'évolution de vos filleuls et vos récompenses en temps réel</p>
              </div>
            </div>

            <!-- Étapes du dashboard -->
            <div class="grid sm:grid-cols-3 gap-6 mb-10">
              <div v-for="step in dashboardSteps" :key="step.title" class="text-center">
                <div class="p-6 rounded-xl bg-gray-50 border-2 border-gray-200 hover:border-primary-300 transition-colors">
                  <UIcon :name="step.icon" class="w-12 h-12 mx-auto mb-3 text-primary-600" />
                  <h4 class="font-bold text-gray-900 mb-1">{{ step.title }}</h4>
                  <p class="text-sm text-gray-600">{{ step.description }}</p>
                </div>
              </div>
            </div>

            <!-- CTA Box -->
            <div class="bg-gradient-to-r from-primary-50 to-secondary-50 rounded-xl p-6 border-2 border-primary-200">
              <div class="flex flex-col lg:flex-row items-center justify-between gap-6">
                <div class="flex-1 text-center lg:text-left">
                  <h4 class="text-xl font-bold text-gray-900 mb-2">
                    Consultez vos gains en temps réel
                  </h4>
                  <p class="text-gray-700 leading-relaxed">
                    Accédez à votre tableau de bord pour voir l'état de chaque parrainage,
                    le montant des commissions et leur statut de paiement.
                  </p>
                </div>
                <div class="flex flex-col sm:flex-row gap-3 flex-shrink-0">
                  <UButton 
                    to="/login" 
                    size="lg" 
                    color="primary"
                    icon="i-heroicons-user-plus"
                    trailing
                  >
                    Ajouter un filleul
                  </UButton>
                  <UButton 
                    to="https://egs-solaire.fr/a-propos/parrainage" 
                    target="_blank"
                    size="lg" 
                    color="neutral"
                    variant="outline"
                    icon="i-heroicons-information-circle"
                    trailing
                  >
                    En savoir plus
                  </UButton>
                </div>
              </div>
            </div>
          </div>
        </UCard>
      </div>
    </div>
  </section>
</template>
