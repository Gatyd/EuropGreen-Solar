<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const links: NavigationMenuItem[][] = [[{
    label: "Compte",
    icon: 'i-heroicons-user-circle',
    to: '/home/settings/account'
}, {
    label: "Sécurité",
    icon: 'i-heroicons-lock-closed',
    to: '/home/settings/security'
}
]]

</script>

<template>
    <div class="sticky top-0 z-50 bg-white">
        <UDashboardNavbar title="Paramètres" class="lg:text-2xl font-semibold" :ui="{root: 'h-12 lg:h-(--ui-header-height)'}" />

        <UDashboardToolbar class="py-0 px-1.5 overflow-x-auto md:block">
            <UNavigationMenu :items="links" />
        </UDashboardToolbar>
    </div>

    <NuxtPage class="lg:mt-4 lg:ps-3 mb-4" />

</template>
