import React, { useState, useEffect, useCallback } from "react";
import {
  Modal,
  Form,
  Input,
  Button,
  DatePicker,
  Select,
  notification,
} from "antd";
import "./ProjectFormModal.css";
import dayjs from "dayjs";
import { useDispatch } from "react-redux";
import {
  createProjectThunk,
  updateProjectThunk,
} from "../../Services/ProjectSlice";

const { TextArea } = Input;
const { RangePicker } = DatePicker;

export default function ProjectFormModal({
  isOpen,
  onClose,
  userList,
  isCreated = true,
  record = null,
  onSuccess,
}) {
  const dispatch = useDispatch();
  const [form] = Form.useForm();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [userOptions, setUserOptions] = useState([]);
  const [searchText, setSearchText] = useState("");

  const normalizeTeamMemberIds = useCallback(
    (members = []) => {
      if (!Array.isArray(members) || !Array.isArray(userList)) return [];

      const byUsername = new Map(
        userList.map((u) => [String(u.username || "").toLowerCase(), u.id]),
      );
      const byFullName = new Map(
        userList.map((u) => [
          `${u.first_name || ""} ${u.last_name || ""}`.trim().toLowerCase(),
          u.id,
        ]),
      );

      const resolved = members
        .map((member) => {
          if (member?.user?.id != null) return member.user.id;
          if (typeof member?.user === "number") return member.user;
          if (typeof member === "number") return member;

          const labelCandidate =
            (typeof member?.user === "string" && member.user) ||
            member?.name ||
            member?.username ||
            (typeof member === "string" ? member : null);

          if (!labelCandidate) return null;

          const key = labelCandidate.trim().toLowerCase();
          return byUsername.get(key) ?? byFullName.get(key) ?? null;
        })
        .filter((id) => id != null);

      return [...new Set(resolved)];
    },
    [userList],
  );

  useEffect(() => {
    if (userList && userList.length > 0) {
      setUserOptions(
        userList.map((user) => ({
          label: `${user.first_name} ${user.last_name} (${user.username})`,
          value: user.id,
        })),
      );
    }
  }, [userList]);

  useEffect(() => {
    if (isOpen) {
      if (!isCreated && record) {
        const normalizedTeamMembers = normalizeTeamMemberIds(
          record.teamMembers,
        );
        if (
          Array.isArray(record.teamMembers) &&
          normalizedTeamMembers.length < record.teamMembers.length
        ) {
          notification.warning({
            message: "Some team members need re-selection",
            description:
              "A few previous team members could not be matched to user IDs. Please review Team Members before saving.",
          });
        }

        form.setFieldsValue({
          projectName: record.project_name,
          description: record.project_description,
          status: record.status,
          progress: record.progress,
          dates: [dayjs(record.start_date), dayjs(record.due_date)],
          teamMembers: normalizedTeamMembers,
        });
      } else {
        form.resetFields();
      }
    }
  }, [isOpen, isCreated, record, form, normalizeTeamMemberIds]);

  const selectedIds = Form.useWatch("teamMembers", form) || [];

  const filteredOptions = userOptions.filter(
    (opt) =>
      selectedIds.includes(opt.value) ||
      (searchText &&
        opt.label.toLowerCase().includes(searchText.toLowerCase())),
  );

  const onFinish = async (values) => {
    setIsSubmitting(true);
    try {
      const payload = {
        project_name: values.projectName,
        project_description: values.description,
        status: values?.status ?? "active",
        progress: values?.progress ?? 0,
        start_date: values.dates[0].format("YYYY-MM-DD"),
        due_date: values.dates[1].format("YYYY-MM-DD"),
        team_members: values.teamMembers,
      };

      if (isCreated) {
        const newProject = await dispatch(createProjectThunk(payload));
        notification.success({
          message: "Project Created",
          description: `${values.projectName} was successfully created.`,
        });
        if (onSuccess) onSuccess(newProject, "create");
      } else {
        const updatedProject = await dispatch(
          updateProjectThunk({ projectId: record.id, projectData: payload }),
        );

        notification.success({
          message: "Project Updated",
          description: `${values.projectName} was successfully updated.`,
        });

        if (onSuccess) onSuccess(updatedProject, "update");
      }

      form.resetFields();
      onClose();
    } catch (error) {
      console.error("Project Form Error:", error);
      let errorMessage = "Ensure all fields are correctly formatted.";

      if (error.message) {
        try {
          const parsedError = JSON.parse(error.message);
          if (typeof parsedError === "object") {
            errorMessage = Object.entries(parsedError)
              .map(([field, msgs]) => `${field}: ${msgs.join(", ")}`)
              .join(" | ");
          } else {
            errorMessage = error.message;
          }
        } catch {
          errorMessage = error.message;
        }
      }

      notification.error({
        message: isCreated ? "Creation Failed" : "Update Failed",
        description: errorMessage,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal
      title={isCreated ? "Create New Project" : "Update Project"}
      width={520}
      onCancel={onClose}
      open={isOpen}
      footer={null}
      centered
      maskStyle={{
        backgroundColor: "rgba(4, 10, 20, 0.45)",
        backdropFilter: "blur(14px)",
        WebkitBackdropFilter: "blur(14px)",
      }}
      className="glass-modal project-form-modal"
      styles={{
        content: {
          background:
            "linear-gradient(180deg, rgba(30, 32, 35, 0.94) 0%, rgba(19, 20, 22, 0.92) 100%)",
          backdropFilter: "blur(28px)",
          WebkitBackdropFilter: "blur(28px)",
          border: "1px solid rgba(255, 255, 255, 0.1)",
          boxShadow: "0 24px 80px rgba(0, 0, 0, 0.55)",
          color: "#fff",
          borderRadius: "16px",
          height: "80vh",
          maxHeight: "80vh",
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
        },
        header: {
          background: "transparent",
          borderBottom: "1px solid rgba(255, 255, 255, 0.12)",
          paddingBottom: "18px",
          marginBottom: "18px",
        },
        body: {
          background: "transparent",
          color: "#fff",
          flex: 1,
          minHeight: 0,
          overflow: "hidden",
          display: "flex",
        },
      }}
    >
      <Form
        layout="vertical"
        form={form}
        onFinish={onFinish}
        className="project-form-modal__form"
        initialValues={{
          status: "active",
          progress: 0,
        }}
      >
        <div className="project-form-modal__scroll-area">
          <Form.Item
            name="projectName"
            label="Project Name"
            rules={[
              { required: true, message: "Please enter the project name" },
            ]}
          >
            <Input placeholder="E.g., TrackPro UI Development" size="large" />
          </Form.Item>

          <Form.Item
            name="description"
            label="Description"
            rules={[
              { required: true, message: "Please enter a brief description" },
            ]}
          >
            <TextArea
              rows={4}
              placeholder="What is the objective of this project?"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="dates"
            label="Project Timeline (Start & Due Date)"
            rules={[
              { required: true, message: "Please select start and due dates" },
            ]}
          >
            <RangePicker
              style={{ width: "100%" }}
              popupClassName="glass-dropdown"
              disabledDate={(current) =>
                current && current < dayjs().startOf("day")
              }
              size="large"
            />
          </Form.Item>

          <Form.Item name="teamMembers" label="Team Members" rules={[]}>
            <Select
              mode="multiple"
              showSearch
              placeholder="Search team members by name or username"
              popupClassName="glass-dropdown"
              options={filteredOptions}
              onSearch={(value) => setSearchText(value)}
              filterOption={false}
              notFoundContent={
                searchText ? "No users found" : "Type to search users..."
              }
              style={{ width: "100%" }}
              size="large"
              onBlur={() => setSearchText("")}
            />
          </Form.Item>
        </div>

        <div
          className="modal-footer-actions"
          style={{
            textAlign: "right",
            marginTop: 24,
            borderTop: "1px solid rgba(255,255,255,0.1)",
            paddingTop: 16,
          }}
        >
          <Button
            onClick={onClose}
            style={{ marginRight: 12 }}
            className="glass-cancel-btn"
            size="large"
          >
            Cancel
          </Button>
          <Button
            type="primary"
            htmlType="submit"
            loading={isSubmitting}
            className="glass-submit-btn"
            size="large"
          >
            {isCreated ? "Create Project" : "Update Project"}
          </Button>
        </div>
      </Form>
    </Modal>
  );
}
