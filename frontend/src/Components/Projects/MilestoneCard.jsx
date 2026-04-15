import {
  Card,
  Form,
  Input,
  notification,
  DatePicker,
  Select,
  Button,
  Empty,
  Tag,
  Space,
  Progress,
  Typography,
  Popconfirm,
} from "antd";
import {
  CloseOutlined,
  DeleteOutlined,
  EditOutlined,
  PlusOutlined,
  SaveOutlined,
} from "@ant-design/icons";
import dayjs from "dayjs";
import { useEffect, useMemo, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import {
  fetchProjects,
  getSelectedProject,
  setSelectedProject,
} from "../../Services/ProjectSlice";
import { getStoredAuthUserId } from "../../Services/userServices";
import {
  createMilestone,
  createTask,
  deleteMilestone,
  deleteTask,
  updateMilestone,
  updateMilestoneStatus,
  updateTask,
  updateTaskStatus,
} from "../../Services/milestoneServices";
import { getMilestoneWorkSummary } from "../../Utils/projectProgress";

const { Text, Title } = Typography;

const milestoneStatusOptions = [
  { label: "Planned", value: "planned" },
  { label: "In Progress", value: "in_progress" },
  { label: "Completed", value: "completed" },
  { label: "Delayed", value: "delayed" },
];

const taskStatusOptions = [
  { label: "To Do", value: "todo" },
  { label: "In Progress", value: "in_progress" },
  { label: "Done", value: "done" },
  { label: "Blocked", value: "blocked" },
];

function MilestoneCard({ teamMembers = [], initialMilestones = [] }) {
  const { RangePicker } = DatePicker;
  const [form] = Form.useForm();
  const dispatch = useDispatch();
  const selectedProject = useSelector(getSelectedProject);
  const currentUserId = getStoredAuthUserId();
  const isProjectOwner =
    selectedProject?.owner_id != null &&
    Number(selectedProject.owner_id) === Number(currentUserId);
  const [isAddingMilestone, setIsAddingMilestone] = useState(false);
  const [editingMilestone, setEditingMilestone] = useState(null);
  const [expandedTaskFormMilestoneId, setExpandedTaskFormMilestoneId] =
    useState(null);
  const [taskDraftsByMilestone, setTaskDraftsByMilestone] = useState({});
  const [editingTaskByMilestone, setEditingTaskByMilestone] = useState({});

  const normalizeMilestones = (milestones) =>
    (milestones || []).map((ms, index) => ({
      id: ms.id || `existing-${index}`,
      title: ms.title || "Untitled Milestone",
      status: ms.status || "planned",
      start_date: ms.start_date,
      due_date: ms.due_date,
      teamMembers: ms.teamMembers || ms.team_members || [],
      tasks: (ms.tasks || ms.milestone_tasks || []).map((task, taskIndex) => ({
        id: task.id || `task-${index}-${taskIndex}`,
        title: task.title || "Untitled Task",
        status: task.status || "todo",
        assignee: task.assignee ?? task.assignee_id ?? null,
      })),
    }));

  const [projectMileStones, setProjectMileStones] = useState(() =>
    normalizeMilestones(initialMilestones),
  );

  useEffect(() => {
    setProjectMileStones(normalizeMilestones(initialMilestones));
  }, [initialMilestones]);

  const teamMemberLabelById = useMemo(() => {
    const map = new Map();

    teamMembers.forEach((tm) => {
      const firstName = tm.user?.first_name || "";
      const lastName = tm.user?.last_name || "";
      const fullName = `${firstName} ${lastName}`.trim();
      map.set(tm.id, fullName || tm.user?.username || `Member ${tm.id}`);
    });

    return map;
  }, [teamMembers]);

  const syncSelectedProject = async () => {
    if (!selectedProject?.id) return;

    const latestProjects = await dispatch(fetchProjects());
    const latest = (latestProjects || []).find(
      (project) => project.id === selectedProject.id,
    );

    if (latest) {
      dispatch(setSelectedProject(latest));
    }
  };

  const upsertMilestone = (nextMilestone) => {
    setProjectMileStones((prev) => {
      const found = prev.some((ms) => ms.id === nextMilestone.id);
      if (found) {
        return prev.map((ms) =>
          ms.id === nextMilestone.id ? nextMilestone : ms,
        );
      }
      return [nextMilestone, ...prev];
    });
  };

  const patchMilestoneById = (milestoneId, patcher) => {
    setProjectMileStones((prev) =>
      prev.map((ms) => (ms.id === milestoneId ? patcher(ms) : ms)),
    );
  };

  const handleMilestoneSubmit = async (values) => {
    if (!selectedProject?.id) {
      notification.error({
        message: "Project Missing",
        description: "Please select a project before managing milestones.",
        placement: "topRight",
      });
      return;
    }

    const payload = {
      project: selectedProject.id,
      title: values.title,
      status: values.status || "planned",
      description: values.description || "",
      members: values.teamMembers || [],
      start_date: values.dates?.[0]?.format("YYYY-MM-DD"),
      due_date: values.dates?.[1]?.format("YYYY-MM-DD"),
    };

    try {
      if (editingMilestone?.id) {
        const updated = await updateMilestone(editingMilestone.id, payload);
        upsertMilestone({
          ...updated,
          teamMembers: updated.teamMembers || updated.team_members || [],
          tasks: updated.tasks || updated.milestone_tasks || [],
        });
        notification.success({
          message: "Milestone Updated",
          placement: "topRight",
        });
      } else {
        const created = await createMilestone(payload);
        upsertMilestone({
          ...created,
          teamMembers: created.teamMembers || created.team_members || [],
          tasks: created.tasks || created.milestone_tasks || [],
        });
        notification.success({
          message: "Milestone Created",
          placement: "topRight",
        });
      }

      form.resetFields();
      setIsAddingMilestone(false);
      setEditingMilestone(null);
      await syncSelectedProject();
    } catch (error) {
      notification.error({
        message: editingMilestone ? "Update Failed" : "Create Failed",
        description: error?.message || "Unable to save milestone.",
        placement: "topRight",
      });
    }
  };

  const handleEditMilestone = (milestone) => {
    setIsAddingMilestone(true);
    setEditingMilestone(milestone);
    form.setFieldsValue({
      title: milestone.title,
      description: milestone.description || "",
      status: milestone.status || "planned",
      dates: [dayjs(milestone.start_date), dayjs(milestone.due_date)],
      teamMembers: milestone.teamMembers || [],
    });
  };

  const handleDeleteMilestone = async (milestoneId) => {
    try {
      await deleteMilestone(milestoneId);
      setProjectMileStones((prev) =>
        prev.filter((ms) => ms.id !== milestoneId),
      );
      notification.success({
        message: "Milestone Deleted",
        placement: "topRight",
      });
      await syncSelectedProject();
    } catch (error) {
      notification.error({
        message: "Delete Failed",
        description: error?.message || "Unable to delete milestone.",
        placement: "topRight",
      });
    }
  };

  const handleMilestoneStatusChange = async (milestoneId, statusValue) => {
    try {
      const updated = await updateMilestoneStatus(milestoneId, statusValue);
      upsertMilestone({
        ...updated,
        teamMembers: updated.teamMembers || updated.team_members || [],
        tasks: updated.tasks || updated.milestone_tasks || [],
      });
      await syncSelectedProject();
    } catch (error) {
      notification.error({
        message: "Milestone Status Update Failed",
        description: error?.message || "Unable to update milestone status.",
        placement: "topRight",
      });
    }
  };

  const handleTaskDraftChange = (milestoneId, updates) => {
    setTaskDraftsByMilestone((prev) => ({
      ...prev,
      [milestoneId]: {
        ...(prev[milestoneId] || {
          title: "",
          status: "todo",
          assignee: undefined,
        }),
        ...updates,
      },
    }));
  };

  const handleAddTask = async (milestone) => {
    if (!selectedProject?.id) return;

    const draft = taskDraftsByMilestone[milestone.id] || {
      title: "",
      status: "todo",
      assignee: undefined,
    };

    const title = draft.title?.trim();
    if (!title) {
      notification.error({
        message: "Task Title Required",
        description: "Please enter a task title.",
        placement: "topRight",
      });
      return;
    }

    try {
      const createdTask = await createTask({
        title,
        description: "",
        status: draft.status || "todo",
        project: selectedProject.id,
        milestone: milestone.id,
        assignee: draft.assignee || null,
      });

      patchMilestoneById(milestone.id, (existing) => ({
        ...existing,
        tasks: [...(existing.tasks || []), createdTask],
      }));

      setTaskDraftsByMilestone((prev) => ({
        ...prev,
        [milestone.id]: {
          title: "",
          status: "todo",
          assignee: undefined,
        },
      }));
      setExpandedTaskFormMilestoneId(null);

      notification.success({
        message: "Task Created",
        placement: "topRight",
      });
      await syncSelectedProject();
    } catch (error) {
      notification.error({
        message: "Task Create Failed",
        description: error?.message || "Unable to create task.",
        placement: "topRight",
      });
    }
  };

  const startTaskEdit = (milestoneId, task) => {
    setEditingTaskByMilestone((prev) => ({
      ...prev,
      [milestoneId]: {
        taskId: task.id,
        title: task.title,
        status: task.status || "todo",
        assignee: task.assignee ?? task.assignee_id ?? undefined,
      },
    }));
  };

  const cancelTaskEdit = (milestoneId) => {
    setEditingTaskByMilestone((prev) => ({
      ...prev,
      [milestoneId]: null,
    }));
  };

  const handleTaskEditField = (milestoneId, patch) => {
    setEditingTaskByMilestone((prev) => ({
      ...prev,
      [milestoneId]: {
        ...(prev[milestoneId] || {}),
        ...patch,
      },
    }));
  };

  const handleSaveTaskEdit = async (milestone) => {
    if (!selectedProject?.id) return;

    const edit = editingTaskByMilestone[milestone.id];
    if (!edit?.taskId) return;

    try {
      const updatedTask = await updateTask(edit.taskId, {
        title: (edit.title || "").trim(),
        description: "",
        status: edit.status || "todo",
        project: selectedProject.id,
        milestone: milestone.id,
        assignee: edit.assignee || null,
      });

      patchMilestoneById(milestone.id, (existing) => ({
        ...existing,
        tasks: (existing.tasks || []).map((task) =>
          task.id === updatedTask.id ? { ...task, ...updatedTask } : task,
        ),
      }));

      cancelTaskEdit(milestone.id);
      notification.success({ message: "Task Updated", placement: "topRight" });
      await syncSelectedProject();
    } catch (error) {
      notification.error({
        message: "Task Update Failed",
        description: error?.message || "Unable to update task.",
        placement: "topRight",
      });
    }
  };

  const handleTaskStatusChange = async (milestoneId, taskId, statusValue) => {
    try {
      const updated = await updateTaskStatus(taskId, statusValue);
      patchMilestoneById(milestoneId, (existing) => ({
        ...existing,
        tasks: (existing.tasks || []).map((task) =>
          task.id === taskId ? { ...task, ...updated } : task,
        ),
      }));
      await syncSelectedProject();
    } catch (error) {
      notification.error({
        message: "Task Status Update Failed",
        description: error?.message || "Unable to update task status.",
        placement: "topRight",
      });
    }
  };

  const handleDeleteTask = async (milestoneId, taskId) => {
    try {
      await deleteTask(taskId);
      patchMilestoneById(milestoneId, (existing) => ({
        ...existing,
        tasks: (existing.tasks || []).filter((task) => task.id !== taskId),
      }));
      notification.success({ message: "Task Deleted", placement: "topRight" });
      await syncSelectedProject();
    } catch (error) {
      notification.error({
        message: "Task Delete Failed",
        description: error?.message || "Unable to delete task.",
        placement: "topRight",
      });
    }
  };

  return (
    <Card className="project-dashboard-card">
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <Title level={5} style={{ margin: 0, color: "#d9e2dc" }}>
          Milestones
        </Title>
        {isProjectOwner && (
          <Button
            type="primary"
            onClick={() => {
              setEditingMilestone(null);
              form.resetFields();
              form.setFieldsValue({ status: "planned" });
              setIsAddingMilestone(true);
            }}
          >
            Add Milestone
          </Button>
        )}
      </div>

      <div style={{ marginTop: 16, display: "grid", gap: 12 }}>
        {projectMileStones.length === 0 ? (
          <Empty
            description="No milestones yet"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        ) : (
          projectMileStones.map((milestone) => {
            const milestoneSummary = getMilestoneWorkSummary(milestone);
            const taskEdit = editingTaskByMilestone[milestone.id];

            return (
              <div
                key={milestone.id}
                style={{
                  border: "1px solid rgba(255,255,255,0.1)",
                  borderRadius: 10,
                  padding: 14,
                  background: "rgba(255,255,255,0.03)",
                }}
              >
                <Space
                  style={{ display: "flex", justifyContent: "space-between" }}
                  align="start"
                  wrap
                >
                  <div>
                    <Text strong style={{ color: "#fff", fontSize: 16 }}>
                      {milestone.title}
                    </Text>
                    <div style={{ marginTop: 8 }}>
                      <Text style={{ color: "rgba(255,255,255,0.75)" }}>
                        {milestone.start_date} - {milestone.due_date}
                      </Text>
                    </div>
                  </div>

                  {isProjectOwner && (
                    <Space wrap>
                      <Select
                        size="small"
                        value={milestone.status || "planned"}
                        onChange={(value) =>
                          handleMilestoneStatusChange(milestone.id, value)
                        }
                        options={milestoneStatusOptions}
                        style={{ minWidth: 150 }}
                      />
                      <Button
                        size="small"
                        icon={<EditOutlined />}
                        onClick={() => handleEditMilestone(milestone)}
                      >
                        Edit
                      </Button>
                      <Popconfirm
                        title="Delete milestone"
                        description="Delete this milestone and all related tasks?"
                        onConfirm={() => handleDeleteMilestone(milestone.id)}
                        okText="Delete"
                        cancelText="Cancel"
                        okButtonProps={{ danger: true }}
                      >
                        <Button size="small" danger icon={<DeleteOutlined />}>
                          Delete
                        </Button>
                      </Popconfirm>
                    </Space>
                  )}
                </Space>

                <div style={{ marginTop: 10 }}>
                  <Progress
                    percent={milestoneSummary.completionPercent}
                    strokeColor={{ "0%": "#00C9FF", "100%": "#92FE9D" }}
                    trailColor="rgba(255, 255, 255, 0.1)"
                  />
                  <Text
                    style={{
                      color: "rgba(255,255,255,0.68)",
                      display: "block",
                      marginTop: 6,
                    }}
                  >
                    {milestoneSummary.workDone}/{milestoneSummary.totalWork}{" "}
                    tasks completed
                  </Text>
                </div>

                {milestone.teamMembers?.length > 0 && (
                  <Space size={[8, 8]} wrap style={{ marginTop: 10 }}>
                    {milestone.teamMembers.map((teamId) => (
                      <Tag color="cyan" key={`${milestone.id}-${teamId}`}>
                        {teamMemberLabelById.get(teamId) || `Member ${teamId}`}
                      </Tag>
                    ))}
                  </Space>
                )}

                <div style={{ marginTop: 12 }}>
                  <Text style={{ color: "#d9e2dc", fontWeight: 600 }}>
                    Tasks ({milestone.tasks?.length || 0})
                  </Text>

                  <div style={{ display: "grid", gap: 8, marginTop: 8 }}>
                    {(milestone.tasks || []).length === 0 ? (
                      <Text style={{ color: "rgba(255,255,255,0.6)" }}>
                        No tasks yet for this milestone.
                      </Text>
                    ) : (
                      (milestone.tasks || []).map((task, taskIndex) => {
                        const assigneeId = task.assignee ?? task.assignee_id;
                        const assigneeLabel = assigneeId
                          ? teamMemberLabelById.get(assigneeId) ||
                            `Member ${assigneeId}`
                          : "Unassigned";
                        const isEditingTask = taskEdit?.taskId === task.id;

                        return (
                          <div
                            key={task.id || `${milestone.id}-task-${taskIndex}`}
                            style={{
                              display: "grid",
                              gap: 8,
                              border: "1px solid rgba(255,255,255,0.08)",
                              borderRadius: 8,
                              padding: "8px 10px",
                              background: "rgba(255,255,255,0.02)",
                            }}
                          >
                            {isEditingTask ? (
                              <>
                                <Input
                                  value={taskEdit.title}
                                  onChange={(event) =>
                                    handleTaskEditField(milestone.id, {
                                      title: event.target.value,
                                    })
                                  }
                                />
                                <Space wrap>
                                  <Select
                                    value={taskEdit.status || "todo"}
                                    onChange={(status) =>
                                      handleTaskEditField(milestone.id, {
                                        status,
                                      })
                                    }
                                    options={taskStatusOptions}
                                    style={{ minWidth: 140 }}
                                  />
                                  <Select
                                    allowClear
                                    placeholder="Assign member"
                                    value={taskEdit.assignee}
                                    onChange={(assignee) =>
                                      handleTaskEditField(milestone.id, {
                                        assignee,
                                      })
                                    }
                                    options={(milestone.teamMembers || []).map(
                                      (memberId) => ({
                                        value: memberId,
                                        label:
                                          teamMemberLabelById.get(memberId) ||
                                          `Member ${memberId}`,
                                      }),
                                    )}
                                    style={{ minWidth: 170 }}
                                  />
                                  <Button
                                    type="primary"
                                    size="small"
                                    icon={<SaveOutlined />}
                                    onClick={() =>
                                      handleSaveTaskEdit(milestone)
                                    }
                                  >
                                    Save
                                  </Button>
                                  <Button
                                    size="small"
                                    icon={<CloseOutlined />}
                                    onClick={() => cancelTaskEdit(milestone.id)}
                                  >
                                    Cancel
                                  </Button>
                                </Space>
                              </>
                            ) : (
                              <>
                                <Space
                                  style={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                  }}
                                  wrap
                                >
                                  <Text style={{ color: "#fff" }}>
                                    {task.title}
                                  </Text>
                                  <Space>
                                    <Select
                                      size="small"
                                      value={task.status || "todo"}
                                      onChange={(statusValue) =>
                                        handleTaskStatusChange(
                                          milestone.id,
                                          task.id,
                                          statusValue,
                                        )
                                      }
                                      options={taskStatusOptions}
                                      style={{ minWidth: 130 }}
                                    />
                                    {isProjectOwner && (
                                      <>
                                        <Button
                                          size="small"
                                          icon={<EditOutlined />}
                                          onClick={() =>
                                            startTaskEdit(milestone.id, task)
                                          }
                                        >
                                          Edit
                                        </Button>
                                        <Popconfirm
                                          title="Delete task"
                                          description="Are you sure you want to delete this task?"
                                          onConfirm={() =>
                                            handleDeleteTask(
                                              milestone.id,
                                              task.id,
                                            )
                                          }
                                          okText="Delete"
                                          cancelText="Cancel"
                                          okButtonProps={{ danger: true }}
                                        >
                                          <Button
                                            size="small"
                                            danger
                                            icon={<DeleteOutlined />}
                                          >
                                            Delete
                                          </Button>
                                        </Popconfirm>
                                      </>
                                    )}
                                  </Space>
                                </Space>
                                <Tag
                                  color="geekblue"
                                  style={{ width: "fit-content" }}
                                >
                                  {assigneeLabel}
                                </Tag>
                              </>
                            )}
                          </div>
                        );
                      })
                    )}
                  </div>

                  {isProjectOwner && (
                    <div style={{ marginTop: 10 }}>
                      <Button
                        type="dashed"
                        icon={<PlusOutlined />}
                        onClick={() =>
                          setExpandedTaskFormMilestoneId((current) =>
                            current === milestone.id ? null : milestone.id,
                          )
                        }
                      >
                        Add Milestone Task
                      </Button>
                    </div>
                  )}

                  {isProjectOwner &&
                    expandedTaskFormMilestoneId === milestone.id && (
                      <div
                        style={{
                          marginTop: 10,
                          display: "grid",
                          gap: 10,
                          padding: 10,
                          borderRadius: 8,
                          border: "1px solid rgba(255,255,255,0.08)",
                          background: "rgba(0,0,0,0.15)",
                        }}
                      >
                        <Input
                          placeholder="Task title"
                          value={
                            taskDraftsByMilestone[milestone.id]?.title || ""
                          }
                          onChange={(event) =>
                            handleTaskDraftChange(milestone.id, {
                              title: event.target.value,
                            })
                          }
                        />
                        <Space wrap>
                          <Select
                            value={
                              taskDraftsByMilestone[milestone.id]?.status ||
                              "todo"
                            }
                            onChange={(status) =>
                              handleTaskDraftChange(milestone.id, { status })
                            }
                            options={taskStatusOptions}
                            style={{ minWidth: 140 }}
                          />
                          <Select
                            allowClear
                            placeholder="Assign member"
                            value={
                              taskDraftsByMilestone[milestone.id]?.assignee
                            }
                            onChange={(assignee) =>
                              handleTaskDraftChange(milestone.id, {
                                assignee,
                              })
                            }
                            options={(milestone.teamMembers || []).map(
                              (memberId) => ({
                                value: memberId,
                                label:
                                  teamMemberLabelById.get(memberId) ||
                                  `Member ${memberId}`,
                              }),
                            )}
                            style={{ minWidth: 170 }}
                          />
                        </Space>
                        <Space>
                          <Button
                            type="primary"
                            onClick={() => handleAddTask(milestone)}
                          >
                            Save Task
                          </Button>
                          <Button
                            onClick={() => {
                              setExpandedTaskFormMilestoneId(null);
                              setTaskDraftsByMilestone((prev) => ({
                                ...prev,
                                [milestone.id]: {
                                  title: "",
                                  status: "todo",
                                  assignee: undefined,
                                },
                              }));
                            }}
                          >
                            Cancel
                          </Button>
                        </Space>
                      </div>
                    )}
                </div>
              </div>
            );
          })
        )}
      </div>

      {isProjectOwner && isAddingMilestone && (
        <Form
          form={form}
          onFinish={handleMilestoneSubmit}
          layout="vertical"
          style={{ marginTop: 20 }}
          initialValues={{ status: "planned" }}
        >
          <Form.Item
            name="title"
            label="Milestone Title"
            rules={[
              { required: true, message: "Please enter a milestone title" },
            ]}
          >
            <Input placeholder="Milestone Name" size="large" />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <Input.TextArea rows={3} placeholder="Optional details" />
          </Form.Item>
          <Form.Item
            name="dates"
            label="Milestone Timeline (Start & Due Date)"
            rules={[
              { required: true, message: "Please select start and due dates" },
            ]}
          >
            <RangePicker
              style={{ width: "100%" }}
              popupClassName="glass-dropdown"
              size="large"
            />
          </Form.Item>
          <Form.Item
            name="status"
            label="Milestone Status"
            rules={[
              { required: true, message: "Please choose milestone status" },
            ]}
          >
            <Select options={milestoneStatusOptions} size="large" />
          </Form.Item>
          {teamMembers.length > 0 && (
            <Form.Item label="Team Member(s) for Milestone" name="teamMembers">
              <Select
                mode="multiple"
                placeholder="Assign team members"
                options={teamMembers.map((tm) => ({
                  label:
                    `${tm.user?.first_name || tm.user?.username || "User"} ${tm.user?.last_name || ""}`.trim(),
                  value: tm.id,
                }))}
                size="large"
              />
            </Form.Item>
          )}
          <Space>
            <Button htmlType="submit" type="primary">
              {editingMilestone ? "Update Milestone" : "Save Milestone"}
            </Button>
            <Button
              onClick={() => {
                form.resetFields();
                setIsAddingMilestone(false);
                setEditingMilestone(null);
              }}
            >
              Cancel
            </Button>
          </Space>
        </Form>
      )}
    </Card>
  );
}

export default MilestoneCard;
