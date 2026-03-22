import { Link, useNavigate } from "react-router-dom";
import { Form, Input, Button, Typography, notification, Row, Col } from "antd";
import { UserOutlined, MailOutlined, LockOutlined } from "@ant-design/icons";
import { registerUser } from "../../Services/userServices";
import "./SignUp.css";
import { useState } from "react";

const { Title, Text } = Typography;

export function SignUp() {
  const [api, contextHolder] = notification.useNotification();
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false)

  const onFinish = async (values) => {
    setIsLoading(true)
    try {
      const response = await registerUser(values);
      api.success({
        message: "Success",
        description: "Account created successfully!",
        duration: 3,
        placement: "topRight",
      });
      form.resetFields();
      setTimeout(() => {
        setIsLoading(false)
        navigate("/login")
      }, 1000);
    } catch (error) {
      api.error({
        message: "Registration Failed",
        description: error.message || "Failed to create account. Please try again.",
        duration: 4,
        placement: "topRight",
      });
    }
  };

  return (
    <div className="signup-container">
      {contextHolder}
      <div className="signup-card">
        <div className="signup-header">
          <Title level={2} className="signup-title">
            Create Account
          </Title>
          <Text className="signup-subtitle">
            Join the platform and start managing projects today.
          </Text>
        </div>

        <Form
          form={form}
          name="signup-form"
          layout="vertical"
          onFinish={onFinish}
          autoComplete="off"
          className="signup-form"
          size="large"
        >
          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item
                name="firstName"
                rules={[
                  { required: true, message: "Please Enter your first name" },
                  {
                    pattern: /^[a-zA-Z]+$/,
                    message: "first name only contain letters",
                  },
                ]}
              >
                <Input placeholder="First Name" />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item
                name="lastName"
                rules={[
                  { required: true, message: "Please enter your last name" },
                  {
                    pattern: /^[a-zA-Z]+$/,
                    message: "last name only contain letters",
                  },
                ]}
              >
                <Input placeholder="Last Name" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item
                name="username"
                rules={[
                  { required: true, message: "Please enter your username!" },
                  { min: 3, message: "Username must be at least 3 characters!" },
                  { max: 20, message: "Username cannot exceed 20 characters!" },
                  {
                    pattern: /^[a-zA-Z0-9_]+$/,
                    message: "Username can only contain letters, numbers, and underscores!",
                  },
                ]}
              >
                <Input prefix={<UserOutlined />} placeholder="Username" />
              </Form.Item>
            </Col>

            <Col xs={24} md={12}>
              <Form.Item
                name="email"
                rules={[
                  { required: true, message: "Please enter your email!" },
                  {
                    type: "email",
                    message: "Please enter a valid email address!",
                  },
                ]}
              >
                <Input prefix={<MailOutlined />} placeholder="Email Address" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col xs={24} md={12}>
              <Form.Item
                name="password"
                rules={[
                  { required: true, message: "Please enter your password!" },
                  { min: 8, message: "Password must be at least 8 characters long!" },
                  {
                    pattern: /(?=.*[A-Za-z])(?=.*\d)/,
                    message: "Password must contain at least one letter and one number!",
                  },
                ]}
                hasFeedback
              >
                <Input.Password prefix={<LockOutlined />} placeholder="Password" />
              </Form.Item>
            </Col>
            <Col xs={24} md={12}>
              <Form.Item
                name="confirmPassword"
                dependencies={["password"]}
                rules={[
                  { required: true, message: "Please enter your password!" },
                  { min: 8, message: "Password must be at least 8 characters long!" },
                  ({ getFieldValue }) => ({
                    validator(_, value) {
                      if (!value || getFieldValue("password") === value) {
                        return Promise.resolve();
                      }
                      return Promise.reject(
                        new Error("Confirm Password not equal to Password you enterd above")
                      );
                    },
                  }),
                ]}
                hasFeedback
              >
                <Input.Password placeholder="Confirm Password" prefix={<LockOutlined />} />
              </Form.Item>
            </Col>
          </Row>
          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              className="signup-button"
              block
              loading={isLoading}
            >
              Sign Up
            </Button>
          </Form.Item>
        </Form>

        <div className="signup-footer">
          <Text>Already have an account?</Text>
          <Link to="/login">
            Log in
          </Link>
        </div>
      </div>
    </div>
  );
}