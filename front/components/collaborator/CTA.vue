<script setup lang="ts">
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import apiRequest from '~/utils/apiRequest'

if (import.meta.client) {
    gsap.registerPlugin(ScrollTrigger)
}

const toast = useToast()
const sectionRef = ref<HTMLElement>()

// État du formulaire
const firstName = ref('')
const lastName = ref('')
const email = ref('')
const phone = ref('')
const role = ref('')
const message = ref('')

const sending = ref(false)
const sent = ref(false)

const charLimit = 5000
const remaining = computed(() => charLimit - message.value.length)

function resetForm() {
    firstName.value = ''
    lastName.value = ''
    email.value = ''
    phone.value = ''
    role.value = ''
    message.value = ''
}

async function submit() {
    if (!firstName.value.trim() || !lastName.value.trim() || !email.value.trim() || !phone.value.trim() || !message.value.trim()) {
        toast.add({
            title: 'Champs requis',
            description: 'Veuillez remplir tous les champs obligatoires.',
            color: 'warning'
        })
        return
    }

    sending.value = true
    const body: any = {
        first_name: firstName.value,
        last_name: lastName.value,
        email: email.value,
        phone: phone.value,
        message: message.value
    }
    if (role.value.trim()) {
        body.role = role.value
    }

    const res = await apiRequest(
        () => $fetch('/api/users/career/', { method: 'POST', credentials: 'include', body }),
        toast
    )

    sending.value = false
    if (res !== null) {
        sent.value = true
    }
}

