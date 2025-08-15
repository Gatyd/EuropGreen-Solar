<template>
    <div class="sticky top-0 z-50 bg-white">
        <UDashboardNavbar title="Demandes" class="lg:text-2xl font-semibold"
            :ui="{ root: 'h-12 lg:h-(--ui-header-height)' }"><template #trailing>
                <UBadge variant="subtle" />
            </template>
            <template #right>
                <UButton color="primary" label="Nouvelle demande" icon="i-heroicons-plus" class="mx-2"
                    @click="" />
            </template>
        </UDashboardNavbar>
    </div>
</template>