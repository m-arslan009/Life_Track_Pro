import {
  Descriptions,
  Tag,
  Progress,
  Divider,
  Table,
  Button,
  Card,
  Typography,
  Space,
} from "antd";
import { DeleteOutlined } from "@ant-design/icons";
import "./ProjectDetailDrawer.css";
import { useSelector } from "react-redux";
import { getSelectedProject } from "../../Services/ProjectSlice";
import { getProjectWorkSummary } from "../../Utils/projectProgress";

const { Title, Text } = Typography;

function OverviewCard() {
  const project = useSelector(getSelectedProject);

  if (!project) return null;

  const progressSummary = getProjectWorkSummary(project);
  const progressPercent = progressSummary.completionPercent;

  const teamColumns = [
    {
      title: "Name",
      key: "fullName",
      render: (_, record) => (
        <span className="team-name">
          {record.user.first_name || record.user.username}{" "}
          {record.user.last_name || ""}
        </span>
      ),
    },
    {
      title: "Username",
      key: "username",
      render: (_, record) => (
        <Text type="secondary">@{record.user.username}</Text>
      ),
    },
    {
      title: "Email",
      key: "email",
      render: (_, record) => record.user.email,
    },
    {
      title: "Role",
      dataIndex: "role",
      key: "role",
      render: (role) => <Tag color="cyan">{role}</Tag>,
    },
    {
      title: "Action",
      key: "action",
      render: (_, record) => (
        <Button
          type="text"
          danger
          icon={<DeleteOutlined />}
          onClick={() => console.log("Delete logic for", record.id)}
        />
      ),
    },
  ];

  return (
    <Card className="project-dashboard-card">
      <div className="drawer-header-content">
        <Title level={2} className="detail-title">
          {project.project_name}
        </Title>
        <Text type="secondary" className="detail-subtitle">
          ID: {project.id}
        </Text>
      </div>

      <Divider />

      <Descriptions
        column={{ xs: 1, sm: 2 }}
        bordered
        size="middle"
        labelStyle={{
          backgroundColor: "rgba(255, 255, 255, 0.04)",
          color: "rgba(255, 255, 255, 0.6)",
        }}
        contentStyle={{ backgroundColor: "transparent", color: "#fff" }}
      >
        <Descriptions.Item label="Current Status">
          {project.status === "active" && <Tag color="blue">Active</Tag>}
          {project.status === "on_track" && <Tag color="green">On Track</Tag>}
          {project.status === "at_risk" && <Tag color="red">At Risk</Tag>}
          {project.status === "complete" && <Tag color="gold">Complete</Tag>}
        </Descriptions.Item>
        <Descriptions.Item label="Start Date">
          {project.start_date}
        </Descriptions.Item>
        <Descriptions.Item label="Due Date">
          {project.due_date}
        </Descriptions.Item>
      </Descriptions>

      <div className="section-spacer">
        <Title level={5} className="section-title">
          Progress Analysis
        </Title>
        <div className="progress-summary-grid">
          <div className="progress-summary-card">
            <Text className="progress-summary-label">Project Progress</Text>
            <Progress
              percent={progressPercent}
              type="circle"
              strokeColor={{ "0%": "#00C9FF", "100%": "#92FE9D" }}
              railColor="rgba(255, 255, 255, 0.1)"
            />
          </div>
          <div className="progress-summary-card progress-summary-copy">
            <Text className="progress-summary-stat">
              {progressSummary.workDone}/{progressSummary.totalWork}
            </Text>
            <Text type="secondary">
              Work done over total work across all milestones.
            </Text>
            <Divider
              style={{
                margin: "12px 0",
                borderColor: "rgba(255,255,255,0.08)",
              }}
            />
            <Space wrap>
              <Tag color="cyan">
                {progressSummary.totalMilestones} Milestones
              </Tag>
              <Tag color="green">
                {progressSummary.completedMilestones} Completed
              </Tag>
              <Tag color="gold">
                {progressSummary.remainingWork} Remaining Work
              </Tag>
            </Space>
          </div>
        </div>
      </div>

      <div className="section-spacer">
        <Title level={5} className="section-title">
          Project Overview
        </Title>
        <div className="project-description-box">
          <Text>
            {project.project_description ||
              "No description provided for this project."}
          </Text>
        </div>
      </div>

      <div className="section-spacer">
        <Title level={5} className="section-title">
          Team Members
        </Title>
        <Table
          columns={teamColumns}
          dataSource={project.teamMembers || []}
          rowKey="id"
          pagination={false}
          className="custom-table team-table"
          scroll={{ x: "max-content" }}
        />
      </div>
    </Card>
  );
}

export default OverviewCard;
