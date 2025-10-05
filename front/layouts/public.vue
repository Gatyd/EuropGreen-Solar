<script setup lang="ts">
import type { DropdownMenuItem, NavigationMenuItem } from '@nuxt/ui'
import { useAuthStore } from '~/store/auth';

useSeoMeta({
    title: "Europ'Green Solar Application",
    description: "Logiciel de gestion des projets d'installation solaire visant à optimiser et à centraliser la gestion des différentes étapes du projet."
});

const route = useRoute()
const { user } = storeToRefs(useAuthStore());

const items = computed<NavigationMenuItem[]>(() => [
    {
        label: 'Installation',
        to: '/#installation',
        active: route.hash === '#installation'
    },
    {
        label: 'Service Après-Vente',
        to: '/#sav',
        active: route.hash === '#sav'
    },
    {
        label: 'Parrainage',
        to: '/#parrainage',
        active: route.hash === '#parrainage'
    },
    {
        label: 'Collaborateur',
        to: '/collaborateur',
        active: route.path === '/collaborateur'
    },
])

const logout = async () => {
    const authStore = useAuthStore();
    await authStore.logout();
    navigateTo('/login', { replace: true });
};

const dropdownItems: DropdownMenuItem[] = [
    [
        {
            label: user.value?.email || 'Anonyme',
            type: 'label',
            ui: {
                itemLabel: 'whitespace-normal break-words'
            },
        }
    ],
    [
        {
            label: user.value?.is_superuser ? 'Tableau de bord' : user.value?.is_staff ? 'Calendrier' : 'Installation',
            to: `/home${user.value?.is_superuser ? '' : user.value?.is_staff ? '/calendar' : '/installations'}`,
            icon: 'i-heroicons-question-mark-circle'
        },
        {
            label: 'Paramètres',
            to: '/home/settings/account',
            icon: 'i-heroicons-cog-8-tooth'
        },
        {
            label: 'Déconnexion',
            icon: 'i-heroicons-arrow-left-start-on-rectangle-16-solid',
            ui: {
                item: 'cursor-pointer',
                itemLabel: 'text-red-500 dark:text-red-400',
                itemLeadingIcon: 'text-red-500 dark:text-red-400',
            },
            onSelect: () => logout()
        }
    ]
]

const footerItems: NavigationMenuItem[] = [
    {
        label: 'Conditions Générales',
        to: '/terms',
        target: '_blank'
    },
    {
        label: 'Politique de Confidentialité',
        to: '/privacy',
        target: '_blank'
    }
]

</script>

<template>
    <UHeader>
        <template #left>
            <NuxtLink to="/">
                <Logo size="sm" />
            </NuxtLink>
        </template>

        <UNavigationMenu :items="items" />

        <template #body>
            <UNavigationMenu :items="items" orientation="vertical" class="-mx-2.5" />
            <div class="mt-4">
                <UDropdownMenu v-if="user" class="rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
                    :items="dropdownItems" :ui="{
                        content: 'w-48',
                    }">
                    <UUser :ui="{ root: 'cursor-pointer' }"
                        :name="`${user.first_name.split(' ')[0]} ${user.last_name.split(' ')[0][0]}.`"
                        :avatar="{ alt: `${user.first_name.split(' ')[0]} ${user.last_name}` }" />
                </UDropdownMenu>
                <div v-else class="flex items-center space-x-3">
                    <UButton to="/login" color="primary">
                        Se connecter
                    </UButton>
                </div>
            </div>
        </template>

        <template #right>
            <div class="hidden lg:flex">
                <UDropdownMenu v-if="user" class="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
                    :items="dropdownItems" :ui="{
                        content: 'w-48',
                    }">
                    <UUser :ui="{ root: 'cursor-pointer' }"
                        :name="`${user.first_name.split(' ')[0]} ${user.last_name.split(' ')[0][0]}.`"
                        :avatar="{ alt: `${user.first_name.split(' ')[0]} ${user.last_name}` }" />
                </UDropdownMenu>
                <div v-else class="hidden sm:flex items-center space-x-3">
                    <UButton to="/login" color="primary">
                        Se connecter
                    </UButton>
                </div>
            </div>
        </template>
    </UHeader>

    <main class="flex-1">
        <slot />
    </main>

    <USeparator :avatar="{
        src: '/favicon.ico',
        alt: 'Europ\'Green Solar Logo',
        ui: {
            root: 'bg-transparent'
        }
    }" type="dashed" class="h-px" />

    <UFooter>
        <template #left>
            <p class="text-muted text-sm">© {{ new Date().getFullYear() }} EUROP' GREEN SOLAR - Tous droits réservés</p>
        </template>

        <!-- <UNavigationMenu :items="footerItems" variant="link" /> -->

        <template #right>
            <UNavigationMenu :items="footerItems" variant="link" />
        </template>
    </UFooter>
</template>
