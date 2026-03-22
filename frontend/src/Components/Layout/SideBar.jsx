import React from 'react';
import { Layout, Menu, Button, Typography } from 'antd';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import {
  AppstoreOutlined,
  ProjectOutlined,
  FlagOutlined,
  CheckSquareOutlined,
  CalendarOutlined,
  BarChartOutlined,
  BellOutlined,
  SettingOutlined,
  LogoutOutlined,
  RobotOutlined
} from '@ant-design/icons';
import { logoutUser } from '../../Services/userServices';
import './SideBar.css';

const { Sider, Content } = Layout;
const { Title, Paragraph } = Typography;

export default function SideBar() {
  const navigate = useNavigate();
  const { pathname } = useLocation();

  const handleLogout = () => {
    logoutUser();
    navigate('/login');
  };

  // Define sidebar items based on extracted JSON data
  const menuItems = [
    {
      key: '/dashboard',
      icon: <AppstoreOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/projects',
      icon: <ProjectOutlined />,
      label: 'My Projects',
    },
    {
      key: '/milestones',
      icon: <FlagOutlined />,
      label: 'Milestones',
    },
    {
      key: '/tasks',
      icon: <CheckSquareOutlined />,
      label: 'Tasks',
    },
    {
      key: '/calendar',
      icon: <CalendarOutlined />,
      label: 'Calendar',
    },
    {
      key: '/reports',
      icon: <BarChartOutlined />,
      label: 'Reports',
    },
    {
      key: '/assistant',
      icon: <RobotOutlined />,
      label: 'AI Assistant',
    },
    {
      key: '/notifications',
      icon: <BellOutlined />,
      label: 'Notifications',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: 'Settings',
    },
  ];

  return (
    <Layout className="main-layout">
      <Sider 
        width={260}
        className="sidebar"
        breakpoint="lg"
        collapsedWidth="0"
      >
        <div className="sidebar-brand-wrap">
          <Title level={4} className="sidebar-brand-title">LifeTrack Pro</Title>
        </div>

        <div className="sidebar-body-wrap">
          <Menu
            mode="inline"
            selectedKeys={[pathname]}
            onClick={({ key }) => navigate(key)}
            items={menuItems}
            className="sidebar-menu"
          />

          <div className="sidebar-logout-wrap">
            <Button
              size="large"
              icon={<LogoutOutlined />}
              className="sidebar-logout-button"
              onClick={handleLogout}
              block
            >
              Logout
            </Button>
          </div>
        </div>
      </Sider>
      
      <Layout className="site-layout">
        <Content className="site-content">
          <div className="content-container">
            <Outlet />
          </div>
        </Content>
      </Layout>
    </Layout>
  );
}
