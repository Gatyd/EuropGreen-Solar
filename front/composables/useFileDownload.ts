/**
 * Composable pour gérer les téléchargements de fichiers depuis l'API
 */
export function useFileDownload() {
    const toast = useToast()

    /**
     * Télécharge un fichier depuis une URL
     * @param url - URL de l'endpoint
     * @param filename - Nom du fichier (optionnel, sera extrait des headers si absent)
     * @param params - Paramètres de requête
     */
    async function downloadFile(
        url: string,
        filename?: string,
        params?: Record<string, string>
    ) {
        try {
            // Construire l'URL avec les paramètres
            const queryString = params
                ? '?' + new URLSearchParams(params).toString()
                : ''

            const response = await $fetch.raw(url + queryString, {
                credentials: 'include',
                method: 'GET',
                responseType: 'blob'
            })

            // Extraire le nom du fichier des headers si non fourni
            if (!filename) {
                const contentDisposition = response.headers.get('content-disposition')
                if (contentDisposition) {
                    const match = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
                    if (match && match[1]) {
                        filename = match[1].replace(/['"]/g, '')
                    }
                }
            }

            // Fallback si toujours pas de nom
            if (!filename) {
                filename = 'download_' + Date.now()
            }

            // Créer un blob et déclencher le téléchargement
            const blob = response._data as Blob
            const blobUrl = window.URL.createObjectURL(blob)

            const link = document.createElement('a')
            link.href = blobUrl
            link.download = filename
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)

            // Nettoyer l'URL du blob
            window.URL.revokeObjectURL(blobUrl)

            toast.add({
                title: 'Téléchargement réussi',
                description: `Le fichier "${filename}" a été téléchargé`,
                color: 'success'
            })

            return true
        } catch (error: any) {
            console.error('Erreur téléchargement:', error)
            toast.add({
                title: 'Erreur de téléchargement',
                description: error.message || 'Impossible de télécharger le fichier',
                color: 'error'
            })
            return false
        }
    }

    return {
        downloadFile
    }
}
