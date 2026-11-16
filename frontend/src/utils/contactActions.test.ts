import { describe, expect, it, vi } from 'vitest';
import {
  copyContactValue,
  createEmailHref,
  createPhoneHref,
  normalizeWebsiteUrl,
} from './contactActions';

describe('contact action helpers', () => {
  it('normalizes safe websites and supplies https by default', () => {
    expect(normalizeWebsiteUrl('example.com/profile')).toBe('https://example.com/profile');
    expect(normalizeWebsiteUrl('http://example.com')).toBe('http://example.com/');
    expect(normalizeWebsiteUrl(' HTTPS://Example.com/path ')).toBe('https://example.com/path');
  });

  it('rejects dangerous and invalid website protocols', () => {
    expect(normalizeWebsiteUrl('javascript:alert(1)')).toBeNull();
    expect(normalizeWebsiteUrl('data:text/html,test')).toBeNull();
    expect(normalizeWebsiteUrl('mailto:test@example.com')).toBeNull();
    expect(normalizeWebsiteUrl('https://')).toBeNull();
    expect(normalizeWebsiteUrl('   ')).toBeNull();
  });

  it('creates encoded phone and email protocol links', () => {
    expect(createPhoneHref(' +86 138 0000 0000 ')).toBe('tel:+86%20138%200000%200000');
    expect(createEmailHref('user+tag@example.com')).toBe('mailto:user%2Btag%40example.com');
  });

  it('copies the exact value through the Clipboard API', async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: { writeText },
    });
    await copyContactValue('user123');
    expect(writeText).toHaveBeenCalledWith('user123');
  });

  it('reports empty values and unavailable Clipboard API', async () => {
    await expect(copyContactValue('   ')).rejects.toThrow('no contact value');
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: undefined,
    });
    await expect(copyContactValue('user123')).rejects.toThrow('Clipboard access is not available');
  });
});
