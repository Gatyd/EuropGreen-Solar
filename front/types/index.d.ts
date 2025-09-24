import type { InstallationStatus } from './installations'

export type UserRoles = "employee" | "installer" | "secretary" | "regional_manager" | "customer" | "admin";

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

export interface User{
    id: string;
	first_name: string;
	last_name: string;
	email: string;
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