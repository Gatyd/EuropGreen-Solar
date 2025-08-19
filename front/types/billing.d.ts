
export type ProductType = "panel" | "inverter" | "battery" | "structure" | "service" | "other"; 

export interface Product {
    id: string;
    name: string;
    type: ProductType;
    description: string;
    unit_price: string;
    cost_price: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}
