import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Form, Input, Button, Typography, notification, Spin } from "antd";
import { UserOutlined, LockOutlined } from "@ant-design/icons";
import { loginUser } from "../../Services/userServices";
import "./Login.css";

const { Title, Text } = Typography;

export function Login() {
  const [api, contextHolder] = notification.useNotification();
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false)

  const onFinish = async (values) => {
    setIsLoading(true)
    try {
      const response = await loginUser(values.username, values.password);
      // loginUser throws an error if authentication fails
      api.success({
        message: "Welcome Back",
        description: "You have successfully logged in!",
        duration: 3,
        placement: "topRight",
      });
      setTimeout(() => {
        navigate("/dashboard")
      }, 1500);
      // Optionally route to dashboard here:
      // navigate("/dashboard");
    } catch (error) {
      api.error({
        message: "Login Failed",
        description: error.message || "Invalid username or password.",
        duration: 4,
        placement: "topRight",
      });
    } finally {
        setIsLoading(false)
        form.resetFields()
    }
  };

  return (
    <div className="login-container">
      {contextHolder}
      <div className="login-card">
        <div className="login-header">
          <Title level={2} className="login-title">
            Welcome Back
          </Title>
          <Text className="login-subtitle">
            Log in to continue managing your projects.
          </Text>
        </div>

        <Form
          form={form}
          name="login-form"
          layout="vertical"
          onFinish={onFinish}
          autoComplete="off"
          className="login-form"
          size="large"
        >
          <Form.Item
            name="username"
            rules={[
              { required: true, message: "Please enter your username!" },
            ]}
          >
            <Input prefix={<UserOutlined />} placeholder="Username" />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: "Please enter your password!" },
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="Password" />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              className="login-button"
              block
              loading={isLoading}
            >
              Log In
            </Button>
          </Form.Item>
        </Form>

        <div className="login-footer">
          <Text>Don't have an account?</Text>
          <Link to="/signup">
            Sign up
          </Link>
        </div>
      </div>
    </div>
  );
}
