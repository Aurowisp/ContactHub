import apiClient from './client';
import type { Contact, ContactInput, ContactListResponse, ContactQuery, Stats } from '../types/contact';

export async function fetchContacts(query: ContactQuery = {}): Promise<ContactListResponse> {
  const { data } = await apiClient.get<ContactListResponse>('/contacts', { params: query });
  return data;
}

export async function fetchContact(id: number): Promise<Contact> {
  const { data } = await apiClient.get<Contact>(`/contacts/${id}`);
  return data;
}

export async function createContact(input: ContactInput): Promise<Contact> {
  const { data } = await apiClient.post<Contact>('/contacts', input);
  return data;
}

export async function updateContact(id: number, input: ContactInput): Promise<Contact> {
  const { data } = await apiClient.put<Contact>(`/contacts/${id}`, input);
  return data;
}

export async function deleteContact(id: number): Promise<void> {
  await apiClient.delete(`/contacts/${id}`);
}

export async function updateFavorite(id: number, isFavorite: boolean): Promise<Contact> {
  const { data } = await apiClient.patch<Contact>(`/contacts/${id}/favorite`, {
    is_favorite: isFavorite,
  });
  return data;
}

export async function fetchStats(): Promise<Stats> {
  const { data } = await apiClient.get<Stats>('/stats');
  return data;
}

