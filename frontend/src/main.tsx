import React from 'react';
import ReactDOM from 'react-dom/client';
import { App as AntApp, ConfigProvider } from 'antd';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './styles.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider theme={{ token: { colorPrimary: '#246bfd', borderRadius: 10, colorBgLayout: '#f4f6fa', fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif' }, components: { Layout: { siderBg: '#111827', headerBg: '#ffffff' }, Menu: { darkItemBg: '#111827', darkItemSelectedBg: '#246bfd', itemBorderRadius: 8 } } }}>
      <AntApp><BrowserRouter><App /></BrowserRouter></AntApp>
    </ConfigProvider>
  </React.StrictMode>,
);

