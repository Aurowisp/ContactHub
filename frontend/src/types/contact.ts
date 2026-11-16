export type ContactMethodType = 'phone' | 'email' | 'social' | 'address' | 'website' | 'other';

export interface ContactMethod {
  id?: number;
  type: ContactMethodType;
  label: string;
  value: string;
}

export interface ContactInput {
  name: string;
  company?: string | null;
  job_title?: string | null;
  category?: string | null;
  notes?: string | null;
  is_favorite: boolean;
  contact_methods: ContactMethod[];
}

export interface Contact extends ContactInput {
  id: number;
  created_at: string;
  updated_at: string;
}

export interface ContactListResponse {
  items: Contact[];
  total: number;
  skip: number;
  limit: number;
}

export interface ContactQuery {
  keyword?: string;
  favorite?: boolean;
  category?: string;
  has_phone?: boolean;
  has_email?: boolean;
  skip?: number;
  limit?: number;
}

export interface Stats {
  total_contacts: number;
  favorite_contacts: number;
  contacts_with_phone: number;
  contacts_with_email: number;
  recently_added: Contact[];
}

export interface ImportResult {
  total: number;
  success: number;
  skipped: number;
  errors: { row: number; reason: string }[];
}

