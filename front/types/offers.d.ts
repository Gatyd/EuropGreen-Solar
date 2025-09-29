export type OfferStatus =
	| 'to_contact'
	| 'phone_meeting'
	| 'meeting'
	| 'quote_sent'
	| 'negotiation'
	| 'quote_signed'

export interface Offer {
	id: string
	request: string
	last_name: string
	first_name: string
	email: string
	phone: string
	address: string
	housing_type?: string
	project_details?: string
	notes?: Array<{ date: string; note: string }>
	status: OfferStatus
	created_at: string
	updated_at: string
	last_quote?: import('./billing').Quote | null
}
