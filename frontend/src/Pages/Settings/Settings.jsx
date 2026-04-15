import { Form, Input } from "antd";

export default function Settings() {
  return (
    <Form>
      <Form.Item
        label="Username"
        name={"username"}
        rules={[
          {
            required: true,
            message: "Please Enter Username",
          },
        ]}
      >
        <Input placeholder="username" size="large" />
      </Form.Item>
      <Form.Item></Form.Item>
    </Form>
  );
}
