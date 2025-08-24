<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const route = useRoute()

const links: NavigationMenuItem[][] = [[{
    icon: 'i-heroicons-user-plus',
    label: "Prospects",
    to: "/home/customers/prospects",
},
{
    icon: 'i-heroicons-user-group',
    label: "Clients",
    to: "/home/customers/list",
}
]]

</script>

<template>
    <div class="sticky top-0 z-50 bg-white">
        <UDashboardNavbar :title="route.path.startsWith('/home/customers/prospects') ? 'Prospects' : 'Clients'" class="lg:text-2xl font-semibold"
            :ui="{ root: 'h-12 lg:h-(--ui-header-height)' }" />

        <UDashboardToolbar class="py-0 px-1.5 overflow-x-auto md:block">
            <UNavigationMenu :items="links" />
        </UDashboardToolbar>
    </div>

    <NuxtPage class="lg:mt-4 lg:ps-3 mb-4" />

</template>
