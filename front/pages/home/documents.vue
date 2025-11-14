<script setup lang="ts">

// definePageMeta({ middleware: 'admin' })

type DocItem = { id: string; pdf: string; number?: string }
type DocsPayload = {
  quotes: DocItem[]
  invoices: DocItem[]
  cerfa16702: DocItem[]
  representation_mandates: DocItem[]
  consuels: DocItem[]
  enedis_mandates: DocItem[]
  technical_visit_reports: DocItem[]
  installation_reports: DocItem[]
}

const route = useRoute()
const toast = useToast()
const loading = ref(true)
const docs = ref<DocsPayload | null>(null)

const sections: { key: keyof DocsPayload; title: string; icon: string }[] = [
  { key: 'quotes', title: 'Devis', icon: 'i-heroicons-document-text' },
  { key: 'invoices', title: 'Factures', icon: 'i-heroicons-receipt-percent' },
  { key: 'cerfa16702', title: 'Déclaration préalable (CERFA 16702)', icon: 'i-heroicons-building-office-2' },
  { key: 'representation_mandates', title: 'Mandats de représentation', icon: 'i-heroicons-user' },
  { key: 'consuels', title: 'Consuels', icon: 'i-heroicons-clipboard-document-check' },
  { key: 'enedis_mandates', title: 'Mandats ENEDIS', icon: 'i-heroicons-bolt' },
  { key: 'technical_visit_reports', title: 'Rapports de visite technique', icon: 'i-heroicons-wrench-screwdriver' },
  { key: 'installation_reports', title: "Rapports d'installation", icon: 'i-heroicons-wrench' },
]

const fetchDocs = async () => {
  loading.value = true
  const clientId = route.query.client as string
  const userId = route.query.user as string
  if (!clientId && !userId) {
    docs.value = null
    loading.value = false
    return
  }
  const targetId = clientId || userId
  // Si on passe un user (non-client attendu), on force mode=created
  const query = userId ? { mode: 'created' } : undefined
  const data = await apiRequest<DocsPayload>(
    () => $fetch(`/api/users/${targetId}/documents/`, { credentials: 'include', query }),
    toast
  )
  docs.value = data || null
  loading.value = false
}

const loadDoc = () => {

}

onMounted(fetchDocs)

const fileName = (path: string) => {
  try {
    const u = new URL(path, typeof window !== 'undefined' ? window.location.origin : 'http://localhost')
    return decodeURIComponent(u.pathname.split('/').pop() || path)
  } catch {
    const parts = path.split('/')
    return parts[parts.length - 1] || path
  }
}

const fileUrl = (doc: DocItem) => {
  return doc.pdf || `/print/invoice/${doc.id}?auto=1`
}
</script>

<template>
  <div class="sticky top-0 z-50 bg-white">
    <UDashboardNavbar title="Documents liés" class="lg:text-2xl font-semibold" :ui="{ root: 'h-12 lg:h-(--ui-header-height)' }" />
  </div>

  <div class="px-3 lg:px-4 py-4 space-y-6">
    <USkeleton v-if="loading" class="h-40 w-full" />

    <template v-else-if="docs">
      <UCard v-for="sec in sections" :key="sec.key" class="overflow-hidden">
        <template #header>
          <div class="flex items-center gap-2">
            <UIcon :name="sec.icon" class="text-(--ui-primary)" />
            <span class="font-medium">{{ sec.title }}</span>
            <UBadge v-if="(docs?.[sec.key] || []).length" variant="subtle">{{ (docs?.[sec.key] || []).length }}</UBadge>
          </div>
        </template>

        <div v-if="(docs?.[sec.key] || []).length" class="relative">
          <div class="grid gap-4 overflow-x-auto pb-2 custom-scroll"
               style="grid-auto-flow: column; grid-template-rows: repeat(1, minmax(0, 1fr));">
            <a v-for="d in docs?.[sec.key]" :key="d.id" :href="fileUrl(d)" target="_blank"
               class="w-40 min-w-40 h-28 rounded-lg border border-(--ui-border) hover:border-(--ui-primary) transition-colors p-3 flex flex-col items-center justify-between">
              <UIcon name="i-heroicons-document" class="text-4xl text-(--ui-primary)" />
              <span class="text-xs line-clamp-3 text-center">{{ fileName(d.pdf) || d.number }}</span>
            </a>
          </div>
        </div>
        <div v-else class="text-sm text-(--ui-text-muted)">Aucun document.</div>
      </UCard>
    </template>
  </div>
</template>

<style scoped>
.custom-scroll { scrollbar-width: thin; }
</style>