import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fetchContacts } from '../api/contacts';
import Contacts from './Contacts';

vi.mock('../api/contacts', () => ({
  fetchContacts: vi.fn(),
  createContact: vi.fn(),
  updateContact: vi.fn(),
  deleteContact: vi.fn(),
  updateFavorite: vi.fn(),
}));

vi.mock('../components/ContactTable', () => ({
  default: () => <div data-testid="contact-table">Contact table</div>,
}));
vi.mock('../components/ContactForm', () => ({ default: () => null }));
vi.mock('../components/ContactDetail', () => ({ default: () => null }));

const mockedFetchContacts = vi.mocked(fetchContacts);

function renderContacts(url = '/contacts') {
  return render(
    <MemoryRouter initialEntries={[url]}>
      <Routes><Route path="/contacts" element={<Contacts />} /></Routes>
    </MemoryRouter>,
  );
}

describe('Contacts search and method URL filters', () => {
  beforeEach(() => {
    mockedFetchContacts.mockReset();
    mockedFetchContacts.mockResolvedValue({ items: [], total: 0, skip: 0, limit: 10 });
  });

  it('reads has_phone from the URL and keeps it in API requests', async () => {
    renderContacts('/contacts?has_phone=true');
    expect(await screen.findByText('With phone')).toBeVisible();
    await waitFor(() => expect(mockedFetchContacts).toHaveBeenCalledWith(
      expect.objectContaining({ has_phone: true, has_email: undefined }),
    ));
  });

  it('reads explicit false email filters and can clear method filters', async () => {
    const user = userEvent.setup();
    renderContacts('/contacts?has_email=false');
    expect(await screen.findByText('Without email')).toBeVisible();
    await user.click(screen.getByRole('button', { name: 'Clear method filters' }));
    await waitFor(() => expect(mockedFetchContacts).toHaveBeenLastCalledWith(
      expect.objectContaining({ has_phone: undefined, has_email: undefined }),
    ));
    expect(screen.queryByText('Without email')).not.toBeInTheDocument();
  });

  it('ignores invalid boolean URL filter values', async () => {
    renderContacts('/contacts?has_phone=invalid');
    await waitFor(() => expect(mockedFetchContacts).toHaveBeenCalledWith(
      expect.objectContaining({ has_phone: undefined }),
    ));
    expect(screen.queryByLabelText('Active contact method filters')).not.toBeInTheDocument();
  });

  it('submits enhanced search text and resets it when cleared', async () => {
    const user = userEvent.setup();
    renderContacts();
    const search = screen.getByPlaceholderText(
      'Search names, companies, roles, notes, labels, or contact details',
    );
    await user.type(search, 'Robotics{Enter}');
    await waitFor(() => expect(mockedFetchContacts).toHaveBeenLastCalledWith(
      expect.objectContaining({ keyword: 'Robotics', skip: 0 }),
    ));
    await user.clear(search);
    await waitFor(() => expect(mockedFetchContacts).toHaveBeenLastCalledWith(
      expect.objectContaining({ keyword: undefined }),
    ));
  });
});
