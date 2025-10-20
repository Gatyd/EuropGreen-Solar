<script setup lang="ts">
definePageMeta({ layout: 'public' })

useSeoMeta({
  title: 'APPLICATION - EUROP\' GREEN SOLAR',
  description: 'Suivez votre installation solaire, accédez à vos documents, contactez notre SAV et bénéficiez du programme de parrainage.',
  ogTitle: 'APPLICATION - EUROP\' GREEN SOLAR',
  ogDescription: 'Suivez votre installation solaire, accédez à vos documents, contactez notre SAV et bénéficiez du programme de parrainage.',
  ogImage: '/logo_icon.png',
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