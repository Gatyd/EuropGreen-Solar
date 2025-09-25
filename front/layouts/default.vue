<script setup lang="ts">
import { useAuthStore } from '~/store/auth';
import apiRequest from '~/utils/apiRequest'

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
        id: "products",
        label: "Produits / Services",
        icon: "i-heroicons-cube",
        to: "/home/products",
        tooltip: {
            text: "Produits / Services",
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
        id: "offers",
        label: "Offres",
        icon: "i-heroicons-document-check",
        to: "/home/offers",
        tooltip: {
            text: "Offres",
        },
    },
    {
        id: "installations",
        label: "Installations",
        icon: "i-heroicons-wrench-screwdriver",
        to: "/home/installations",
        tooltip: {
            text: "Installations",
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
        id: "customers",
        label: "Prospects / Clients",
        icon: "i-heroicons-user-group",
        defaultOpen: true,
        children: [
            {
                icon: 'i-heroicons-user-plus',
                label: "Prospects",
                to: "/home/customers/prospects",
            },
            {
                icon: 'i-heroicons-user-group',
                label: "Clients",
                to: "/home/customers/list",
            }
        ],
        tooltip: {
            text: "Clients",
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
        if (link.id === "products") return null
        if (link.id === "home") return null
    }
    if (!user.value?.is_superuser && user.value?.is_staff) {
        const useraccess = user.value?.useraccess;

        if ((link.id === "requests") && !useraccess?.requests) return null
        if ((link.id === "offers") && !useraccess?.offers) return null
        if ((link.id === "installations") && !useraccess?.installation) return null
    }
    if (!user.value?.is_staff && !user.value?.is_superuser) {
        if (link.id !== "settings" && link.id !== "installations") return null
    }

    return link;
}).filter((link: any) => link !== null);

const logout = async () => {
    const authStore = useAuthStore();
    await authStore.logout();
    navigateTo('/login', { replace: true });
};

// SAV (Service Après Vente)
const savOpen = ref(false)

</script>

<template>
    <UDashboardGroup>
        <UDashboardSidebar collapsible resizable :min-size="15" :default-size="17.5" :max-size="20" :ui="{
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

            <UTooltip v-if="!user?.is_staff" text="Service après vente" :delay-duration="0" :ui="{ content: 'px-2 py-1 text-base' }">
                <button type="button" @click="savOpen = true" aria-label="Ouvrir le support SAV" class="fixed bottom-5 right-5 h-14 w-14 rounded-full grid place-items-center shadow-xl
                bg-gradient-to-br from-(--ui-primary) to-(--ui-primary)/90 text-white hover:brightness-95 transition-all duration-200
                focus:outline-none focus:ring-4 ring-(--ui-primary)/30">
                    <span
                        class="absolute inset-0 rounded-full animate-[ping_2s_linear_infinite] bg-(--ui-primary)/20"></span>
                    <UIcon name="i-heroicons-lifebuoy" class="relative text-2xl" />
                </button>
            </UTooltip>
        </div>
        <SAVModal v-model="savOpen" />
    </UDashboardGroup>
</template>