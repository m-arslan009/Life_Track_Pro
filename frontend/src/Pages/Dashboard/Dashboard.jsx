import { useEffect, useMemo, useState } from "react";
import {
    Button,
    Card,
    Col,
    Empty,
    Progress,
    Row,
    Skeleton,
    Space,
    Statistic,
    Tag,
    Typography,
    notification,
} from "antd";
import {
    CalendarOutlined,
    ExclamationCircleOutlined,
    EyeOutlined,
    FundProjectionScreenOutlined,
    RocketOutlined,
    WarningOutlined,
} from "@ant-design/icons";
import { useDispatch } from "react-redux";
import ProjectDashboard from "../../Components/Projects/ProjectDashboard";
import {
    fetchProjects,
    setSelectedProject,
} from "../../Services/ProjectSlice";
import { getProjectDashboardOverview } from "../../Services/dashboardServices";
import "./Dashboard.css";

const { Title, Text, Paragraph } = Typography;

const statusConfig = {
    active: {
        label: "Active",
        color: "blue",
    },
    on_track: {
        label: "On Track",
        color: "green",
    },
    at_risk: {
        label: "At Risk",
        color: "red",
    },
};

const formatDate = (value) => {
    if (!value) return "N/A";
    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) return value;
    return parsed.toLocaleDateString();
};

const formatDaysRemaining = (daysRemaining) => {
    if (daysRemaining == null) return "No due date";
    if (daysRemaining < 0) {
        const absoluteDays = Math.abs(daysRemaining);
        return `${absoluteDays} day${absoluteDays === 1 ? "" : "s"} overdue`;
    }
    if (daysRemaining === 0) return "Due today";
    return `${daysRemaining} day${daysRemaining === 1 ? "" : "s"} left`;
};

