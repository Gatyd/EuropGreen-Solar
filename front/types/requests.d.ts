export type ProspectStatus = "new" | "followup" | "info" | "in_progress" | "closed";

export type ProspectSource = "call_center" | "web_form";

export interface ProspectRequest {
  id: string;
  last_name: string;
  first_name: string;
  email: string;
  phone: string;
  address: string;
  housing_type?: string;
  electricity_bill?: string; // URL du fichier
  status: ProspectStatus;
  source: ProspectSource;
  appointment_date?: string;
  assigned_to?: {
    id: string;
    first_name: string;
    last_name: string;
    email: string;
    role: string;
  } | null;
  created_by?: {
    id: string;
    first_name: string;
    last_name: string;
    email: string;
    role: string;
  } | null;
//   notes?: string;
  created_at: string;
  updated_at: string;
}

export interface ProspectRequestPayload {
  last_name: string;
  first_name: string;
  email: string;
  phone: string;
  address: string;
  housing_type?: string;
  electricity_bill?: File | null;
  status?: ProspectStatus;
  source: ProspectSource;
  appointment_date?: string | null;
  assigned_to_id?: string;
//   notes?: string;
}
