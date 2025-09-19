export interface DocumentItem { id: string; pdf: string }

export interface UserDocumentsResponse {
  quotes: DocumentItem[]
  invoices: DocumentItem[]
  cerfa16702: DocumentItem[]
  representation_mandates: DocumentItem[]
  consuels: DocumentItem[]
  enedis_mandates: DocumentItem[]
  technical_visit_reports: DocumentItem[]
  installation_reports: DocumentItem[]
}