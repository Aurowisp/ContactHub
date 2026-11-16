import { CloudDownloadOutlined, CloudUploadOutlined, FileExcelOutlined } from '@ant-design/icons';
import { Alert, Button, Card, Col, List, Progress, Row, Statistic, Upload, message } from 'antd';
import type { UploadProps } from 'antd';
import { useState } from 'react';
import { downloadTemplate, exportContacts, importContacts } from '../api/excel';
import { getErrorMessage } from '../api/client';
import PageHeader from '../components/PageHeader';
import type { ImportResult } from '../types/contact';

export default function ImportExport() {
  const [busy, setBusy] = useState('');
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [messageApi, contextHolder] = message.useMessage();
  async function run(action: 'export' | 'template', callback: () => Promise<void>) {
    setBusy(action);
    try { await callback(); messageApi.success(action === 'export' ? 'Export downloaded' : 'Template downloaded'); }
    catch (err) { messageApi.error(getErrorMessage(err)); } finally { setBusy(''); }
  }
  const uploadProps: UploadProps = {
    accept: '.xlsx', maxCount: 1, showUploadList: false,
    beforeUpload: (file) => {
      if (!file.name.toLowerCase().endsWith('.xlsx')) { messageApi.error('Please select an .xlsx file'); return Upload.LIST_IGNORE; }
      if (file.size > 10 * 1024 * 1024) { messageApi.error('File must be 10 MB or smaller'); return Upload.LIST_IGNORE; }
      setBusy('import'); setProgress(0); setResult(null);
      importContacts(file as File, setProgress).then((data) => { setResult(data); messageApi.success(`Imported ${data.success} contact${data.success === 1 ? '' : 's'}`); }).catch((err) => messageApi.error(getErrorMessage(err))).finally(() => setBusy(''));
      return false;
    },
  };
  return (
    <div className="page-container">
      {contextHolder}
      <PageHeader eyebrow="Data tools" title="Import & export" description="Move your complete address book safely, without losing contact methods." />
      <Row gutter={[20, 20]}>
        <Col xs={24} lg={8}><Card className="transfer-card"><div className="transfer-icon blue"><CloudDownloadOutlined /></div><h2>Export contacts</h2><p>Download every contact in one Excel workbook. Multiple methods become separate, reusable columns.</p><Button type="primary" block icon={<CloudDownloadOutlined />} loading={busy === 'export'} onClick={() => run('export', exportContacts)}>Export all to Excel</Button></Card></Col>
        <Col xs={24} lg={8}><Card className="transfer-card"><div className="transfer-icon green"><CloudUploadOutlined /></div><h2>Import contacts</h2><p>Add contacts from a valid ContactHub workbook. Invalid rows are reported while valid rows continue.</p><Upload {...uploadProps}><Button block icon={<CloudUploadOutlined />} loading={busy === 'import'}>Choose .xlsx file</Button></Upload>{busy === 'import' && <Progress percent={progress} size="small" />}</Card></Col>
        <Col xs={24} lg={8}><Card className="transfer-card"><div className="transfer-icon gold"><FileExcelOutlined /></div><h2>Start with a template</h2><p>Use the documented workbook with example data and columns for every supported contact method.</p><Button block icon={<FileExcelOutlined />} loading={busy === 'template'} onClick={() => run('template', downloadTemplate)}>Download template</Button></Card></Col>
      </Row>
      {result && <Card className="result-card" title="Import completed">
        <Row gutter={[16, 16]}><Col xs={12} md={6}><Statistic title="Rows processed" value={result.total} /></Col><Col xs={12} md={6}><Statistic title="Successful" value={result.success} valueStyle={{ color: '#16835b' }} /></Col><Col xs={12} md={6}><Statistic title="Empty rows skipped" value={result.skipped} /></Col><Col xs={12} md={6}><Statistic title="Errors" value={result.errors.length} valueStyle={{ color: result.errors.length ? '#c93c3c' : undefined }} /></Col></Row>
        {result.errors.length > 0 ? <Alert type="warning" showIcon message="Some rows need attention" description={<List size="small" dataSource={result.errors} renderItem={(error) => <List.Item>Row {error.row}: {error.reason}</List.Item>} />} /> : <Alert type="success" showIcon message="Every row was imported successfully." />}
      </Card>}
    </div>
  );
}

