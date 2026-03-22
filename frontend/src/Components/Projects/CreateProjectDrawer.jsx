import React, { useState } from "react";
import { Drawer, Form, Input, Button, DatePicker, Select, InputNumber, notification } from "antd";
import "./CreateProjectDrawer.css";

const { Option } = Select;
const { TextArea } = Input;
const { RangePicker } = DatePicker;

export default function CreateProjectDrawer({ isOpen, onClose }) {
  const [form] = Form.useForm();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (values) => {
    setIsSubmitting(true);
    try {
      // Mock saving logic - we will connect to backend API here later.
      const payload = {
        project_name: values.projectName,
        project_description: values.description,
        status: values.status,
        progress: values.progress || 0,
        start_date: values.dates[0].format("YYYY-MM-DD"),
        due_date: values.dates[1].format("YYYY-MM-DD"),
      };

      console.log("Submitting Project Data:", payload);
      
      notification.success({
        message: 'Project Created',
        description: `${values.projectName} was successfully created.`,
      });
      
      form.resetFields();
      onClose();
    } catch (error) {
      notification.error({
        message: 'Creation Failed',
        description: 'Ensure all fields are correctly formatted.',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Drawer
      title="Create New Project"
      width={480}
      onClose={onClose}
      open={isOpen}
      rootClassName="create-drawer"
      styles={{
        body: { paddingBottom: 80 }
      }}
    >
      <Form
        layout="vertical"
        form={form}
        onFinish={handleSubmit}
        initialValues={{
          status: 'active',
          progress: 0
        }}
      >
        <Form.Item
          name="projectName"
          label="Project Name"
          rules={[{ required: true, message: "Please enter the project name" }]}
        >
          <Input placeholder="E.g., TrackPro UI Development" />
        </Form.Item>

        <Form.Item
          name="description"
          label="Description"
          rules={[{ required: true, message: "Please enter a brief description" }]}
        >
          <TextArea rows={4} placeholder="What is the objective of this project?" />
        </Form.Item>

        <Form.Item
          name="status"
          label="Status"
          rules={[{ required: true, message: "Please select a status" }]}
        >
          <Select placeholder="Select Status">
            <Option value="active">Active</Option>
            <Option value="on_track">On Track</Option>
            <Option value="at_risk">At Risk</Option>
            <Option value="complete">Complete</Option>
          </Select>
        </Form.Item>

        <Form.Item
          name="dates"
          label="Project Timeline (Start & Due Date)"
          rules={[{ required: true, message: "Please select start and due dates" }]}
        >
          <RangePicker style={{ width: '100%' }} />
        </Form.Item>

        <Form.Item
          name="progress"
          label="Initial Progress %"
          rules={[
            { type: "number", min: 0, max: 100, message: "Must be between 0 and 100" }
          ]}
        >
          <InputNumber min={0} max={100} style={{ width: '100%' }} />
        </Form.Item>

        <div style={{ textAlign: "right" }}>
          <Button onClick={onClose} style={{ marginRight: 8 }}>
            Cancel
          </Button>
          <Button type="primary" htmlType="submit" loading={isSubmitting}>
            Submit
          </Button>
        </div>
      </Form>
    </Drawer>
  );
}
