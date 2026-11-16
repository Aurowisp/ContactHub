import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import type { Contact } from '../types/contact';
import ContactDetail from './ContactDetail';

const contact: Contact = {
  id: 1,
  name: 'Action Contact',
  company: 'ContactHub',
  job_title: 'Tester',
  category: 'Work',
  notes: 'Shortcut verification',
  is_favorite: true,
  created_at: '2026-11-16T00:00:00Z',
  updated_at: '2026-11-16T00:00:00Z',
  contact_methods: [
    { id: 1, type: 'phone', label: 'Mobile', value: '+86 13800000000' },
    { id: 2, type: 'email', label: 'Work', value: 'abc+tag@example.com' },
    { id: 3, type: 'website', label: 'Portfolio', value: 'example.com/profile' },
    { id: 4, type: 'social', label: 'WeChat', value: 'user123' },
    { id: 5, type: 'address', label: 'Home', value: 'Fuzhou, China' },
    { id: 6, type: 'other', label: 'Other', value: 'custom-value' },
    { id: 7, type: 'website', label: 'Unsafe', value: 'javascript:alert(1)' },
    { id: 8, type: 'other', label: 'Empty', value: '' },
  ],
};

describe('ContactDetail quick actions', () => {
  it('renders phone, email, safe website links and blocks dangerous websites', async () => {
    const user = userEvent.setup();
    render(<ContactDetail contact={contact} open onClose={() => undefined} />);
    expect(screen.getByRole('link', { name: 'Call Mobile' })).toHaveAttribute(
      'href', 'tel:+86%2013800000000',
    );
    expect(screen.getByRole('link', { name: 'Email Work' })).toHaveAttribute(
      'href', 'mailto:abc%2Btag%40example.com',
    );
    expect(screen.getByRole('link', { name: 'Open Portfolio' })).toHaveAttribute(
      'href', 'https://example.com/profile',
    );
    expect(screen.getByRole('link', { name: 'Open Portfolio' })).toHaveAttribute(
      'rel', 'noopener noreferrer',
    );
    expect(screen.queryByRole('link', { name: 'Open Unsafe' })).not.toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: 'Open Unsafe' }));
    expect(await screen.findByText('Website address is invalid or unsafe')).toBeVisible();
    expect(screen.queryByRole('button', { name: 'Copy Empty' })).not.toBeInTheDocument();
  });

  it.each([
    ['Mobile', '+86 13800000000'],
    ['Work', 'abc+tag@example.com'],
    ['Portfolio', 'example.com/profile'],
    ['WeChat', 'user123'],
    ['Home', 'Fuzhou, China'],
    ['Other', 'custom-value'],
  ])('copies the exact %s value', async (label, value) => {
    const user = userEvent.setup();
    const writeText = vi.spyOn(navigator.clipboard, 'writeText').mockResolvedValue(undefined);
    render(<ContactDetail contact={contact} open onClose={() => undefined} />);
    await user.click(screen.getByRole('button', { name: `Copy ${label}` }));
    expect(writeText).toHaveBeenCalledWith(value);
    expect(await screen.findByText('Contact value copied')).toBeVisible();
  });

  it('shows an error when Clipboard API rejects the copy', async () => {
    const user = userEvent.setup();
    vi.spyOn(navigator.clipboard, 'writeText').mockRejectedValueOnce(
      new Error('Permission denied'),
    );
    render(<ContactDetail contact={contact} open onClose={() => undefined} />);
    await user.click(screen.getByRole('button', { name: 'Copy Home' }));
    expect(await screen.findByText('Unable to copy contact value')).toBeVisible();
  });

  it('shows an error when Clipboard API is unavailable', async () => {
    const user = userEvent.setup();
    Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: undefined,
    });
    render(<ContactDetail contact={contact} open onClose={() => undefined} />);
    await user.click(screen.getByRole('button', { name: 'Copy WeChat' }));
    expect(await screen.findByText('Unable to copy contact value')).toBeVisible();
  });
});
