export async function copyContactValue(value: string): Promise<void> {
  if (!value.trim()) {
    throw new Error('There is no contact value to copy');
  }
  if (!navigator.clipboard?.writeText) {
    throw new Error('Clipboard access is not available');
  }
  await navigator.clipboard.writeText(value);
}

export function normalizeWebsiteUrl(value: string): string | null {
  const trimmed = value.trim();
  if (!trimmed) return null;

  const candidate = /^[a-zA-Z][a-zA-Z\d+.-]*:/.test(trimmed)
    ? trimmed
    : `https://${trimmed}`;
  try {
    const url = new URL(candidate);
    if (!['http:', 'https:'].includes(url.protocol) || !url.hostname) return null;
    return url.toString();
  } catch {
    return null;
  }
}

export function createPhoneHref(value: string): string {
  return `tel:${encodeURI(value.trim())}`;
}

export function createEmailHref(value: string): string {
  return `mailto:${encodeURIComponent(value.trim())}`;
}
