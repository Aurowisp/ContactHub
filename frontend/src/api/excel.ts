import apiClient from './client';
import type { ImportResult } from '../types/contact';

function saveBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export async function exportContacts(): Promise<void> {
  const response = await apiClient.get<Blob>('/contacts/export', { responseType: 'blob' });
  const date = new Date().toISOString().slice(0, 10);
  saveBlob(response.data, `contacthub_export_${date}.xlsx`);
}

export async function downloadTemplate(): Promise<void> {
  const response = await apiClient.get<Blob>('/contacts/import-template', { responseType: 'blob' });
  saveBlob(response.data, 'contacts_template.xlsx');
}

export async function importContacts(file: File, onProgress?: (percent: number) => void): Promise<ImportResult> {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await apiClient.post<ImportResult>('/contacts/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (event) => {
      if (event.total && onProgress) onProgress(Math.round((event.loaded * 100) / event.total));
    },
  });
  return data;
}

