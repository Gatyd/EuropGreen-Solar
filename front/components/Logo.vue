<script setup lang="ts">
interface Props {
  size?: 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'lg'
})

// Configuration des tailles pour chaque variante
const sizeConfig = {
  md: {
    container: 'gap-3',
    icon: 'w-16 h-auto',
    text: 'leading-none',
    europ: 'text-xl font-extrabold',
    green: 'text-2xl font-extrabold -mt-0.5',
    solar: 'text-base font-bold mt-0'
  },
  lg: {
    container: 'gap-4',
    icon: 'w-20 h-auto',
    text: 'leading-tight',
    europ: 'text-3xl font-extrabold',
    green: 'text-4xl font-extrabold -mt-1',
    solar: 'text-xl font-bold mt-0.5'
  }
}

const currentSize = sizeConfig[props.size]
</script>

<template>
    <div v-bind="$attrs" class="flex items-center justify-center" :class="currentSize.container">
        <!-- Icône : place logo_icon.png dans src/assets/ -->
        <img src="/logo_icon.png" alt="Europ' Green Solar" :class="currentSize.icon" />

        <!-- Texte (colonne) -->
        <div class="flex flex-col" :class="currentSize.text">
            <!-- EUROP' en bleu du drapeau français -->
            <span class="text-blue-500 tracking-tight" :class="currentSize.europ">
                EUROP'
            </span>

            <!-- GREEN en vert -->
            <span class="text-green-500 tracking-tight" :class="currentSize.green">
                GREEN
            </span>

            <!-- SOLAR en bleu du drapeau français (plus petit) -->
            <span class="text-blue-500 tracking-tight" :class="currentSize.solar">
                SOLAR
            </span>
        </div>
    </div>
</template>
