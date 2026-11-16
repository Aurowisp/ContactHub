import { MinusCircleOutlined, PlusOutlined } from '@ant-design/icons';
import { Button, Checkbox, Col, Form, Input, Modal, Row, Select, Tabs } from 'antd';
import { useEffect } from 'react';
import type { Contact, ContactInput, ContactMethodType } from '../types/contact';

const methodGroups: { type: ContactMethodType; label: string; defaultLabel: string }[] = [
  { type: 'phone', label: 'Phone numbers', defaultLabel: 'Mobile' },
  { type: 'email', label: 'Email addresses', defaultLabel: 'Work' },
  { type: 'social', label: 'Social accounts', defaultLabel: 'WeChat' },
  { type: 'address', label: 'Addresses', defaultLabel: 'Home' },
  { type: 'website', label: 'Websites', defaultLabel: 'Portfolio' },
  { type: 'other', label: 'Other methods', defaultLabel: 'Other' },
];

type FormValues = Omit<ContactInput, 'contact_methods'> & Record<ContactMethodType, { id?: number; label: string; value: string }[]>;

export default function ContactForm({ open, contact, saving, onCancel, onSave }: {
  open: boolean; contact?: Contact | null; saving: boolean;
  onCancel: () => void; onSave: (input: ContactInput) => Promise<void>;
}) {
  const [form] = Form.useForm<FormValues>();

  useEffect(() => {
    if (!open) return;
    const grouped = Object.fromEntries(methodGroups.map(({ type }) => [
      type,
      (contact?.contact_methods ?? []).filter((method) => method.type === type).map(({ id, label, value }) => ({ id, label, value })),
    ]));
    form.setFieldsValue({
      name: contact?.name ?? '', company: contact?.company ?? '', job_title: contact?.job_title ?? '',
      category: contact?.category ?? '', notes: contact?.notes ?? '', is_favorite: contact?.is_favorite ?? false,
      ...grouped,
    } as FormValues);
  }, [contact, form, open]);

  async function submit() {
    const values = await form.validateFields();
    const methods = methodGroups.flatMap(({ type }) =>
      (values[type] ?? []).map((method) => ({ ...method, type }))
    );
    await onSave({
      name: values.name.trim(), company: values.company?.trim() || null,
      job_title: values.job_title?.trim() || null, category: values.category?.trim() || null,
      notes: values.notes?.trim() || null, is_favorite: values.is_favorite ?? false,
      contact_methods: methods,
    });
  }

  return (
    <Modal
      title={contact ? 'Edit contact' : 'Create a new contact'} open={open} onCancel={onCancel}
      onOk={submit} confirmLoading={saving} okText={contact ? 'Save changes' : 'Create contact'}
      width={760} destroyOnClose={false} maskClosable={false}
    >
      <Form form={form} layout="vertical" requiredMark="optional" className="contact-form">
        <Row gutter={16}>
          <Col xs={24} md={12}><Form.Item name="name" label="Full name" rules={[{ required: true, whitespace: true, message: 'Contact name is required' }]}><Input placeholder="e.g. Zhang San" maxLength={200} /></Form.Item></Col>
          <Col xs={24} md={12}><Form.Item name="company" label="Company"><Input placeholder="Organization" maxLength={200} /></Form.Item></Col>
          <Col xs={24} md={12}><Form.Item name="job_title" label="Job title"><Input placeholder="Role or position" maxLength={200} /></Form.Item></Col>
          <Col xs={24} md={12}><Form.Item name="category" label="Category"><Select allowClear showSearch placeholder="Choose a category" options={['Work', 'Family', 'Friends', 'Other'].map((value) => ({ value }))} /></Form.Item></Col>
        </Row>
        <Form.Item name="notes" label="Notes"><Input.TextArea rows={3} placeholder="Anything useful to remember" /></Form.Item>
        <Form.Item name="is_favorite" valuePropName="checked"><Checkbox>Mark as favorite</Checkbox></Form.Item>
        <div className="form-section-title">Contact methods</div>
        <Tabs items={methodGroups.map(({ type, label, defaultLabel }) => ({
          key: type,
          label,
          children: (
            <Form.List name={type}>
              {(fields, { add, remove }) => (
                <div className="method-list">
                  {fields.map((field) => (
                    <div className="method-row" key={field.key}>
                      <Form.Item name={[field.name, 'id']} hidden><Input /></Form.Item>
                      <Form.Item name={[field.name, 'label']} rules={[{ required: true, whitespace: true, message: 'Enter a label' }]}><Input placeholder="Label" maxLength={100} /></Form.Item>
                      <Form.Item name={[field.name, 'value']} rules={[{ required: true, whitespace: true, message: 'Enter a value' }]}><Input placeholder="Contact value" maxLength={500} /></Form.Item>
                      <Button type="text" danger icon={<MinusCircleOutlined />} onClick={() => remove(field.name)} aria-label="Remove method" />
                    </div>
                  ))}
                  {fields.length === 0 && <div className="method-empty">No {label.toLowerCase()} added yet.</div>}
                  <Button type="dashed" icon={<PlusOutlined />} onClick={() => add({ label: defaultLabel, value: '' })}>Add {label.toLowerCase().replace(/s$/, '')}</Button>
                </div>
              )}
            </Form.List>
          ),
        }))} />
      </Form>
    </Modal>
  );
}

