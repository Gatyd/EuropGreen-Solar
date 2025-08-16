<script setup lang="ts">
import { useAuthStore } from '~/store/auth';

useSeoMeta({
    title: "Europ'Green Solar Application",
    description: "Logiciel de gestion des projets d'installation solaire",
    robots: 'noindex, nofollow'
});

const { user } = storeToRefs(useAuthStore());

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
        id: "requests",
        label: "Demandes",
        icon: "i-heroicons-document-text",
        to: "/home/requests",
        tooltip: {
            text: "Demandes",
        },
    },
    {
        id: "users",
        label: "Utilisateurs",
        icon: "i-heroicons-users",
        to: "/home/users",
        tooltip: {
            text: "Utilisateurs",
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

const accessLink = links.map((link: any) => {
    if (!user.value?.is_superuser) {
        if (link.id === "users") return null
        if (link.id === "home") return null
    }
    if (!user.value?.is_superuser && user.value?.is_staff) {
        const useraccess = user.value?.useraccess;
    //     if (link.id === "home") return null

        if ((link.id === "requests") && !useraccess?.requests) return null
    }

    return link;
}).filter((link: any) => link !== null);

const logout = async () => {
    const authStore = useAuthStore();
    await authStore.logout();
    navigateTo('/login', { replace: true });
};

</script>

<template>

    <UDashboardGroup>
        <UDashboardSidebar collapsible resizable :min-size="14" :default-size="17.5" :max-size="21" :ui="{
            footer: 'block',
            header: 'h-auto lg:pt-2',
        }" toggle-side="right">
            <template #header="{ collapsed }">
                <Logo v-if="!collapsed" size="sm" class="lg:hidden" />
                <Logo v-if="!collapsed" size="md" class="hidden lg:flex" />
                <img v-else src="/logo_icon.png" alt="Icône Europ'Green Solar" class="h-10 w-auto shrink-0" />
            </template>

            <template #default="{ collapsed }">

                <UNavigationMenu :collapsed="collapsed" :items="accessLink" orientation="vertical" :ui="{
                    item: 'my-2'
                }" />

            </template>

            <template #footer="{ collapsed }">
                <div v-if="user">
                    <UButton v-if="collapsed" to="/home/settings/account" variant="ghost"
                        :avatar="{ alt: `${user.first_name.split(' ')[0]} ${user.last_name}`, size: 'md' }" />
                    <UUser v-else :ui="{ root: 'cursor-pointer' }" to="/home/settings/account"
                        :name="`${user.first_name.split(' ')[0]} ${user.last_name.split(' ')[0][0]}.`"
                        :avatar="{ alt: `${user.first_name.split(' ')[0]} ${user.last_name}` }" />

                    <USeparator class="mt-2" />
                </div>

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