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
            start: 'top 80%',
            toggleActions: 'play none none none'
        },
        opacity: 0,
        y: 30,
        stagger: 0.1,
        duration: 0.7,
        ease: 'power3.out'
    })
})
</script>

<template>
    <section ref="sectionRef" class="py-20 bg-secondary-900">
        <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 class="animate-item text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-6 leading-tight">
                Prêt à accéder à votre espace client ?
            </h2>
            <p class="animate-item text-lg sm:text-xl text-white/90 mb-10 max-w-2xl mx-auto">
                Connectez-vous dès maintenant pour suivre votre projet, gérer vos documents
                et profiter de toutes les fonctionnalités.
            </p>
            <UButton to="/login" size="xl" color="neutral" variant="subtle"
                icon="i-heroicons-arrow-right-end-on-rectangle" >
                Se connecter
            </UButton>
        </div>
    </section>
</template>
