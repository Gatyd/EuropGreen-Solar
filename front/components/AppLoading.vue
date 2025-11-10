<script setup lang="ts">
// Simple composant de chargement global pendant la résolution de l'utilisateur
// Aucun prop pour l'instant; extensible (message, taille...) si besoin.
</script>

<template>
    <div class="fixed inset-0 flex items-center justify-center bg-white dark:bg-slate-900">
        <div class="flex flex-col items-center space-y-6">
            <div class="relative h-48 w-48">
                <!-- Cercle primaire -->
                <div class="animate-spin-slow rounded-full h-48 w-48 border-4 border-primary/30 border-t-primary"></div>
                <!-- Cercle secondaire décalé -->
                <div
                    class="absolute inset-0 animate-spin-slower rounded-full h-48 w-48 border-4 border-transparent border-l-secondary">
                </div>
                <!-- Logo centré -->
                <img src="/logo_icon.png" alt="Logo Europ'Green Solar"
                    class="absolute inset-0 m-auto h-24 w-24 object-contain" />
            </div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Chargement de votre session...</p>
        </div>
    </div>
</template>

<style scoped>
@keyframes spinSlow {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

@keyframes spinSlower {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(-360deg);
    }
}

.animate-spin-slow {
    animation: spinSlow 1.4s linear infinite;
}

.animate-spin-slower {
    animation: spinSlower 2s linear infinite;
    animation-delay: .25s;
}
</style>
