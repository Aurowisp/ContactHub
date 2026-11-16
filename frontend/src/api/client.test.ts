import { describe, expect, it } from 'vitest';
import { resolveApiBaseUrl } from './client';

describe('resolveApiBaseUrl', () => {
  it('keeps same-origin local development when no value is configured', () => {
    expect(resolveApiBaseUrl()).toBe('/api/v1');
    expect(resolveApiBaseUrl('   ')).toBe('/api/v1');
  });

  it('adds the API prefix to a Render backend origin', () => {
    expect(resolveApiBaseUrl('https://contacthub-api.onrender.com')).toBe(
      'https://contacthub-api.onrender.com/api/v1',
    );
  });

  it('does not duplicate the prefix and removes trailing slashes', () => {
    expect(resolveApiBaseUrl('https://api.example.com/api/v1/')).toBe(
      'https://api.example.com/api/v1',
    );
  });
});
