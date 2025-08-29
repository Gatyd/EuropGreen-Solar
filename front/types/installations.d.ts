import type { Quote } from './billing'

export type InstallationStatus =
  | 'technical_visit'
  | 'representation_mandate'
  | 'administrative_validation'
  | 'installation_completed'
  | 'consuel_visit'
  | 'enedis_connection'
  | 'commissioning'

export interface Signature {
  id: string
  signer_name?: string
  ip_address?: string | null
  user_agent?: string
  signed_at: string
  signature_image?: string | null
  created_at: string
}

export interface TechnicalVisit {
  id: string
  visit_date: string
  expected_installation_date: string
  roof_type?: string | null
  tiles_spare_provided: boolean
  roof_shape?: string | null
  roof_access?: string | null
  roof_access_other?: string
  truck_access?: string
  truck_access_comment?: string
  nacelle_needed?: string
  meter_type?: string | null
  report_pdf?: string | null
  created_at: string
  current_type?: string | null
  existing_grid_connection?: boolean
  meter_position?: string
  meter_location_photo?: string | null
  panels_to_board_distance_m?: number | null
  additional_equipment_needed: boolean
  additional_equipment_details?: string
  is_validated: boolean
  validated_at?: string | null
  approval_statement?: string
  client_signature?: Signature | null
  installer_signature?: Signature | null
  created_at: string
  updated_at: string
}

export interface RepresentationMandate {
  id: string
  client_civility?: string | null
  client_birth_date?: string | null
  client_birth_place?: string
  client_address?: string
  company_name?: string
  company_rcs_city?: string
  company_siret?: string
  company_head_office_address?: string
  represented_by?: string
  representative_role?: string
  client_signature?: Signature | null
  installer_signature?: Signature | null
  mandate_pdf?: string | null
  created_at: string
  updated_at: string
}

export interface AdministrativeValidation {
  id: string
  is_validated: boolean
  validated_at?: string | null
  created_at: string
  updated_at: string
}

export interface InstallationCompleted {
  id: string
  modules_installed: boolean
  inverters_installed: boolean
  dc_ac_box_installed: boolean
  battery_installed: boolean
  photo_modules?: string | null
  photo_inverter?: string | null
  client_signature?: Signature | null
  installer_signature?: Signature | null
  created_at: string
  updated_at: string
}

export interface ConsuelVisit {
  id: string
  passed?: boolean | null
  refusal_reason?: string
  created_at: string
  updated_at: string
}

export interface EnedisConnection {
  id: string
  is_validated: boolean
  validated_at?: string | null
}

export interface Commissioning {
  id: string
  handover_receipt_given?: boolean | null
  updated_at: string
}

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
  client?: {
    id: string
    first_name: string
    last_name: string
    email: string
  } | null
  created_at: string
  updated_at: string
  technical_visit?: TechnicalVisit | null
  representation_mandate?: RepresentationMandate | null
  administrative_validation?: AdministrativeValidation | null
  installation_completed?: InstallationCompleted | null
  consuel_visit?: ConsuelVisit | null
  enedis_connection?: EnedisConnection | null
  commissioning?: Commissioning | null
  // Documents administratifs
  cerfa16702?: Cerfa16702 | null
  electrical_diagram?: ElectricalDiagram | null
  enedis_mandate?: EnedisMandate | null
  // Devis
  quote?: Quote | null
}

// ————————————————
// Documents administratifs
// ————————————————

export type DeclarantType = 'individual' | 'company'

export interface Cerfa16702 {
  id: string
  // Identité du déclarant
  declarant_type: DeclarantType
  last_name: string
  first_name: string
  birth_date?: string | null
  birth_place?: string
  birth_department?: string
  birth_country?: string
  company_denomination?: string
  company_reason?: string
  company_siret?: string
  company_type?: string

  // Coordonnées du déclarant
  address_street?: string
  address_number?: string
  address_lieu_dit?: string
  address_locality?: string
  address_postal_code?: string
  address_bp?: string
  address_cedex?: string
  phone_country_code?: string
  phone?: string
  email?: string
  email_consent?: boolean

  // Terrain
  land_street?: string
  land_number?: string
  land_lieu_dit?: string
  land_locality?: string
  land_postal_code?: string

  cadastral_prefix?: string
  cadastral_section?: string
  cadastral_number?: string
  cadastral_surface_m2?: number | null

  // Projet
  project_new_construction?: boolean
  project_existing_works?: boolean
  project_description?: string
  destination_primary_residence?: boolean
  destination_secondary_residence?: boolean
  agrivoltaic_project?: boolean
  electrical_power_text?: string
  peak_power_text?: string
  energy_destination?: string

  // Périmètres de protection
  protection_site_patrimonial?: boolean
  protection_site_classe_or_instance?: boolean
  protection_monument_abords?: boolean

  // Engagement du déclarant
  engagement_city?: string
  engagement_date?: string
  declarant_signature?: Signature | null

  // Pièces jointes
  dpc1?: string | null
  dpc2?: string | null
  dpc3?: string | null
  dpc4?: string | null
  dpc5?: string | null
  dpc6?: string | null
  dpc7?: string | null
  dpc8?: string | null
  dpc11?: string | null
  dpc11_notice_materiaux?: string

  // PDF généré
  pdf?: string | null

  created_at?: string
  updated_at?: string
}

export interface ElectricalDiagram {
  id: string
  file?: string | null
  created_at?: string
  updated_at?: string
}

export type ClientType = 'individual' | 'company' | 'collectivity'
export type Civility = 'mr' | 'mme'
export type MandateType = 'simple' | 'special'
export type ConnectionNature =
  | 'indiv_or_group_housing'
  | 'commercial_or_production'
  | 'branch_modification'
  | 'power_change_or_ev'

export interface EnedisMandate {
  id: string
  client_type: ClientType
  client_civility?: Civility | null

  // Adresse complète du client
  client_address_street?: string
  client_address_number?: string
  client_address_locality?: string
  client_address_postal_code?: string

  // Société / Collectivité
  client_company_name?: string
  client_company_siret?: string
  client_company_represented_by?: string

  // Entreprise en charge
  contractor_company_name?: string
  contractor_company_siret?: string
  contractor_represented_by_name?: string
  contractor_represented_by_role?: string

  // Mandat
  mandate_type: MandateType
  authorize_signature?: boolean
  authorize_payment?: boolean
  authorize_l342?: boolean
  authorize_network_access?: boolean

  // Localisation
  geographic_area?: string
  connection_nature?: ConnectionNature | null

  // Signatures
  client_signature?: Signature | null
  installer_signature?: Signature | null

  // PDF
  pdf?: string | null

  created_at?: string
  updated_at?: string
}