function newApplication() {
    sent.value = false
    resetForm()
}

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
    <section ref="sectionRef" class="py-20 sm:py-24 bg-gradient-to-br from-gray-50 to-white">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="max-w-4xl mx-auto">
                <!-- En-tête de section -->
                <div class="text-center mb-12 animate-item space-y-4">
                    <h2 class="text-3xl sm:text-4xl font-bold text-gray-900">
                        Prêt à nous rejoindre ?
                    </h2>
                    <p class="text-lg text-gray-600 max-w-2xl mx-auto">
                        Développez votre activité et bénéficiez d'un système de rémunération transparent
                        avec des outils professionnels à la pointe de la technologie.
                    </p>
                </div>

                <!-- Card formulaire -->
                <UCard class="animate-item">
                    <transition name="fade" mode="out-in">
                        <div v-if="!sent" key="form" class="space-y-6">
                            <!-- Conseils -->
                            <div
                                class="bg-primary-50 dark:bg-primary-950 rounded-lg p-4 border border-primary-200 dark:border-primary-800">
                                <h3
                                    class="font-semibold flex items-center gap-2 text-primary-900 dark:text-primary-100 mb-2">
                                    <UIcon name="i-heroicons-light-bulb" class="text-primary-600" />
                                    Conseils pour votre candidature
                                </h3>
                                <ul
                                    class="space-y-1 list-disc ps-5 marker:text-primary-600 text-gray-700 dark:text-gray-300">
                                    <li>Présentez votre expérience et vos motivations clairement</li>
                                    <li>Indiquez le rôle qui vous intéresse (commercial, installateur, collaborateur...)
                                    </li>
                                    <li>Mentionnez vos compétences et qualifications pertinentes</li>
                                </ul>
                            </div>

                            <!-- Informations personnelles -->
                            <div class="grid sm:grid-cols-3 gap-4">
                                <UFormField label="Prénom" required>
                                    <UInput v-model="firstName" placeholder="Jean" :disabled="sending"
                                        icon="i-heroicons-user" class="w-full" size="lg" />
                                </UFormField>
                                <UFormField label="Nom" required>
                                    <UInput v-model="lastName" placeholder="Dupont" :disabled="sending"
                                        icon="i-heroicons-user" class="w-full" size="lg" />
                                </UFormField>
                                <UFormField label="Téléphone" required>
                                    <UInput v-model="phone" type="tel" placeholder="06 12 34 56 78" :disabled="sending"
                                        icon="i-heroicons-phone" class="w-full" size="lg" />
                                </UFormField>
                            </div>

                            <!-- Contact -->
                            <div class="grid sm:grid-cols-2 gap-4">
                                <UFormField label="Email" required>
                                    <UInput v-model="email" type="email" placeholder="jean.dupont@exemple.fr"
                                        :disabled="sending" icon="i-heroicons-envelope" class="w-full" size="lg" />
                                </UFormField>
                                <UFormField label="Rôle souhaité (optionnel)">
                                    <UInput v-model="role" placeholder="Ex: Commercial, Installateur, Collaborateur..."
                                        :disabled="sending" icon="i-heroicons-briefcase" class="w-full" size="lg" />
                                </UFormField>
                            </div>

                            <!-- Message -->
                            <div class="space-y-2">
                                <UFormField label="Votre message / Motivations" required>
                                    <UTextarea v-model="message" :rows="10" :maxlength="charLimit"
                                        placeholder="Parlez-nous de votre parcours, vos compétences, et ce qui vous motive à rejoindre notre équipe..."
                                        :disabled="sending" class="w-full" size="lg" />
                                </UFormField>
                                <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400">
                                    <span>Décrivez précisément votre profil et vos motivations.</span>
                                    <span :class="remaining < 0 ? 'text-red-500' : ''">
                                        {{ message.length }}/{{ charLimit }}
                                    </span>
                                </div>
                            </div>

                            <!-- Boutons -->
                            <div class="flex justify-end gap-2 pt-2">
                                <UButton variant="ghost" color="neutral" label="Réinitialiser"
                                    :disabled="!firstName && !lastName && !email && !phone && !role && !message"
                                    @click="resetForm" size="lg" />
                                <UButton color="primary"
                                    :disabled="!firstName.trim() || !lastName.trim() || !email.trim() || !phone.trim() || !message.trim() || remaining < 0"
                                    :loading="sending" label="Envoyer ma candidature" icon="i-heroicons-paper-airplane"
                                    @click="submit" size="lg" />
                            </div>
                        </div>

                        <!-- Message de succès -->
                        <div v-else key="success" class="space-y-8 py-8 text-center">
                            <div
                                class="mx-auto h-16 w-16 rounded-full bg-green-100 dark:bg-green-900 text-green-600 dark:text-green-400 grid place-items-center">
                                <UIcon name="i-heroicons-check-badge" class="text-3xl" />
                            </div>
                            <div class="space-y-2">
                                <h3 class="text-2xl font-semibold text-gray-900 dark:text-white">Candidature envoyée !
                                </h3>
                                <p class="text-sm text-gray-600 dark:text-gray-400 max-w-md mx-auto">
                                    Merci pour votre intérêt ! Notre équipe examinera votre candidature et vous
                                    contactera
                                    dans les plus brefs délais à l'adresse email fournie.
                                </p>
                            </div>
                            <div class="flex justify-center gap-3">
                                <UButton variant="ghost" size="lg" color="neutral" label="Retour" @click="$router.back()" />
                                <UButton color="primary" size="lg" label="Nouvelle candidature" @click="newApplication" />
                            </div>
                        </div>
                    </transition>
                </UCard>

                <!-- Contact alternatif -->
                <div class="mt-8 animate-item text-center space-y-4">
                    <p class="text-sm text-gray-600 dark:text-gray-400">
                        Vous pouvez également nous contacter directement :
                    </p>
                    <div class="flex flex-col sm:flex-row items-center justify-center gap-3">
                        <UButton to="mailto:contact@egs-solaire.fr" variant="outline" color="neutral"
                            icon="i-heroicons-envelope" label="contact@egs-solaire.fr" external size="lg" />
                        <UButton to="tel:+33970702656" variant="outline" color="neutral" icon="i-heroicons-phone"
                            label="09 70 70 26 56" external size="lg" />
                    </div>
                </div>
            </div>
        </div>
    </section>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.25s;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>
