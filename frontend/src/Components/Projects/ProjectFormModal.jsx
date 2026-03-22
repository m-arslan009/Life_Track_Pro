import React, { useState, useEffect } from "react";
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
import { createProject, updateProject } from "../../Services/projectServices";

const { TextArea } = Input;
const { RangePicker } = DatePicker;

export default function ProjectFormModal({ 
  isOpen, 
  onClose, 
  userList, 
  isCreated = true, 
  record = null,
  onSuccess 
}) {
  const [form] = Form.useForm();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [userOptions, setUserOptions] = useState([]);
  const [searchText, setSearchText] = useState("");

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
        form.setFieldsValue({
          projectName: record.project_name,
          description: record.project_description,
          status: record.status,
          progress: record.progress,
          dates: [dayjs(record.start_date), dayjs(record.due_date)],
          teamMembers: record.teamMembers?.map(m => m.user.id) || []
        });
      } else {
        form.resetFields();
      }
    }
  }, [isOpen, isCreated, record, form]);

  const selectedIds = Form.useWatch("teamMembers", form) || [];
  
  // To satisfy "only show when search" while keeping labels for selected items:
  // We include items that are either:
  // 1. Currently selected (so their labels are visible in the box)
  // 2. Matching the search text (to satisfy the search requirement)
  const filteredOptions = userOptions.filter(opt => 
    selectedIds.includes(opt.value) || 
    (searchText && opt.label.toLowerCase().includes(searchText.toLowerCase()))
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
        const newProject = await createProject(payload);
        notification.success({
          message: "Project Created",
          description: `${values.projectName} was successfully created.`,
        });
        if (onSuccess) onSuccess(newProject, 'create');
      } else {
        // Commenting out update logic as requested
        // const updatedProject = await updateProject(record.id, payload);
        
        notification.success({
          message: "Project Updated",
          description: `${values.projectName} was successfully updated.`,
        });
        
        // if (onSuccess) onSuccess(updatedProject, 'update');
      }

      form.resetFields();
      onClose();
    } catch (error) {
      console.error("Project Form Error:", error);
      let errorMessage = "Ensure all fields are correctly formatted.";
      
      if (error.message) {
        try {
          const parsedError = JSON.parse(error.message);
          if (typeof parsedError === 'object') {
            errorMessage = Object.entries(parsedError)
              .map(([field, msgs]) => `${field}: ${msgs.join(", ")}`)
              .join(" | ");
          } else {
            errorMessage = error.message;
          }
        } catch (e) {
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
      className="glass-modal project-form-modal"
      styles={{
        content: {
          background: "rgba(255, 255, 255, 0.05)",
          backdropFilter: "blur(24px)",
          WebkitBackdropFilter: "blur(24px)",
          border: "1px solid rgba(255, 255, 255, 0.1)",
          boxShadow: "0 12px 40px rgba(0, 0, 0, 0.5)",
          color: "#fff",
          borderRadius: "16px",
        },
        header: {
          background: "transparent",
          borderBottom: "1px solid rgba(255, 255, 255, 0.1)",
          paddingBottom: "16px",
          marginBottom: "24px",
        },
        body: {
          background: "rgba(255, 255, 255, 0.05)",
          color: "#fff",
        },
      }}
    >
      <Form
        layout="vertical"
        form={form}
        onFinish={onFinish}
        initialValues={{
          status: "active",
          progress: 0,
        }}
      >
        <Form.Item
          name="projectName"
          label="Project Name"
          rules={[{ required: true, message: "Please enter the project name" }]}
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
            notFoundContent={searchText ? "No users found" : "Type to search users..."}
            style={{ width: "100%" }}
            size="large"
            onBlur={() => setSearchText("")}
          />
        </Form.Item>

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
