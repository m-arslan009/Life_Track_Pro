import { useEffect, useMemo, useState } from "react";
import {
    Alert,
    Button,
    Card,
    Col,
    Empty,
    Progress,
    Row,
    Skeleton,
    Space,
    Tag,
    Typography,
    notification,
} from "antd";
import {
    BarChartOutlined,
    CheckCircleOutlined,
    ExclamationCircleOutlined,
    FundProjectionScreenOutlined,
    ReloadOutlined,
    RiseOutlined,
} from "@ant-design/icons";
import { useDispatch } from "react-redux";
import ProjectDashboard from "../../Components/Projects/ProjectDashboard";
import {
    fetchProjects,
    setSelectedProject,
} from "../../Services/ProjectSlice";
import { getReportsOverview } from "../../Services/reportsServices";
import "./Reports.css";

const { Title, Text, Paragraph } = Typography;

const severityColorMap = {
    high: "red",
    medium: "orange",
    low: "blue",
};

const statusColorMap = {
    active: "blue",
    on_track: "green",
    at_risk: "volcano",
};

const formatDaysRemaining = (daysRemaining, isOverdue) => {
    if (daysRemaining === null || daysRemaining === undefined) {
        return "No due date";
    }
    if (isOverdue) {
        return `${Math.abs(daysRemaining)} day(s) overdue`;
    }
    if (daysRemaining === 0) {
        return "Due today";
    }
    return `${daysRemaining} day(s) left`;
};

