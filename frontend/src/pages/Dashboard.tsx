import { ContactsOutlined, MailOutlined, PhoneOutlined, PlusOutlined, StarOutlined } from '@ant-design/icons';
import { Alert, Avatar, Button, Card, Col, List, Row, Skeleton, Statistic } from 'antd';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchStats } from '../api/contacts';
import { getErrorMessage } from '../api/client';
import PageHeader from '../components/PageHeader';
import type { Stats } from '../types/contact';

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  useEffect(() => { fetchStats().then(setStats).catch((err) => setError(getErrorMessage(err))); }, []);
  const cards = stats ? [
    { label: 'Total contacts', value: stats.total_contacts, icon: <ContactsOutlined />, tone: 'blue', path: '/contacts' },
    { label: 'Favorites', value: stats.favorite_contacts, icon: <StarOutlined />, tone: 'gold', path: '/favorites' },
    { label: 'With phone', value: stats.contacts_with_phone, icon: <PhoneOutlined />, tone: 'green', path: '/contacts?has_phone=true' },
    { label: 'With email', value: stats.contacts_with_email, icon: <MailOutlined />, tone: 'purple', path: '/contacts?has_email=true' },
  ] : [];

  function openCard(path: string) {
    navigate(path);
  }
  return (
    <div className="page-container">
      <PageHeader eyebrow="Overview" title="Good to see you." description="A clear view of your address book and the people who matter." actions={<Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/contacts', { state: { create: true } })}>Add contact</Button>} />
      {error && <Alert type="error" showIcon message="Could not load dashboard" description={error} />}
      {!stats ? <Skeleton active /> : <>
        <Row gutter={[16, 16]}>{cards.map((item) => <Col xs={24} sm={12} xl={6} key={item.label}><Card className={`stat-card stat-card-link ${item.tone}`} role="link" tabIndex={0} aria-label={`View ${item.label.toLowerCase()}`} onClick={() => openCard(item.path)} onKeyDown={(event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); openCard(item.path); } }}><div className="stat-icon">{item.icon}</div><Statistic title={item.label} value={item.value} /></Card></Col>)}</Row>
        <Card className="recent-card" title="Recently added" extra={<Button type="link" onClick={() => navigate('/contacts')}>View all</Button>}>
          <List dataSource={stats.recently_added} locale={{ emptyText: 'Your recently added contacts will appear here.' }} renderItem={(contact) => <List.Item onClick={() => navigate('/contacts')} className="recent-item"><List.Item.Meta avatar={<Avatar>{contact.name.charAt(0).toUpperCase()}</Avatar>} title={contact.name} description={[contact.job_title, contact.company].filter(Boolean).join(' · ') || 'No organization details'} /></List.Item>} />
        </Card>
      </>}
    </div>
  );
}

