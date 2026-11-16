import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fetchStats } from '../api/contacts';
import Dashboard from './Dashboard';

vi.mock('../api/contacts', () => ({ fetchStats: vi.fn() }));

const mockedFetchStats = vi.mocked(fetchStats);

function LocationProbe() {
  const location = useLocation();
  return <div data-testid="location">{location.pathname}{location.search}</div>;
}

function renderDashboard() {
  return render(
    <MemoryRouter initialEntries={['/']}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="*" element={<LocationProbe />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe('Dashboard statistic navigation', () => {
  beforeEach(() => {
    mockedFetchStats.mockResolvedValue({
      total_contacts: 8,
      favorite_contacts: 3,
      contacts_with_phone: 5,
      contacts_with_email: 4,
      recently_added: [],
    });
  });

  it.each([
    ['View total contacts', '/contacts'],
    ['View favorites', '/favorites'],
  ])('navigates from %s by click', async (accessibleName, expectedPath) => {
    const user = userEvent.setup();
    renderDashboard();
    await user.click(await screen.findByRole('link', { name: accessibleName }));
    expect(screen.getByTestId('location')).toHaveTextContent(expectedPath);
  });

  it('supports Enter for the phone filter card', async () => {
    const user = userEvent.setup();
    renderDashboard();
    const card = await screen.findByRole('link', { name: 'View with phone' });
    card.focus();
    await user.keyboard('{Enter}');
    expect(screen.getByTestId('location')).toHaveTextContent('/contacts?has_phone=true');
  });

  it('supports Space for the email filter card', async () => {
    const user = userEvent.setup();
    renderDashboard();
    const card = await screen.findByRole('link', { name: 'View with email' });
    card.focus();
    await user.keyboard(' ');
    expect(screen.getByTestId('location')).toHaveTextContent('/contacts?has_email=true');
  });
});
