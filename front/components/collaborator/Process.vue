<script setup lang="ts">
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

if (import.meta.client) {
    gsap.registerPlugin(ScrollTrigger)
}

const sectionRef = ref<HTMLElement>()

const steps = [
    {
        icon: 'i-heroicons-user-plus',
        title: 'Apportez des clients',
        description: 'Identifiez des prospects intéressés par une installation photovoltaïque et présentez-les à notre équipe. Vous créez la connexion initiale.',
        color: 'primary' as const
    },
    {
        icon: 'i-heroicons-document-check',
        title: 'Nous gérons le projet',
        description: 'Notre équipe technique prend en charge toutes les étapes : visite technique, démarches administratives, installation et mise en service.',
        color: 'primary' as const
    },
    {
        icon: 'i-heroicons-eye',
        title: 'Suivez l\'avancement',
        description: 'Accédez à votre tableau de bord pour suivre l\'état de chaque projet : clients, prospects, installations en cours et terminées.',
        color: 'primary' as const
    },
    {
        icon: 'i-heroicons-banknotes',
        title: 'Percevez vos commissions',
        description: 'Une fois le projet finalisé et la facturation effectuée, vous recevez votre commission selon les conditions définies dans votre contrat.',
        color: 'primary' as const
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
    <section ref="sectionRef" class="py-20 sm:py-24 bg-gray-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <!-- Header -->
            <div class="text-center mb-16 animate-item">
                <div class="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-100 text-primary-700 text-sm font-semibold mb-6">
                    <UIcon name="i-heroicons-clipboard-document-list" class="w-4 h-4" />
                    <span>Comment ça fonctionne</span>
                </div>
                <h2 class="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
                    Un processus
                    <span class="text-secondary-600">simple et transparent</span>
                </h2>
                <p class="text-lg sm:text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
                    De l'apport de clients à la perception de vos commissions,
                    découvrez comment fonctionne notre collaboration au quotidien.
                </p>
            </div>

            <!-- Timeline -->
            <div class="animate-item max-w-4xl mx-auto">
                <UTimeline :items="steps" />
            </div>

            <!-- Info complémentaire -->
            <div class="mt-16 animate-item">
                <div class="max-w-4xl mx-auto">
                    <UCard class="bg-white border-2 border-gray-200">
                        <div class="grid md:grid-cols-3 gap-8 p-6">
                            <div class="text-center space-y-2">
                                <div class="text-3xl font-bold text-primary-600">
                                    <UIcon name="i-heroicons-clock" class="inline w-8 h-8" />
                                </div>
                                <p class="text-lg font-semibold text-gray-900">Flexibilité totale</p>
                                <p class="text-sm text-gray-600">Travaillez à votre rythme, selon vos disponibilités</p>
                            </div>

                            <div class="text-center space-y-2">
                                <div class="text-3xl font-bold text-primary-600">
                                    <UIcon name="i-heroicons-map-pin" class="inline w-8 h-8" />
                                </div>
                                <p class="text-lg font-semibold text-gray-900">Sans contrainte géographique</p>
                                <p class="text-sm text-gray-600">Développez votre réseau partout en France</p>
                            </div>

                            <div class="text-center space-y-2">
                                <div class="text-3xl font-bold text-primary-600">
                                    <UIcon name="i-heroicons-arrow-trending-up" class="inline w-8 h-8" />
                                </div>
                                <p class="text-lg font-semibold text-gray-900">Évolution constante</p>
                                <p class="text-sm text-gray-600">Plus vous développez, plus vous gagnez</p>
                            </div>
                        </div>
                    </UCard>
                </div>
            </div>
        </div>
    </section>
</template>
