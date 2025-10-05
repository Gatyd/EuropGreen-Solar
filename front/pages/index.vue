<script setup lang="ts">
definePageMeta({ layout: 'public' })

useSeoMeta({
  title: 'Plateforme Client - EUROP\' GREEN SOLAR',
  description: 'Suivez votre installation solaire, accédez à vos documents, contactez notre SAV et bénéficiez du programme de parrainage.',
})

const scrollToSection = (id: string) => {
  const element = document.querySelector(id)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}
</script>

<template>
  <div class="min-h-screen bg-white">
    <LandingHero @scroll-to-section="scrollToSection" />
    <LandingInstallationSection />
    <LandingSAVSection />
    <LandingParrainageSection />
    <LandingCTASection />
  </div>
</template>