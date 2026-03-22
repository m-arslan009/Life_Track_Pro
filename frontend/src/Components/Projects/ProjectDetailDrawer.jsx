import {
  Drawer,
  Descriptions,
  Tag,
  Progress,
  Divider,
  Typography,
  Table,
  Button,
  Space,
} from "antd";
import { DeleteOutlined } from "@ant-design/icons";
import "./ProjectDetailDrawer.css";

const { Title, Text } = Typography;

export default function ProjectDetailDrawer({ isOpen, onClose, project }) {
  if (!project) return null;

  const teamColumns = [
    {
      title: "Name",
      key: "fullName",
      render: (_, record) => (
        <span className="team-name">
          {record.user.first_name || record.user.username}{" "}
          {record.user.last_name || ""}
        </span>
      ),
    },
    {
      title: "Username",
      key: "username",
      render: (_, record) => (
        <Text type="secondary">@{record.user.username}</Text>
      ),
    },
    {
      title: "Email",
      key: "email",
      render: (_, record) => record.user.email,
    },
    {
      title: "Role",
      dataIndex: "role",
      key: "role",
      render: (role) => <Tag color="cyan">{role}</Tag>,
    },
    {
      title: "Action",
      key: "action",
      render: (_, record) => (
        <Button
          type="text"
          danger
          icon={<DeleteOutlined />}
          onClick={() => console.log("Delete logic for", record.id)}
        />
      ),
    },
  ];

  return (
    <Drawer
      title={null}
      size={720}
      onClose={onClose}
      open={isOpen}
      rootClassName="detail-drawer"
      closeIcon={false}
      styles={{
        body: {
          background: "rgba(255, 255, 255, 0.05)",
          backdropFilter: "blur(24px)",
          WebkitBackdropFilter: "blur(24px)",
          color: "#fff",
          borderLeft: "1px solid rgba(255, 255, 255, 0.1)",
          boxShadow: "-10px 0 30px rgba(0, 0, 0, 0.3)",
        },
        header: {
          background: "transparent",
          borderBottom: "1px solid rgba(255, 255, 255, 0.1)",
        },
      }}
    >
      <div className="drawer-header-content">
        <Title level={2} className="detail-title">
          {project.project_name}
        </Title>
        <Text type="secondary" className="detail-subtitle">
          ID: {project.id}
        </Text>
      </div>

      <Divider />

      <Descriptions
        column={{ xs: 1, sm: 2 }}
        bordered
        size="middle"
        labelStyle={{
          backgroundColor: "rgba(255, 255, 255, 0.04)",
          color: "rgba(255, 255, 255, 0.6)",
        }}
        contentStyle={{ backgroundColor: "transparent", color: "#fff" }}
      >
        <Descriptions.Item label="Current Status">
          {project.status === "active" && <Tag color="blue">Active</Tag>}
          {project.status === "on_track" && <Tag color="green">On Track</Tag>}
          {project.status === "at_risk" && <Tag color="red">At Risk</Tag>}
          {project.status === "complete" && <Tag color="gold">Complete</Tag>}
        </Descriptions.Item>
        <Descriptions.Item label="Start Date">
          {project.start_date}
        </Descriptions.Item>
        <Descriptions.Item label="Due Date">
          {project.due_date}
        </Descriptions.Item>
      </Descriptions>

      <div className="section-spacer">
        <Title level={5} className="section-title">Progress</Title>
        <Progress
            percent={project.progress}
            type="circle"
            strokeColor={{ "0%": "#00C9FF", "100%": "#92FE9D" }}
            railColor="rgba(255, 255, 255, 0.1)"
          />
      </div>

      <div className="section-spacer">
        <Title level={5} className="section-title">
          Project Overview
        </Title>
        <div className="project-description-box">
          <Text>
            {project.project_description || "No description provided for this project."}
          </Text>
        </div>
      </div>

      <div className="section-spacer">
        <Title level={5} className="section-title">
          Team Members
        </Title>
        <Table
          columns={teamColumns}
          dataSource={project.teamMembers || []}
          rowKey="id"
          pagination={false}
          className="custom-table team-table"
          scroll={{ x: "max-content" }}
        />
      </div>

      <div className="drawer-footer">
        <Button onClick={onClose} className="drawer-close-btn" size="large">
          Close Details
        </Button>
      </div>
    </Drawer>
  );
}
