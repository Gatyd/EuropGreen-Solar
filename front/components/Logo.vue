<template>
    <div v-bind="$attrs" class="flex items-center justify-center gap-4">
        <!-- Icône : place logo_icon.png dans src/assets/ -->
        <img src="/logo_icon.png" alt="Europ' Green Solar" class="w-20 h-auto" />

        <!-- Texte (colonne) -->
        <div class="flex flex-col leading-tight">
            <!-- EUROP' en bleu du drapeau français -->
            <span class="text-blue-500 font-extrabold text-3xl tracking-tight">
                EUROP'
            </span>

            <!-- GREEN en vert -->
            <span class="text-green-500 font-extrabold text-4xl -mt-1 tracking-tight">
                GREEN
            </span>

            <!-- SOLAR en bleu du drapeau français (plus petit) -->
            <span class="text-blue-500 font-bold text-xl mt-0.5 tracking-tight">
                SOLAR
            </span>
        </div>
    </div>
</template>
