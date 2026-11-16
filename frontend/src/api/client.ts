import axios from 'axios';

export function resolveApiBaseUrl(configuredOrigin?: string): string {
  const configured = configuredOrigin?.trim().replace(/\/+$/, '');
  if (!configured) return '/api/v1';
  return configured.endsWith('/api/v1') ? configured : `${configured}/api/v1`;
}

const apiClient = axios.create({
  baseURL: resolveApiBaseUrl(import.meta.env.VITE_API_BASE_URL),
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) return detail.map((item) => item.msg).join(', ');
    return error.message;
  }
  return error instanceof Error ? error.message : 'An unexpected error occurred';
}

export default apiClient;

