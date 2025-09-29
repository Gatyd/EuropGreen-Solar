import type { InstallationStatus } from './installations'

// Aligné avec le backend: quatre rôles natifs
export type UserRoles = "admin" | "customer" | "collaborator" | "sales";

export interface Item {
    value: string;
    label: string;
}

export interface LoginResponse {
	success: boolean;
	message: string;
}

export interface UserAccess {
    installation: boolean,
    offers: boolean,
    requests: boolean,
    administrative_procedures: boolean
}

// Nouveau modèle Role (dynamique) non encore lié directement à User
export interface Role {
    id: string;
    name: string;
    installation: boolean;
    offers: boolean;
    requests: boolean;
    administrative_procedures: boolean;
    created_at: string;
    updated_at: string;
}

export interface User{
    id: string;
	first_name: string;
	last_name: string;
	email: string;
    phone_number?: string;
    role: UserRoles;
	accept_invitation: boolean;
	is_active: boolean;
    is_staff: boolean;
    is_superuser: boolean;
	useraccess?: UserAccess;
    // Champs calculés (clients uniquement)
    installations_count?: number;
    last_installation?: { id: string; status: InstallationStatus; installer?: { id: string; first_name: string; last_name: string } } | null;
}