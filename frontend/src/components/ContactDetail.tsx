import { CopyOutlined, EnvironmentOutlined, ExportOutlined, GlobalOutlined, MailOutlined, PhoneOutlined, ShareAltOutlined, ToolOutlined } from '@ant-design/icons';
import { Avatar, Button, Descriptions, Divider, Drawer, Empty, Space, Tag, Tooltip, Typography, message } from 'antd';
import type { Contact, ContactMethodType } from '../types/contact';
import { copyContactValue, createEmailHref, createPhoneHref, normalizeWebsiteUrl } from '../utils/contactActions';

const icons: Record<ContactMethodType, React.ReactNode> = {
  phone: <PhoneOutlined />, email: <MailOutlined />, social: <ShareAltOutlined />,
  address: <EnvironmentOutlined />, website: <GlobalOutlined />, other: <ToolOutlined />,
};

export default function ContactDetail({ contact, open, onClose }: {
  contact?: Contact | null; open: boolean; onClose: () => void;
}) {
  const [messageApi, contextHolder] = message.useMessage();

  async function copyValue(value: string) {
    try {
      await copyContactValue(value);
      messageApi.success('Contact value copied');
    } catch {
      messageApi.error('Unable to copy contact value');
    }
  }

  return (
    <Drawer title="Contact details" width={480} open={open} onClose={onClose}>
      {contextHolder}
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
          {contact.contact_methods.length ? contact.contact_methods.map((method) => {
            const hasValue = Boolean(method.value.trim());
            const websiteUrl = method.type === 'website' && hasValue
              ? normalizeWebsiteUrl(method.value)
              : null;
            return (
              <div className="detail-method" key={method.id ?? `${method.type}-${method.label}-${method.value}`}>
                <div className="method-icon">{icons[method.type]}</div>
                <div className="method-content"><span>{method.label}</span><strong>{method.value}</strong></div>
                {hasValue && <Space className="method-actions" size={4} wrap>
                  <Tooltip title="Copy"><Button type="text" icon={<CopyOutlined />} aria-label={`Copy ${method.label}`} onClick={() => void copyValue(method.value)} /></Tooltip>
                  {method.type === 'phone' && <Tooltip title="Call"><Button type="text" icon={<PhoneOutlined />} href={createPhoneHref(method.value)} aria-label={`Call ${method.label}`} /></Tooltip>}
                  {method.type === 'email' && <Tooltip title="Email"><Button type="text" icon={<MailOutlined />} href={createEmailHref(method.value)} aria-label={`Email ${method.label}`} /></Tooltip>}
                  {method.type === 'website' && websiteUrl && <Tooltip title="Open website"><Button type="text" icon={<ExportOutlined />} href={websiteUrl} target="_blank" rel="noopener noreferrer" aria-label={`Open ${method.label}`} /></Tooltip>}
                  {method.type === 'website' && !websiteUrl && <Tooltip title="Invalid or unsafe website address"><Button type="text" danger icon={<ExportOutlined />} aria-label={`Open ${method.label}`} onClick={() => messageApi.error('Website address is invalid or unsafe')} /></Tooltip>}
                </Space>}
              </div>
            );
          }) : <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="No contact methods" />}
        </>
      ) : null}
    </Drawer>
  );
}

