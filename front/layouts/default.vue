<script setup lang="ts">
import { useAuthStore } from '~/store/auth';

useSeoMeta({
    title: "Europ'Green Solar Application",
    description: "Logiciel de gestion des projets d'installation solaire",
    robots: 'noindex, nofollow'
});

const { user } = storeToRefs(useAuthStore());
const route = useRoute();

const links = [
    {
        id: "home",
        label: "Accueil",
        icon: "i-heroicons-home",
        to: "/home",
        tooltip: {
            text: "Accueil",
        },
    },
    {
        id: "settings",
        label: "Paramètres",
        defaultOpen: true,
        icon: "i-heroicons-cog-8-tooth",
        children: [
            {
                icon: 'i-heroicons-user-circle',
                label: "Compte",
                to: "/home/settings/account",
            },
            {
                icon: 'i-heroicons-lock-closed',
                label: "Sécurité",
                to: "/home/settings/security",
            }
        ],
        tooltip: {
            text: "Paramètres",
        },
    },
]

const logout = async () => {
    const authStore = useAuthStore();
    await authStore.logout();
    navigateTo('/login', { replace: true });
};

</script>

<template>

    <UDashboardGroup>
        <UDashboardSidebar collapsible resizable :min-size="14" :default-size="17.5" :max-size="21" :ui="{
            footer: 'block border-t border-(--ui-border)',
            header: 'h-auto lg:pt-2',
        }" toggle-side="right">
            <template #header="{ collapsed }">
                <Logo v-if="!collapsed" size="md" />
                <img v-else src="/logo_icon.png" alt="Icône Europ'Green Solar" class="h-10 w-auto shrink-0" />
            </template>

            <template #default="{ collapsed }">

                <UNavigationMenu :collapsed="collapsed" :items="links" orientation="vertical" :ui="{
                    item: 'my-2'
                }" />

            </template>

            <template #footer>
                <div class="pb-2">
                    <UButton icon="i-heroicons-arrow-left-start-on-rectangle-16-solid" label="Déconnexion" color="error"
                        variant="ghost" class="w-full justify-start" @click="logout" :ui="{
                            leadingIcon: 'size-5 flex-shrink-0'
                        }" />
                </div>
            </template>
        </UDashboardSidebar>

        <div class="relative bg-white dark:bg-slate-900 min-h-screen w-full overflow-auto">
            <slot />
        </div>
    </UDashboardGroup>
</template>