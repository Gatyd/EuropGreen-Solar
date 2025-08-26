export type InstallationStatus =
  | 'technical_visit'
  | 'representation_mandate'
  | 'administrative_validation'
  | 'installation_completed'
  | 'consuel_visit'
  | 'enedis_connection'
  | 'commissioning'

export interface InstallationForm {
  id: string
  offer: string
  client_first_name: string
  client_last_name: string
  client_address: string
  installation_power: number
  installation_type: string
  status: InstallationStatus
  created_by?: {
    id: string
    first_name: string
    last_name: string
    email: string
  } | null
  created_at: string
  updated_at: string
}
