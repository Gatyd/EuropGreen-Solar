
export type UserRoles = "employee" | "installer" | "secretary" | "customer" | "admin";

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
}