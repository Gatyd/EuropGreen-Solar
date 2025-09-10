
export type ProductType = "panel" | "inverter" | "battery" | "structure" | "service" | "other";

export interface Product {
    id: string;
    name: string;
    type: ProductType;
    description: string;
    unit_price: string; // Decimal as string
    cost_price: string; // Decimal as string
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export type QuoteStatus = "draft" | "sent" | "accepted" | "declined" | "pending";

export interface QuoteLine {
    id: string;
    product_type: ProductType;
    name: string;
    description: string;
    unit_price: string; // Decimal as string
    cost_price: string; // Decimal as string
    quantity: string; // Decimal as string
    discount_rate: string; // Decimal as string (%) 
    line_total: string; // Decimal as string
    position: number;
    created_at: string;
    updated_at: string;
}

export interface QuoteSignature {
    signer_name?: string;
    signer_email?: string;
    ip_address?: string | null;
    user_agent?: string;
    signed_at: string;
    signature_image?: string | null; // URL
    signature_data?: string; // base64 or JSON
}

export interface QuotePDF {
    id: string;
    number: string;
    pdf?: string | null; // URL du PDF
}

export interface Quote {
    id: string;
    number: string;
    offer: string; // UUID
    version: number;
    predecessor?: string | null; // UUID
    status: QuoteStatus;
    title?: string;
    negociations?: string;
    notes?: string;
    currency: string; // e.g. EUR
    valid_until?: string | null; // date
    subtotal: string; // Decimal as string
    discount_amount: string; // Decimal as string
    tax_rate: string; // Decimal as string (%)
    total: string; // Decimal as string
    pdf?: string | null; // URL du PDF
    created_by?: string | null;
    updated_by?: string | null;
    created_at: string;
    updated_at: string;
    lines: QuoteLine[];
    signature?: QuoteSignature | null;
}

export type InvoiceStatus = "draft" | "issued" | "partially_paid" | "paid" | "cancelled";

export interface Invoice {
    id: string;
    number: string;
    installation: string; // UUID
    quote?: string | null; // UUID
    title?: string;
    notes?: string;
    currency: string; // e.g. EUR
    issue_date: string; // date
    due_date?: string | null; // date
    subtotal: string; // Decimal as string
    discount_amount: string; // Decimal as string
    tax_rate: string; // Decimal as string (%)
    total: string; // Decimal as string
    amount_paid?: string; // Decimal as string
    balance_due?: string; // Decimal as string
    pdf?: string | null; // URL du PDF
    status: InvoiceStatus;
    created_by?: string | null;
    updated_by?: string | null;
    created_at: string;
    updated_at: string;
    lines: QuoteLine[];
    installments?: Installment[];
    payments?: Payment[];
}

export type InstallmentType = "deposit" | "balance" | "milestone";

export interface Installment {
    id: string;
    invoice: string; // UUID
    type: InstallmentType;
    label: string;
    due_date?: string | null; // date
    percentage?: string | null; // Decimal as string (%)
    amount?: string | null; // Decimal as string (EUR)
    is_paid: boolean;
    position: number;
    created_at: string;
    updated_at: string;
}

export interface Payment {
    id: string;
    invoice: string; // UUID
    installment?: string | null; // UUID
    date: string; // date
    method?: string; // virement, CB, cheque, etc
    reference?: string;
    amount: string; // Decimal as string
    notes?: string;
    created_by?: string | null;
    created_at: string;
}
