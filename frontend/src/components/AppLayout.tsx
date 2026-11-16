import { useState } from 'react';
import {
  AppstoreOutlined,
  ContactsOutlined,
  FileExcelOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  StarOutlined,
} from '@ant-design/icons';
import { Button, Drawer, Grid, Layout, Menu } from 'antd';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';

const { Header, Sider, Content } = Layout;
const menuItems = [
  { key: '/', icon: <AppstoreOutlined />, label: 'Dashboard' },
  { key: '/contacts', icon: <ContactsOutlined />, label: 'Contacts' },
  { key: '/favorites', icon: <StarOutlined />, label: 'Favorites' },
  { key: '/import-export', icon: <FileExcelOutlined />, label: 'Import / Export' },
];

function Navigation({ onSelect }: { onSelect?: () => void }) {
  const navigate = useNavigate();
  const location = useLocation();
  return (
    <>
      <div className="brand">
        <div className="brand-mark">C</div>
        <div><strong>ContactHub</strong><span>Your people, organized</span></div>
      </div>
      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={({ key }) => { navigate(key); onSelect?.(); }}
      />
    </>
  );
}

export default function AppLayout() {
  const screens = Grid.useBreakpoint();
  const mobile = !screens.lg;
  const [collapsed, setCollapsed] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);

  return (
    <Layout className="app-shell">
      {!mobile && (
        <Sider width={250} collapsed={collapsed} className="sidebar" trigger={null}>
          <Navigation />
        </Sider>
      )}
      <Drawer placement="left" width={270} open={mobile && drawerOpen} onClose={() => setDrawerOpen(false)} closable={false} className="mobile-nav">
        <Navigation onSelect={() => setDrawerOpen(false)} />
      </Drawer>
      <Layout>
        <Header className="topbar">
          <Button
            type="text"
            icon={mobile || collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => mobile ? setDrawerOpen(true) : setCollapsed(!collapsed)}
            aria-label="Toggle navigation"
          />
          <div className="topbar-title">Address Book Management</div>
          <div className="version-chip">v1.0.1</div>
        </Header>
        <Content className="content"><Outlet /></Content>
      </Layout>
    </Layout>
  );
}