export default function Dashboard() {
    const dispatch = useDispatch();
    const [overview, setOverview] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isProjectDashboardOpen, setIsProjectDashboardOpen] = useState(false);

    const loadOverview = async () => {
        setIsLoading(true);
        try {
            const data = await getProjectDashboardOverview();
            setOverview(data);
        } catch (error) {
            notification.error({
                message: "Unable to load dashboard",
                description:
                    error?.message ||
                    "Failed to load active projects. Ensure backend is running.",
                placement: "topRight",
            });
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        loadOverview();
    }, []);

    const activeProjects = overview?.active_projects || [];
    const summary = overview?.summary || {};

    const heroStats = useMemo(
        () => [
            {
                key: "active",
                title: "Active Projects",
                value: summary.active_projects || 0,
                icon: <RocketOutlined />,
            },
            {
                key: "track",
                title: "On Track",
                value: summary.on_track_projects || 0,
                icon: <FundProjectionScreenOutlined />,
            },
            {
                key: "risk",
                title: "At Risk",
                value: summary.at_risk_projects || 0,
                icon: <WarningOutlined />,
            },
            {
                key: "due",
                title: "Due This Week",
                value: summary.due_this_week || 0,
                icon: <CalendarOutlined />,
            },
        ],
        [summary],
    );

    const handleOpenProject = async (projectId) => {
        try {
            const allProjects = await dispatch(fetchProjects());
            const targetProject = (allProjects || []).find((p) => p.id === projectId);

            if (!targetProject) {
                notification.warning({
                    message: "Project Not Found",
                    description: "This project is no longer available.",
                    placement: "topRight",
                });
                return;
            }

            dispatch(setSelectedProject(targetProject));
            setIsProjectDashboardOpen(true);
        } catch (error) {
            notification.error({
                message: "Unable to open project",
                description: error?.message || "Failed to load project details.",
                placement: "topRight",
            });
        }
    };

    return (
        <div className="dashboard-page">
            <div className="dashboard-hero">
                <div>
                    <Title level={2} className="dashboard-title">
                        Project Dashboard
                    </Title>
                    <Paragraph className="dashboard-subtitle">
                        Overview of all active projects with quick access to detailed
                        project workspaces.
                    </Paragraph>
                </div>
                <Button onClick={loadOverview} className="dashboard-refresh-btn">
                    Refresh
                </Button>
            </div>

            <Row gutter={[16, 16]}>
                {heroStats.map((item) => (
                    <Col xs={24} sm={12} lg={6} key={item.key}>
                        <Card className="dashboard-stat-card" bordered={false}>
                            <Space className="dashboard-stat-head">
                                <span className="dashboard-stat-icon">{item.icon}</span>
                                <Text className="dashboard-stat-title">{item.title}</Text>
                            </Space>
                            <Statistic value={item.value} valueStyle={{ color: "#ffffff" }} />
                        </Card>
                    </Col>
                ))}
            </Row>

            <Card className="dashboard-list-card" bordered={false}>
                <div className="dashboard-list-head">
                    <Title level={4} className="dashboard-list-title">
                        Active Projects
                    </Title>
                    <Tag color="magenta">{activeProjects.length} visible</Tag>
                </div>

                {isLoading ? (
                    <Space direction="vertical" size={16} className="dashboard-skeleton-wrap">
                        <Skeleton active paragraph={{ rows: 3 }} />
                        <Skeleton active paragraph={{ rows: 3 }} />
                    </Space>
                ) : activeProjects.length === 0 ? (
                    <Empty
                        description="No active projects found. Create or reactivate a project to see it here."
                        image={Empty.PRESENTED_IMAGE_SIMPLE}
                    />
                ) : (
                    <div className="dashboard-project-grid">
                        {activeProjects.map((project) => {
                            const statusMeta = statusConfig[project.status] || {
                                label: project.status,
                                color: "default",
                            };

                            return (
                                <Card key={project.id} className="dashboard-project-card" bordered={false}>
                                    <div className="dashboard-project-header">
                                        <div>
                                            <Title level={5} className="dashboard-project-title">
                                                {project.project_name}
                                            </Title>
                                            <Text className="dashboard-project-owner">
                                                Owner: {project.owner_name}
                                            </Text>
                                        </div>
                                        <Tag color={statusMeta.color}>{statusMeta.label}</Tag>
                                    </div>

                                    <Paragraph className="dashboard-project-description" ellipsis={{ rows: 2 }}>
                                        {project.project_description ||
                                            "No description provided for this project."}
                                    </Paragraph>

                                    <div className="dashboard-progress-wrap">
                                        <div className="dashboard-progress-copy">
                                            <Text>Progress</Text>
                                            <Text>{project.progress}%</Text>
                                        </div>
                                        <Progress
                                            percent={project.progress || 0}
                                            strokeColor={{ "0%": "#22d3ee", "100%": "#34d399" }}
                                            trailColor="rgba(255, 255, 255, 0.12)"
                                            size="small"
                                        />
                                    </div>

                                    <div className="dashboard-meta-grid">
                                        <div>
                                            <Text type="secondary">Milestones</Text>
                                            <div>
                                                {project.completed_milestones}/{project.milestone_count}
                                            </div>
                                        </div>
                                        <div>
                                            <Text type="secondary">Tasks</Text>
                                            <div>
                                                {project.completed_tasks}/{project.task_count}
                                            </div>
                                        </div>
                                        <div>
                                            <Text type="secondary">Team</Text>
                                            <div>{project.team_size}</div>
                                        </div>
                                        <div>
                                            <Text type="secondary">Due Date</Text>
                                            <div>{formatDate(project.due_date)}</div>
                                        </div>
                                    </div>

                                    <div className="dashboard-card-footer">
                                        <Space>
                                            {project.is_overdue && (
                                                <Tag icon={<ExclamationCircleOutlined />} color="error">
                                                    {formatDaysRemaining(project.days_remaining)}
                                                </Tag>
                                            )}
                                            {!project.is_overdue && (
                                                <Text className="dashboard-due-copy">
                                                    {formatDaysRemaining(project.days_remaining)}
                                                </Text>
                                            )}
                                        </Space>
                                        <Button
                                            type="primary"
                                            icon={<EyeOutlined />}
                                            className="dashboard-open-btn"
                                            onClick={() => handleOpenProject(project.id)}
                                        >
                                            Open Details
                                        </Button>
                                    </div>
                                </Card>
                            );
                        })}
                    </div>
                )}
            </Card>

            <ProjectDashboard
                isOpen={isProjectDashboardOpen}
                onClose={() => setIsProjectDashboardOpen(false)}
            />
        </div>
    );
}