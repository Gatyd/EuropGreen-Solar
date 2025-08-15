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
        label: 'Acceuil',
        to: '/',
        active: route.path === '/'
    },
    {
        label: 'Evolution',
        to: '/evolution',
        active: route.path.startsWith('/evolution')
    }
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
            label: 'Paramètres',
            to: '/home/settings/account',
            icon: 'i-heroicons-cog-8-tooth'
        },
        {
            label: 'Aide & Support',
            to: '#',
            icon: 'i-heroicons-question-mark-circle'
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

</script>

<template>
    <UHeader>
        <template #left>
            <Logo size="sm" />
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
            <p class="text-muted text-sm">Copyright © {{ new Date().getFullYear() }}</p>
        </template>

        <!-- <UNavigationMenu :items="footerItems" variant="link" /> -->

        <template #right>
            <UButton icon="i-simple-icons-facebook" variant="ghost" to="#" target="_blank" aria-label="Discord" />
            <UButton icon="i-simple-icons-instagram" variant="ghost" to="#" target="_blank" aria-label="X" />
            <UButton icon="i-simple-icons-tiktok" variant="ghost" to="#" target="_blank" aria-label="GitHub" />
        </template>
    </UFooter>
</template>
