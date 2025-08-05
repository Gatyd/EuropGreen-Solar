
export type UserRoles = "employee" | "installer" | "secretary" | "customer" | "admin";

export interface LoginResponse {
	success: boolean;
	message: string;
}

export interface User{
    id: string;
	first_name: string;
	last_name: string;
	email: string;
    role: UserRoles;
    is_staff: boolean;
    is_superuser: boolean;
}