export default function Reports() {
    const dispatch = useDispatch();

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [reportData, setReportData] = useState(null);
    const [isProjectDashboardOpen, setIsProjectDashboardOpen] = useState(false);

    const fetchReportData = async () => {
        setLoading(true);
        setError("");
        try {
            const data = await getReportsOverview();
            setReportData(data);
        } catch (requestError) {
            const message = requestError?.message || "Unable to load reports";
            setError(message);
            notification.error({
                message: "Report Generation Failed",
                description: message,
                placement: "topRight",
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchReportData();
    }, []);

    const summary = reportData?.summary || {};
    const issues = reportData?.ongoing_issues || [];
    const insights = reportData?.insights || [];
    const projectSummaries = reportData?.project_summaries || [];
    const charts = reportData?.charts || {};

    const summaryCards = useMemo(
        () => [
            {
                key: "active_projects",
                label: "Active Projects",
                value: summary.active_projects || 0,
                icon: <FundProjectionScreenOutlined />,
            },
            {
                key: "completed_projects",
                label: "Completed Projects",
                value: summary.completed_projects || 0,
                icon: <CheckCircleOutlined />,
            },
            {
                key: "average_progress",
                label: "Average Progress",
                value: `${summary.average_progress || 0}%`,
                icon: <RiseOutlined />,
            },
            {
                key: "task_completion_rate",
                label: "Task Completion",
                value: `${summary.task_completion_rate || 0}%`,
                icon: <BarChartOutlined />,
            },
            {
                key: "milestone_completion_rate",
                label: "Milestone Completion",
                value: `${summary.milestone_completion_rate || 0}%`,
                icon: <BarChartOutlined />,
            },
            {
                key: "overdue_projects",
                label: "Overdue Projects",
                value: summary.overdue_projects || 0,
                icon: <ExclamationCircleOutlined />,
            },
            {
                key: "blocked_tasks",
                label: "Blocked Tasks",
                value: summary.blocked_tasks || 0,
                icon: <ExclamationCircleOutlined />,
            },
        ],
        [summary],
    );

    const openProjectFromIssue = async (projectId) => {
        try {
            const allProjects = await dispatch(fetchProjects());
            const targetProject = (allProjects || []).find((project) => project.id === projectId);

            if (!targetProject) {
                notification.warning({
                    message: "Project unavailable",
                    description: "This project cannot be opened right now.",
                    placement: "topRight",
                });
                return;
            }

            dispatch(setSelectedProject(targetProject));
            setIsProjectDashboardOpen(true);
        } catch (requestError) {
            notification.error({
                message: "Unable to open project",
                description: requestError?.message || "Please try again.",
                placement: "topRight",
            });
        }
    };

    const maxTrendValue = Math.max(
    ...(charts.completion_trend || []).map(
      (item) => (item.completed_tasks || 0) + (item.completed_projects || 0)
    ),
    );

    return (
        <div className="reports-page">
            <section className="reports-hero">
                <div>
                    <Title level={2} className="reports-title">
                        Performance Reports & Insights
                    </Title>
                    <Paragraph className="reports-subtitle">
                        Track performance, monitor progress summaries, and detect ongoing issues across active projects.
                    </Paragraph>
                </div>
                <Button
                    icon={<ReloadOutlined />}
                    className="reports-refresh-btn"
                    onClick={fetchReportData}
                    loading={loading}
                >
                    Refresh Reports
                </Button>
            </section>

            {error ? (
                <Alert
                    showIcon
                    type="error"
                    message="Reports unavailable"
                    description={error}
                    className="reports-error"
                />
            ) : null}

            <Row gutter={[16, 16]}>
                {summaryCards.map((card) => (
                    <Col key={card.key} xs={24} sm={12} lg={8} xl={4}>
                        <Card className="reports-summary-card" bordered={false}>
                            <Space className="reports-summary-head">
                                <span className="reports-summary-icon">{card.icon}</span>
                                <Text className="reports-summary-label">{card.label}</Text>
                            </Space>
                            {loading ? (
                                <Skeleton.Input active size="small" />
                            ) : (
                                <Title level={3} className="reports-summary-value">
                                    {card.value}
                                </Title>
                            )}
                        </Card>
                    </Col>
                ))}
            </Row>

            <Row gutter={[16, 16]}>
                <Col xs={24} lg={14}>
                    <Card className="reports-chart-card" bordered={false}>
                        <Title level={4} className="reports-section-title">
                            Completion Trend (Last 6 Months)
                        </Title>
                        {loading ? (
                            <Skeleton active paragraph={{ rows: 4 }} />
                        ) : !(charts.completion_trend || []).length ? (
                            <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="No trend data" />
                        ) : (
                            <div className="reports-trend-chart">
                                {(charts.completion_trend || []).map((item) => {
                                    const completedTasks = item.completed_tasks || 0;
                                    const completedProjects = item.completed_projects || 0;
                                    const totalCompletion = completedTasks + completedProjects;
                                    const heightPercent = Math.max(
                                        12,
                                        Math.round((totalCompletion / maxTrendValue) * 100),
                                    );

                                    return (
                                        <div key={item.month} className="reports-trend-item">
                                            {totalCompletion > 0 && (
                                                <div className="reports-trend-value-group">
                                                    {completedProjects > 0 && (
                                                        <div className="reports-trend-value-sub">
                                                            <span className="reports-trend-badge-projects">P</span>
                                                            {completedProjects}
                                                        </div>
                                                    )}
                                                    {completedTasks > 0 && (
                                                        <div className="reports-trend-value-sub">
                                                            <span className="reports-trend-badge-tasks">T</span>
                                                            {completedTasks}
                                                        </div>
                                                    )}
                                                </div>
                                            )}
                                            <div className="reports-trend-bar-wrap">
                                                <div
                                                    className="reports-trend-bar"
                                                    style={{ height: `${heightPercent}%` }}
                                                    title={`${completedTasks} tasks, ${completedProjects} projects`}
                                                />
                                            </div>
                                            <div className="reports-trend-label">{item.month}</div>
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </Card>
                </Col>

                <Col xs={24} lg={10}>
                    <Card className="reports-chart-card" bordered={false}>
                        <Title level={4} className="reports-section-title">
                            Task Status Breakdown
                        </Title>

                        {(charts.task_status || []).map((item) => {
                            const total = (charts.task_status || []).reduce((sum, row) => sum + row.value, 0);
                            const percent = total ? Math.round((item.value / total) * 100) : 0;

                            return (
                                <div className="reports-breakdown-row" key={item.status}>
                                    <div className="reports-breakdown-copy">
                                        <Text>{item.status}</Text>
                                        <Text>{item.value}</Text>
                                    </div>
                                    <Progress
                                        percent={percent}
                                        size="small"
                                        showInfo={false}
                                        strokeColor="#22d3ee"
                                        trailColor="rgba(255,255,255,0.08)"
                                    />
                                </div>
                            );
                        })}
                    </Card>
                </Col>
            </Row>

            <Card className="reports-chart-card" bordered={false}>
                <Title level={4} className="reports-section-title">
                    Project Progress Comparison
                </Title>
                {loading ? (
                    <Skeleton active paragraph={{ rows: 4 }} />
                ) : !(charts.project_progress || []).length ? (
                    <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="No projects available" />
                ) : (
                    <div className="reports-project-progress-list">
                        {charts.project_progress.map((item) => (
                            <div className="reports-project-progress-item" key={item.project_name}>
                                <div className="reports-project-progress-head">
                                    <Space>
                                        <Text className="reports-project-name">{item.project_name}</Text>
                                        <Tag color={statusColorMap[item.status] || "default"}>
                                            {(item.status || "unknown").replace("_", " ")}
                                        </Tag>
                                    </Space>
                                    <Text>{item.progress}%</Text>
                                </div>
                                <Progress
                                    percent={item.progress || 0}
                                    size="small"
                                    showInfo={false}
                                    strokeColor={{ "0%": "#22d3ee", "100%": "#84cc16" }}
                                    trailColor="rgba(255,255,255,0.08)"
                                />
                            </div>
                        ))}
                    </div>
                )}
            </Card>

            <Row gutter={[16, 16]}>
                <Col xs={24} lg={11}>
                    <Card className="reports-chart-card" bordered={false}>
                        <Title level={4} className="reports-section-title">
                            Insights
                        </Title>
                        {loading ? (
                            <Skeleton active paragraph={{ rows: 3 }} />
                        ) : !(insights || []).length ? (
                            <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="No insights available" />
                        ) : (
                            <div className="reports-insight-list">
                                {insights.map((insight) => (
                                    <div key={insight.title} className="reports-insight-item">
                                        <Text className="reports-insight-title">{insight.title}</Text>
                                        <Paragraph className="reports-insight-value">{insight.value}</Paragraph>
                                    </div>
                                ))}
                            </div>
                        )}
                    </Card>
                </Col>

                <Col xs={24} lg={13}>
                    <Card className="reports-chart-card" bordered={false}>
                        <Title level={4} className="reports-section-title">
                            Ongoing Issues
                        </Title>
                        {loading ? (
                            <Skeleton active paragraph={{ rows: 4 }} />
                        ) : !issues.length ? (
                            <Empty
                                image={Empty.PRESENTED_IMAGE_SIMPLE}
                                description="No critical ongoing issues detected"
                            />
                        ) : (
                            <div className="reports-issue-list">
                                {issues.map((issue, index) => (
                                    <div key={`${issue.issue_type}-${issue.project_id}-${index}`} className="reports-issue-item">
                                        <div className="reports-issue-copy">
                                            <Space>
                                                <Text className="reports-issue-project">{issue.project_name}</Text>
                                                <Tag color={severityColorMap[issue.severity] || "default"}>
                                                    {issue.severity}
                                                </Tag>
                                            </Space>
                                            <Paragraph className="reports-issue-message">{issue.message}</Paragraph>
                                        </div>
                                        <Button
                                            type="default"
                                            size="small"
                                            onClick={() => openProjectFromIssue(issue.project_id)}
                                        >
                                            Open Project
                                        </Button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </Card>
                </Col>
            </Row>

            <Card className="reports-chart-card" bordered={false}>
                <Title level={4} className="reports-section-title">
                    Progress Summary by Active Project
                </Title>
                {loading ? (
                    <Skeleton active paragraph={{ rows: 4 }} />
                ) : !projectSummaries.length ? (
                    <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="No project summaries available" />
                ) : (
                    <div className="reports-project-summary-grid">
                        {projectSummaries.map((project) => (
                            <Card key={project.id} className="reports-project-summary-card" bordered={false}>
                                <div className="reports-project-summary-head">
                                    <Text className="reports-project-summary-title">{project.project_name}</Text>
                                    <Tag color={statusColorMap[project.status] || "default"}>
                                        {(project.status || "unknown").replace("_", " ")}
                                    </Tag>
                                </div>

                                <div className="reports-project-summary-metrics">
                                    <Text>Progress: {project.progress}%</Text>
                                    <Text>
                                        Timeline: {formatDaysRemaining(project.days_remaining, project.is_overdue)}
                                    </Text>
                                    <Text>
                                        Tasks: {project.completed_tasks}/{project.task_count} completed
                                    </Text>
                                    <Text>
                                        Milestones: {project.completed_milestones}/{project.milestone_count} completed
                                    </Text>
                                    <Text>Blocked Tasks: {project.blocked_tasks}</Text>
                                    <Text>Overdue Milestones: {project.overdue_milestones}</Text>
                                </div>

                                <div className="reports-project-summary-progress">
                                    <Text>Task Completion</Text>
                                    <Progress
                                        percent={project.task_completion_rate}
                                        size="small"
                                        strokeColor="#60a5fa"
                                        trailColor="rgba(255,255,255,0.08)"
                                    />

                                    <Text>Milestone Completion</Text>
                                    <Progress
                                        percent={project.milestone_completion_rate}
                                        size="small"
                                        strokeColor="#34d399"
                                        trailColor="rgba(255,255,255,0.08)"
                                    />
                                </div>

                                <Button type="primary" onClick={() => openProjectFromIssue(project.id)}>
                                    Open Details
                                </Button>
                            </Card>
                        ))}
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
