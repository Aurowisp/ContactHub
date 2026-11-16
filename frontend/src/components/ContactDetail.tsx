import { EnvironmentOutlined, GlobalOutlined, MailOutlined, PhoneOutlined, ShareAltOutlined, ToolOutlined } from '@ant-design/icons';
import { Avatar, Descriptions, Divider, Drawer, Empty, Space, Tag, Typography } from 'antd';
import type { Contact, ContactMethodType } from '../types/contact';

const icons: Record<ContactMethodType, React.ReactNode> = {
  phone: <PhoneOutlined />, email: <MailOutlined />, social: <ShareAltOutlined />,
  address: <EnvironmentOutlined />, website: <GlobalOutlined />, other: <ToolOutlined />,
};

export default function ContactDetail({ contact, open, onClose }: {
  contact?: Contact | null; open: boolean; onClose: () => void;
}) {
  return (
    <Drawer title="Contact details" width={480} open={open} onClose={onClose}>
      {contact ? (
        <>
          <div className="detail-profile">
            <Avatar size={64}>{contact.name.charAt(0).toUpperCase()}</Avatar>
            <div><Typography.Title level={3}>{contact.name}</Typography.Title><Typography.Text type="secondary">{contact.job_title || 'No job title'}{contact.company ? ` · ${contact.company}` : ''}</Typography.Text></div>
          </div>
          <Space wrap>{contact.is_favorite && <Tag color="gold">Favorite</Tag>}{contact.category && <Tag color="blue">{contact.category}</Tag>}</Space>
          <Divider />
          <Descriptions column={1} size="small">
            <Descriptions.Item label="Company">{contact.company || '—'}</Descriptions.Item>
            <Descriptions.Item label="Job title">{contact.job_title || '—'}</Descriptions.Item>
            <Descriptions.Item label="Notes">{contact.notes || '—'}</Descriptions.Item>
          </Descriptions>
          <Divider orientation="left">Contact methods</Divider>
          {contact.contact_methods.length ? contact.contact_methods.map((method) => (
            <div className="detail-method" key={method.id ?? `${method.type}-${method.label}-${method.value}`}>
              <div className="method-icon">{icons[method.type]}</div>
              <div><span>{method.label}</span><strong>{method.value}</strong></div>
            </div>
          )) : <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="No contact methods" />}
        </>
      ) : null}
    </Drawer>
  );
}

