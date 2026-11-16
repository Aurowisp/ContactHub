import { DeleteOutlined, EditOutlined, EyeOutlined, MailOutlined, PhoneOutlined } from '@ant-design/icons';
import { Avatar, Button, Empty, Popconfirm, Space, Table, Tag, Tooltip, Typography } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import type { Contact } from '../types/contact';
import FavoriteButton from './FavoriteButton';

export default function ContactTable({ contacts, total, page, pageSize, loading, favoriteLoading, onPage, onView, onEdit, onDelete, onFavorite }: {
  contacts: Contact[]; total: number; page: number; pageSize: number; loading: boolean; favoriteLoading?: number | null;
  onPage: (page: number, pageSize: number) => void; onView: (contact: Contact) => void; onEdit: (contact: Contact) => void;
  onDelete: (contact: Contact) => void; onFavorite: (contact: Contact) => void;
}) {
  const columns: ColumnsType<Contact> = [
    {
      title: 'Contact', key: 'contact', fixed: 'left', width: 230,
      render: (_, contact) => <div className="contact-cell"><Avatar>{contact.name.charAt(0).toUpperCase()}</Avatar><div><Typography.Text strong>{contact.name}</Typography.Text><span>{contact.category ? <Tag>{contact.category}</Tag> : 'Uncategorized'}</span></div></div>,
    },
    { title: 'Company', dataIndex: 'company', key: 'company', width: 180, render: (value: string | null) => value || <span className="muted">—</span> },
    { title: 'Primary phone', key: 'phone', width: 180, render: (_, contact) => { const method = contact.contact_methods.find((item) => item.type === 'phone'); return method ? <Space><PhoneOutlined className="muted" />{method.value}</Space> : <span className="muted">—</span>; } },
    { title: 'Primary email', key: 'email', width: 230, render: (_, contact) => { const method = contact.contact_methods.find((item) => item.type === 'email'); return method ? <Space><MailOutlined className="muted" />{method.value}</Space> : <span className="muted">—</span>; } },
    { title: '', key: 'favorite', width: 56, align: 'center', render: (_, contact) => <FavoriteButton active={contact.is_favorite} loading={favoriteLoading === contact.id} onClick={() => onFavorite(contact)} /> },
    {
      title: 'Actions', key: 'actions', width: 150, align: 'right',
      render: (_, contact) => <Space size={2}>
        <Tooltip title="View"><Button type="text" icon={<EyeOutlined />} onClick={() => onView(contact)} /></Tooltip>
        <Tooltip title="Edit"><Button type="text" icon={<EditOutlined />} onClick={() => onEdit(contact)} /></Tooltip>
        <Popconfirm title="Delete this contact?" description="This also removes every associated method." okText="Delete" okButtonProps={{ danger: true }} onConfirm={() => onDelete(contact)}><Tooltip title="Delete"><Button type="text" danger icon={<DeleteOutlined />} /></Tooltip></Popconfirm>
      </Space>,
    },
  ];
  return (
    <Table<Contact>
      rowKey="id" className="contacts-table" columns={columns} dataSource={contacts} loading={loading}
      scroll={{ x: 1050 }} locale={{ emptyText: <Empty description="No contacts match these filters" /> }}
      pagination={{ current: page, pageSize, total, showSizeChanger: true, pageSizeOptions: [10, 20, 50], showTotal: (count) => `${count} contacts`, onChange: onPage }}
      onRow={(contact) => ({ onDoubleClick: () => onView(contact) })}
    />
  );
}

