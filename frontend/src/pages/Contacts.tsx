import { FilterOutlined, PlusOutlined, SearchOutlined } from '@ant-design/icons';
import { Alert, Button, Card, Input, Select, Space, Tag, message } from 'antd';
import { useCallback, useEffect, useState } from 'react';
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import { createContact, deleteContact, fetchContacts, updateContact, updateFavorite } from '../api/contacts';
import { getErrorMessage } from '../api/client';
import ContactDetail from '../components/ContactDetail';
import ContactForm from '../components/ContactForm';
import ContactTable from '../components/ContactTable';
import PageHeader from '../components/PageHeader';
import type { Contact, ContactInput } from '../types/contact';

function readOptionalBoolean(params: URLSearchParams, key: string): boolean | undefined {
  const value = params.get(key);
  if (value === 'true') return true;
  if (value === 'false') return false;
  return undefined;
}

export default function Contacts({ favoritesOnly = false }: { favoritesOnly?: boolean }) {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [keyword, setKeyword] = useState('');
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState<string | undefined>();
  const [favoriteFilter, setFavoriteFilter] = useState<boolean | undefined>(favoritesOnly ? true : undefined);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<Contact | null>(null);
  const [detail, setDetail] = useState<Contact | null>(null);
  const [saving, setSaving] = useState(false);
  const [favoriteLoading, setFavoriteLoading] = useState<number | null>(null);
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [messageApi, contextHolder] = message.useMessage();
  const hasPhone = readOptionalBoolean(searchParams, 'has_phone');
  const hasEmail = readOptionalBoolean(searchParams, 'has_email');

  const load = useCallback(async () => {
    setLoading(true); setError('');
    try {
      const result = await fetchContacts({ keyword: search || undefined, category, favorite: favoritesOnly ? true : favoriteFilter, has_phone: hasPhone, has_email: hasEmail, skip: (page - 1) * pageSize, limit: pageSize });
      setContacts(result.items); setTotal(result.total);
    } catch (err) { setError(getErrorMessage(err)); } finally { setLoading(false); }
  }, [category, favoriteFilter, favoritesOnly, hasEmail, hasPhone, page, pageSize, search]);

  useEffect(() => { void load(); }, [load]);
  useEffect(() => { setPage(1); }, [hasEmail, hasPhone]);
  useEffect(() => {
    if ((location.state as { create?: boolean } | null)?.create) {
      setEditing(null); setFormOpen(true); navigate(location.pathname, { replace: true, state: null });
    }
  }, [location, navigate]);

  async function save(input: ContactInput) {
    setSaving(true);
    try {
      if (editing) await updateContact(editing.id, input); else await createContact(input);
      messageApi.success(editing ? 'Contact updated' : 'Contact created');
      setFormOpen(false); setEditing(null); await load();
    } catch (err) { messageApi.error(getErrorMessage(err)); } finally { setSaving(false); }
  }
  async function remove(contact: Contact) {
    try { await deleteContact(contact.id); messageApi.success(`${contact.name} deleted`); if (contacts.length === 1 && page > 1) setPage(page - 1); else await load(); }
    catch (err) { messageApi.error(getErrorMessage(err)); }
  }
  async function toggleFavorite(contact: Contact) {
    setFavoriteLoading(contact.id);
    try { await updateFavorite(contact.id, !contact.is_favorite); messageApi.success(contact.is_favorite ? 'Removed from favorites' : 'Added to favorites'); await load(); }
    catch (err) { messageApi.error(getErrorMessage(err)); } finally { setFavoriteLoading(null); }
  }

  function clearMethodFilters() {
    const next = new URLSearchParams(searchParams);
    next.delete('has_phone');
    next.delete('has_email');
    setSearchParams(next, { replace: true });
  }

  return (
    <div className="page-container">
      {contextHolder}
      <PageHeader eyebrow={favoritesOnly ? 'Bookmarked' : 'Directory'} title={favoritesOnly ? 'Favorite contacts' : 'All contacts'} description={favoritesOnly ? 'The people you want to keep close at hand.' : 'Search, organize, and keep every way to connect in one place.'} actions={<Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); setFormOpen(true); }}>Add contact</Button>} />
      {error && <Alert type="error" showIcon closable message="Could not load contacts" description={error} />}
      {(hasPhone !== undefined || hasEmail !== undefined) && <div className="active-filters" aria-label="Active contact method filters">
        <span>Active filters:</span>
        {hasPhone !== undefined && <Tag color="blue">{hasPhone ? 'With phone' : 'Without phone'}</Tag>}
        {hasEmail !== undefined && <Tag color="purple">{hasEmail ? 'With email' : 'Without email'}</Tag>}
        <Button type="link" size="small" onClick={clearMethodFilters}>Clear method filters</Button>
      </div>}
      <Card className="table-card">
        <div className="filters">
          <Input.Search prefix={<SearchOutlined />} placeholder="Search names, companies, roles, notes, labels, or contact details" value={keyword} onChange={(e) => { setKeyword(e.target.value); if (!e.target.value) { setPage(1); setSearch(''); } }} onSearch={(value) => { setPage(1); setSearch(value.trim()); }} allowClear className="search-input" />
          <Space wrap>
            <Select allowClear placeholder="Category" suffixIcon={<FilterOutlined />} value={category} onChange={(value) => { setCategory(value); setPage(1); }} options={['Work', 'Family', 'Friends', 'Other'].map((value) => ({ value }))} />
            {!favoritesOnly && <Select allowClear placeholder="Favorite status" value={favoriteFilter} onChange={(value) => { setFavoriteFilter(value); setPage(1); }} options={[{ value: true, label: 'Favorites only' }, { value: false, label: 'Not favorites' }]} />}
          </Space>
        </div>
        <ContactTable contacts={contacts} total={total} page={page} pageSize={pageSize} loading={loading} favoriteLoading={favoriteLoading} onPage={(nextPage, nextSize) => { setPage(nextPage); setPageSize(nextSize); }} onView={setDetail} onEdit={(contact) => { setEditing(contact); setFormOpen(true); }} onDelete={remove} onFavorite={toggleFavorite} />
      </Card>
      <ContactForm open={formOpen} contact={editing} saving={saving} onCancel={() => { setFormOpen(false); setEditing(null); }} onSave={save} />
      <ContactDetail contact={detail} open={Boolean(detail)} onClose={() => setDetail(null)} />
    </div>
  );
}

