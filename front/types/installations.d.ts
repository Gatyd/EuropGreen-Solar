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
  meter_type_other?: string
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
}
