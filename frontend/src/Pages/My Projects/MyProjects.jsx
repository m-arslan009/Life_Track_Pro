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
  Select,
  notification,
} from "antd";
import {
  PlusOutlined,
  EyeOutlined,
  DeleteOutlined,
  EditOutlined,
} from "@ant-design/icons";
import ProjectFormModal from "../../Components/Projects/ProjectFormModal";
import ProjectDetailDrawer from "../../Components/Projects/ProjectDetailDrawer";
import "./MyProjects.css";

import { useLoaderData } from "react-router-dom";
import { message, Popconfirm } from "antd";
import ProjectDashboard from "../../Components/Projects/ProjectDashboard";
import { useDispatch, useSelector } from "react-redux";
import {
  deleteProjectThunk,
  fetchProjects,
  getSelectedProject,
  selectProjects,
  selectProjectsLoading,
  setSelectedProject,
  updateProjectStatusThunk,
} from "../../Services/ProjectSlice";
import {
  getCurrentUser,
  getStoredAuthUserId,
} from "../../Services/userServices";

const { Title } = Typography;

export default function MyProjects() {
  const dispatch = useDispatch();
  const [api, contextHolder] = notification.useNotification();
  const { users } = useLoaderData();
  const projects = useSelector(selectProjects);
  const selectedProject = useSelector(getSelectedProject);
  const isLoading = useSelector(selectProjectsLoading);
  const [isProjectDashboardOpen, setIsProjectDashboardOpen] = useState(false);
  const [authUserId, setAuthUserId] = useState(() => getStoredAuthUserId());

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [formMode, setFormMode] = useState("create"); // 'create' or 'update'

  useEffect(() => {
    dispatch(fetchProjects()).catch(() => {
      notification.error({
        message: "Failed to load projects",
        description:
          "Unable to load project. Check your internet and make sure backend is running",
        duration: 1.5,
        placement: "topRight",
      });
    });
  }, [dispatch]);

  useEffect(() => {
    if (authUserId) return;

    getCurrentUser()
      .then((user) => setAuthUserId(user?.id || null))
      .catch(() => {
        setAuthUserId(null);
      });
  }, [authUserId]);

  const handleOpenDetail = (record) => {
    dispatch(setSelectedProject(record));
    setIsProjectDashboardOpen(true);
  };

  const handleOpenCreate = () => {
    setFormMode("create");
    dispatch(setSelectedProject(null));
    setIsFormOpen(true);
  };

  const handleOpenEdit = (record) => {
    setFormMode("update");
    dispatch(setSelectedProject(record));
    setIsFormOpen(true);
  };

  const handleFormSuccess = () => {};

  const handleDeleteProject = async (projectId) => {
    try {
      await dispatch(deleteProjectThunk(projectId));
      api.success({
        message: "Deletion Successful",
        description: "Project deleted successfully",
        duration: 3,
        placement: "topRight",
      });
    } catch (error) {
      message.error(error.message || "Failed to delete project");
    }
  };

  const handleStatusChange = async (record, status) => {
    try {
      await dispatch(
        updateProjectStatusThunk({ projectId: record.id, status }),
      );
      api.success({
        message: "Status Updated",
        description: `${record.project_name} is now ${status.replace("_", " ")}.`,
        duration: 2,
        placement: "topRight",
      });
    } catch (error) {
      api.error({
        message: "Status Update Failed",
        description: error.message || "Could not update project status.",
        duration: 2,
        placement: "topRight",
      });
    }
  };

  const canManageProject = (record) => {
    if (!authUserId) return false;
    return Number(record.owner_id) === Number(authUserId);
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
      render: (status, record) => (
        <Select
          size="small"
          value={status}
          disabled={!canManageProject(record)}
          onChange={(nextStatus) => handleStatusChange(record, nextStatus)}
          options={[
            { label: "Active", value: "active" },
            { label: "On Track", value: "on_track" },
            { label: "At Risk", value: "at_risk" },
            { label: "Complete", value: "complete" },
          ]}
          style={{ minWidth: 126 }}
        />
      ),
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
      render: (_, record) => {
        const isOwner = canManageProject(record);

        return (
          <Space size="middle">
            <Tooltip title="View Project Details">
              <Button
                type="primary"
                icon={<EyeOutlined />}
                onClick={() => handleOpenDetail(record)}
                className="action-btn"
              />
            </Tooltip>
            <Tooltip
              title={
                isOwner
                  ? "Edit Project"
                  : "Only project creator can edit project details"
              }
            >
              <Button
                type="primary"
                icon={<EditOutlined />}
                onClick={() => handleOpenEdit(record)}
                className="action-btn edit-btn"
                disabled={!isOwner}
              />
            </Tooltip>
            <Tooltip
              title={
                isOwner
                  ? "Delete Project"
                  : "Only project creator can delete this project"
              }
            >
              <Popconfirm
                title="Delete Project"
                description="Are you sure you want to delete this project? This action cannot be undone."
                onConfirm={() => handleDeleteProject(record.id)}
                okText="Yes"
                cancelText="No"
                okButtonProps={{ danger: true }}
                disabled={!isOwner}
              >
                <Button
                  type="primary"
                  danger
                  icon={<DeleteOutlined />}
                  className="action-btn"
                  disabled={!isOwner}
                />
              </Popconfirm>
            </Tooltip>
          </Space>
        );
      },
    },
  ];

  return (
    <div className="projects-container">
      <Card className="glass-card table-card">
        {contextHolder}
        <div className="table-header">
          <div>
            <Title level={3} className="page-title">
              Projects
            </Title>
            <Typography.Text className="page-subtitle">
              Projects you created or are assigned to.
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

      <ProjectDashboard
        isOpen={isProjectDashboardOpen}
        onClose={() => setIsProjectDashboardOpen(false)}
      />

      <ProjectFormModal
        isOpen={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        userList={users}
        isCreated={formMode === "create"}
        record={selectedProject}
        onSuccess={handleFormSuccess}
      />

      {/* <ProjectDetailDrawer
        isOpen={isDetailOpen}
        onClose={() => setIsDetailOpen(false)}
        project={selectedProject}
      /> */}
    </div>
  );
}
