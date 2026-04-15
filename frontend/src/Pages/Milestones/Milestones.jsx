import { useEffect, useMemo, useState } from "react";
import {
  Button,
  Card,
  DatePicker,
  Form,
  Input,
  Modal,
  Popconfirm,
  Select,
  Space,
  Table,
  Tag,
  Typography,
  notification,
} from "antd";
import {
  DeleteOutlined,
  EditOutlined,
  PlusOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import dayjs from "dayjs";

import {
  createMilestone,
  deleteMilestone,
  getMilestones,
  updateMilestone,
} from "../../Services/milestoneServices";
import { useDispatch, useSelector } from "react-redux";
import { fetchProjects, selectProjects } from "../../Services/ProjectSlice";
import "../My Projects/MyProjects.css";
import "./Milestones.css";
import { getStoredAuthUserId } from "../../Services/userServices";

const { Title, Text } = Typography;
const { TextArea } = Input;
const { RangePicker } = DatePicker;

const statusOptions = [
  { label: "Planned", value: "planned" },
  { label: "In Progress", value: "in_progress" },
  { label: "Completed", value: "completed" },
  { label: "Delayed", value: "delayed" },
];

const statusColors = {
  planned: "default",
  in_progress: "processing",
  completed: "success",
  delayed: "error",
};

export default function Milestones() {
  const dispatch = useDispatch();
  const projects = useSelector(selectProjects);
  const [form] = Form.useForm();
  const [api, contextHolder] = notification.useNotification();

  const [milestones, setMilestones] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const authUserId = getStoredAuthUserId();
  const [selectedProjectId, setSelectedProjectId] = useState("all");
  const [editingMilestone, setEditingMilestone] = useState(null);

  const isEditing = Boolean(editingMilestone);
  const selectedProjectValue = Form.useWatch("project", form);

  const selectedProject = useMemo(
    () => projects.find((project) => project.id === selectedProjectValue),
    [projects, selectedProjectValue],
  );

  const ownedProjects = useMemo(
    () =>
      projects.filter(
        (project) =>
          authUserId != null && Number(project.owner_id) === Number(authUserId),
      ),
    [projects, authUserId],
  );

  const selectedProjectTeamMemberOptions = useMemo(() => {
    if (!selectedProject?.teamMembers) return [];

    return selectedProject.teamMembers.map((tm) => ({
      label:
        `${tm.user?.first_name || tm.user?.username || "User"} ${tm.user?.last_name || ""}`.trim(),
      value: tm.id,
    }));
  }, [selectedProject]);

  const loadMilestones = async (projectFilter) => {
    const projectId =
      projectFilter && projectFilter !== "all" ? projectFilter : null;
    const data = await getMilestones(projectId);
    setMilestones(data);
  };

  const loadData = async (projectFilter = selectedProjectId) => {
    setIsLoading(true);
    try {
      await dispatch(fetchProjects());
      await loadMilestones(projectFilter);
    } catch (error) {
      api.error({
        message: "Failed to Load Milestones",
        description: error.message || "Could not load data.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleProjectFilterChange = async (value) => {
    setSelectedProjectId(value);
    setIsLoading(true);
    try {
      await loadMilestones(value);
    } catch (error) {
      api.error({
        message: "Filter Failed",
        description: error.message || "Could not filter milestones.",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const canManageMilestone = (record) => {
    const project = projects.find((item) => item.id === record.project);
    return Boolean(
      authUserId != null &&
      project &&
      Number(project.owner_id) === Number(authUserId),
    );
  };

  const projectOptions = useMemo(
    () => [
      { label: "All Projects", value: "all" },
      ...projects.map((project) => ({
        label: project.project_name,
        value: project.id,
      })),
    ],
    [projects],
  );

  const openCreateModal = () => {
    if (ownedProjects.length === 0) {
      api.warning({
        message: "No Owned Projects",
        description: "You can only create milestones for projects you own.",
      });
      return;
    }
    setEditingMilestone(null);
    form.resetFields();
    form.setFieldsValue({ status: "planned" });
    setIsModalOpen(true);
  };

  const openEditModal = (record) => {
    setEditingMilestone(record);
    form.setFieldsValue({
      project: record.project,
      title: record.title,
      description: record.description,
      status: record.status,
      timeline: [dayjs(record.start_date), dayjs(record.due_date)],
      members: (record.members || []).map((member) =>
        typeof member === "object" ? member.id : member,
      ),
    });
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingMilestone(null);
    form.resetFields();
  };

  const normalizeApiError = (message) => {
    try {
      const parsed = JSON.parse(message);
      if (typeof parsed === "object" && parsed !== null) {
        return Object.entries(parsed)
          .map(
            ([field, msgs]) =>
              `${field}: ${Array.isArray(msgs) ? msgs.join(", ") : msgs}`,
          )
          .join(" | ");
      }
      return message;
    } catch {
      return message;
    }
  };

  const handleSubmit = async (values) => {
    setIsSubmitting(true);
    try {
      const payload = {
        project: values.project,
        title: values.title,
        description: values.description || "",
        status: values.status,
        members: values.members || [],
        start_date: values.timeline[0].format("YYYY-MM-DD"),
        due_date: values.timeline[1]
          ? values.timeline[1].format("YYYY-MM-DD")
          : null,
      };

      if (
        !selectedProject ||
        Number(selectedProject.owner_id) !== Number(authUserId)
      ) {
        throw new Error(
          "Only the project owner can manage milestones for this project.",
        );
      }

      if (isEditing) {
        const updated = await updateMilestone(editingMilestone.id, payload);
        setMilestones((prev) =>
          prev.map((m) => (m.id === updated.id ? updated : m)),
        );
        api.success({
          message: "Milestone Updated",
          description: "Milestone has been updated successfully.",
        });
      } else {
        const created = await createMilestone(payload);
        setMilestones((prev) => [created, ...prev]);
        api.success({
          message: "Milestone Created",
          description: "Milestone has been created successfully.",
        });
      }

      closeModal();
    } catch (error) {
      api.error({
        message: isEditing ? "Update Failed" : "Create Failed",
        description: normalizeApiError(
          error.message || "Please check your input fields.",
        ),
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (milestoneId) => {
    try {
      await deleteMilestone(milestoneId);
      setMilestones((prev) => prev.filter((m) => m.id !== milestoneId));
      api.success({
        message: "Milestone Deleted",
        description: "Milestone has been deleted.",
      });
    } catch (error) {
      api.error({
        message: "Delete Failed",
        description: error.message || "Could not delete milestone.",
      });
    }
  };

  const columns = [
    {
      title: "Title",
      dataIndex: "title",
      key: "title",
      render: (title) => <span className="project-name-cell">{title}</span>,
    },
    {
      title: "Project",
      dataIndex: "project",
      key: "project",
      render: (projectId) => {
        const project = projects.find((p) => p.id === projectId);
        return project?.project_name || `Project #${projectId}`;
      },
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (status) => (
        <Tag color={statusColors[status] || "default"}>
          {status.replace("_", " ").toUpperCase()}
        </Tag>
      ),
    },
    {
      title: "Timeline",
      key: "timeline",
      render: (_, record) => (
        <span>
          {record.start_date} to {record.due_date}
        </span>
      ),
    },
    {
      title: "Actions",
      key: "actions",
      render: (_, record) =>
        canManageMilestone(record) ? (
          <Space size="middle">
            <Button
              type="primary"
              icon={<EditOutlined />}
              onClick={() => openEditModal(record)}
              className="action-btn edit-btn"
            />
            <Popconfirm
              title="Delete Milestone"
              description="Are you sure you want to delete this milestone?"
              onConfirm={() => handleDelete(record.id)}
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
          </Space>
        ) : (
          <Tag>View only</Tag>
        ),
    },
  ];

  return (
    <div className="projects-container milestones-container">
      {contextHolder}
      <Card className="glass-card table-card">
        <div className="table-header milestones-header">
          <div>
            <Title level={3} className="page-title">
              Milestones
            </Title>
            <Text className="page-subtitle">
              Break projects into measurable checkpoints and track delivery.
            </Text>
          </div>
          <Space wrap>
            <Select
              className="milestone-project-filter"
              value={selectedProjectId}
              onChange={handleProjectFilterChange}
              options={projectOptions}
            />
            <Button
              icon={<ReloadOutlined />}
              className="action-btn"
              onClick={() => loadData(selectedProjectId)}
            >
              Refresh
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={openCreateModal}
              size="large"
              className="create-btn"
              disabled={ownedProjects.length === 0}
            >
              Create Milestone
            </Button>
          </Space>
        </div>

        <Table
          columns={columns}
          dataSource={milestones}
          rowKey="id"
          loading={isLoading}
          pagination={{ pageSize: 8 }}
          className="custom-table"
          scroll={{ x: "max-content" }}
        />
      </Card>

      <Modal
        title={isEditing ? "Update Milestone" : "Create New Milestone"}
        open={isModalOpen}
        onCancel={closeModal}
        footer={null}
        width={620}
        centered
      >
        <Form
          layout="vertical"
          form={form}
          onFinish={handleSubmit}
          initialValues={{ status: "planned" }}
        >
          <Form.Item
            name="project"
            label="Project"
            rules={[{ required: true, message: "Please select a project" }]}
          >
            <Select
              options={ownedProjects.map((project) => ({
                label: project.project_name,
                value: project.id,
              }))}
              placeholder="Select project"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="title"
            label="Milestone Title"
            rules={[{ required: true, message: "Please enter a title" }]}
          >
            <Input size="large" placeholder="e.g., MVP Feature Freeze" />
          </Form.Item>

          <Form.Item name="description" label="Description">
            <TextArea rows={3} placeholder="Optional milestone details" />
          </Form.Item>

          <Form.Item
            name="timeline"
            label="Start & Due Date"
            rules={[
              { required: true, message: "Please choose start and due dates" },
            ]}
          >
            <RangePicker style={{ width: "100%" }} size="large" />
          </Form.Item>

          <Form.Item
            name="status"
            label="Status"
            rules={[{ required: true, message: "Please select a status" }]}
          >
            <Select options={statusOptions} size="large" />
          </Form.Item>

          <Form.Item
            name="members"
            label="Assigned Members"
            dependencies={["project"]}
          >
            <Select
              mode="multiple"
              options={selectedProjectTeamMemberOptions}
              placeholder={
                selectedProjectValue
                  ? "Select project members"
                  : "Select project first"
              }
              disabled={!selectedProjectValue}
              size="large"
            />
          </Form.Item>

          <div className="modal-footer-actions">
            <Button
              onClick={closeModal}
              style={{ marginRight: 12 }}
              size="large"
            >
              Cancel
            </Button>
            <Button
              type="primary"
              htmlType="submit"
              loading={isSubmitting}
              className="create-btn"
              size="large"
            >
              {isEditing ? "Update Milestone" : "Create Milestone"}
            </Button>
          </div>
        </Form>
      </Modal>
    </div>
  );
}
