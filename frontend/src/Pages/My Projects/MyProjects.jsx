import { useState, useEffect } from "react";
import {
  Table,
  Button,
  Tag,
  Progress,
  Space,
  Typography,
  Card,
  Tooltip,
  notification
} from "antd";
import { PlusOutlined, EyeOutlined, DeleteOutlined, EditOutlined } from "@ant-design/icons";
import ProjectFormModal from "../../Components/Projects/ProjectFormModal";
import ProjectDetailDrawer from "../../Components/Projects/ProjectDetailDrawer";
import "./MyProjects.css";

import { deleteProject } from "../../Services/projectServices";
import { useLoaderData } from "react-router-dom";
import { message, Popconfirm } from "antd";

const { Title } = Typography;

export default function MyProjects() {
  const [api, contextHolder] = notification.useNotification()
  const { users, projects: loadedProjects } = useLoaderData();
  const [projects, setProjects] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [formMode, setFormMode] = useState('create'); // 'create' or 'update'

  const [selectedProject, setSelectedProject] = useState(null);

  useEffect(() => {
    if (loadedProjects) {
      setProjects(loadedProjects);
      setIsLoading(false);
    }
  }, [loadedProjects]);


  const handleOpenDetail = (record) => {
    setSelectedProject(record);
    setIsDetailOpen(true);
  };

  const handleOpenCreate = () => {
    setFormMode('create');
    setSelectedProject(null);
    setIsFormOpen(true);
  };

  const handleOpenEdit = (record) => {
    setFormMode('update');
    setSelectedProject(record);
    setIsFormOpen(true);
  };

  const handleFormSuccess = (project, mode) => {
    if (mode === 'create') {
      setProjects([project, ...projects]);
    } else {
      setProjects(projects.map(p => p.id === project.id ? project : p));
    }
  };

  const handleDeleteProject = async (projectId) => {
    try {
      await deleteProject(projectId);
      api.success({
        message: "Deletion Successful",
        description: "Project deleted successfully",
        duration: 3, 
        placement: "topRight"
      });
      setProjects(projects.filter((p) => p.id !== projectId));
    } catch (error) {
      message.error(error.message || "Failed to delete project");
    }
  };

  const getStatusTag = (status) => {
    switch (status) {
      case "active":
        return <Tag color="blue">Active</Tag>;
      case "on_track":
        return <Tag color="green">On Track</Tag>;
      case "at_risk":
        return <Tag color="red">At Risk</Tag>;
      case "complete":
        return <Tag color="gold">Complete</Tag>;
      default:
        return <Tag>{status}</Tag>;
    }
  };

  const columns = [
    {
      title: "Project Name",
      dataIndex: "project_name",
      key: "project_name",
      render: (text) => <span className="project-name-cell">{text}</span>,
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (status) => getStatusTag(status),
    },
    {
      title: "Start Date",
      dataIndex: "start_date",
      key: "start_date",
    },
    {
      title: "Progress",
      dataIndex: "progress",
      key: "progress",
      render: (progress) => (
        <Progress
          percent={progress}
          size="small"
          strokeColor={{
            "0%": "#00C9FF",
            "100%": "#92FE9D",
          }}
          trailColor="rgba(255, 255, 255, 0.1)"
        />
      ),
    },
    {
      title: "Actions",
      key: "actions",
      render: (_, record) => (
        <Space size="middle">
          <Tooltip title="View Project Details">
            <Button
              type="primary"
              icon={<EyeOutlined />}
              onClick={() => handleOpenDetail(record)}
              className="action-btn"
            />
          </Tooltip>
          <Tooltip title="Edit Project">
            <Button
              type="primary"
              icon={<EditOutlined />}
              onClick={() => handleOpenEdit(record)}
              className="action-btn edit-btn"
            />
          </Tooltip>
          <Tooltip title="Delete Project">
            <Popconfirm
              title="Delete Project"
              description="Are you sure you want to delete this project? This action cannot be undone."
              onConfirm={() => handleDeleteProject(record.id)}
              okText="Yes"
              cancelText="No"
              okButtonProps={{ danger: true }}
            >
              <Button
                type="primary"
                danger
                icon={<DeleteOutlined />}
                className="action-btn"
              />
            </Popconfirm>
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <div className="projects-container">
      <Card className="glass-card table-card">
        {contextHolder}
        <div className="table-header">
          <div>
            <Title level={3} className="page-title">
              My Projects
            </Title>
            <Typography.Text className="page-subtitle">
              Track and manage your active project workflows.
            </Typography.Text>
          </div>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleOpenCreate}
            size="large"
            className="create-btn"
          >
            Create Project
          </Button>
        </div>

        <Table
          columns={columns}
          dataSource={projects}
          rowKey="id"
          loading={isLoading}
          pagination={{ pageSize: 8 }}
          className="custom-table"
          scroll={{ x: "max-content" }}
        />
      </Card>

      <ProjectFormModal
        isOpen={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        userList={users}
        isCreated={formMode === 'create'}
        record={selectedProject}
        onSuccess={handleFormSuccess}
      />

      <ProjectDetailDrawer
        isOpen={isDetailOpen}
        onClose={() => setIsDetailOpen(false)}
        project={selectedProject}
      />
    </div>
  );
}
