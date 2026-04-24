import { useEffect, useState } from "react";
import {
  Alert,
  Button,
  Card,
  Col,
  Empty,
  Row,
  Skeleton,
  Space,
  Tag,
  Typography,
  notification,
  Popconfirm,
  Space as AntSpace,
  Segmented,
} from "antd";
import {
  AlertOutlined,
  CheckCircleOutlined,
  DeleteOutlined,
  CheckOutlined,
  DeleteFilled,
  ProjectOutlined,
  CheckSquareOutlined,
  TeamOutlined,
  ExclamationCircleOutlined,
  ClockCircleOutlined,
} from "@ant-design/icons";
import {
  getNotifications,
  markNotificationAsRead,
  markAllNotificationsAsRead,
  deleteNotification,
  deleteAllNotifications,
} from "../../Services/notificationServices";
import "./Notifications.css";

const { Title, Text, Paragraph } = Typography;

const getNotificationIcon = (type) => {
  const iconMap = {
    project_created: <ProjectOutlined />,
    project_updated: <ProjectOutlined />,
    project_completed: <CheckCircleOutlined />,
    milestone_created: <CheckSquareOutlined />,
    milestone_completed: <CheckCircleOutlined />,
    task_assigned: <CheckSquareOutlined />,
    task_completed: <CheckCircleOutlined />,
    task_blocked: <ExclamationCircleOutlined />,
    team_member_added: <TeamOutlined />,
    project_at_risk: <ExclamationCircleOutlined />,
    project_overdue: <ClockCircleOutlined />,
  };
  return iconMap[type] || <AlertOutlined />;
};

const getNotificationColor = (type) => {
  if (type.includes("completed")) return "success";
  if (type.includes("at_risk") || type.includes("overdue") || type.includes("blocked"))
    return "error";
  if (type.includes("created") || type.includes("added")) return "blue";
  return "default";
};

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState("all"); // all, unread, read
  const [totalCount, setTotalCount] = useState(0);
  const [unreadCount, setUnreadCount] = useState(0);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    fetchNotifications();
  }, [filter]);

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const filters = {};
      if (filter === "unread") {
        filters.is_read = false;
      } else if (filter === "read") {
        filters.is_read = true;
      }

      const data = await getNotifications(filters);
      setNotifications(data.notifications || []);
      setTotalCount(data.total_count || 0);
      setUnreadCount(data.unread_count || 0);
      setErrorMessage("");
    } catch (error) {
      console.error("Error fetching notifications:", error);
      setErrorMessage(error.message || "Failed to fetch notifications");
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (notificationId) => {
    try {
      await markNotificationAsRead(notificationId);
      fetchNotifications();
      notification.success({
        message: "Success",
        description: "Notification marked as read",
      });
    } catch (error) {
      notification.error({
        message: "Error",
        description: "Failed to mark notification as read",
      });
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await markAllNotificationsAsRead();
      fetchNotifications();
      notification.success({
        message: "Success",
        description: "All notifications marked as read",
      });
    } catch (error) {
      notification.error({
        message: "Error",
        description: "Failed to mark all notifications as read",
      });
    }
  };

  const handleDelete = async (notificationId) => {
    try {
      await deleteNotification(notificationId);
      fetchNotifications();
      notification.success({
        message: "Success",
        description: "Notification deleted",
      });
    } catch (error) {
      notification.error({
        message: "Error",
        description: "Failed to delete notification",
      });
    }
  };

  const handleDeleteAll = async () => {
    try {
      await deleteAllNotifications();
      fetchNotifications();
      notification.success({
        message: "Success",
        description: "All notifications deleted",
      });
    } catch (error) {
      notification.error({
        message: "Error",
        description: "Failed to delete all notifications",
      });
    }
  };

  return (
    <div className="notifications-container">
      <Row gutter={[24, 24]}>
        {/* Header Section */}
        <Col xs={24}>
          <div className="notifications-header">
            <div className="notifications-title-section">
              <Title level={2} className="notifications-title">
                Notifications
              </Title>
              <Paragraph className="notifications-subtitle">
                Stay updated with all your project activities and updates
              </Paragraph>
            </div>

            {unreadCount > 0 && (
              <div className="notifications-unread-badge">
                <span className="badge-text">{unreadCount} unread</span>
              </div>
            )}
          </div>
        </Col>

        {/* Stats Cards */}
        <Col xs={24} lg={12}>
          <Row gutter={[12, 12]}>
            <Col xs={12} sm={8}>
              <Card className="notifications-stat-card" bordered={false}>
                <div className="stat-content">
                  <div className="stat-number">{totalCount}</div>
                  <div className="stat-label">Total</div>
                </div>
              </Card>
            </Col>
            <Col xs={12} sm={8}>
              <Card className="notifications-stat-card" bordered={false}>
                <div className="stat-content">
                  <div className="stat-number">{unreadCount}</div>
                  <div className="stat-label">Unread</div>
                </div>
              </Card>
            </Col>
            <Col xs={12} sm={8}>
              <Card className="notifications-stat-card" bordered={false}>
                <div className="stat-content">
                  <div className="stat-number">{totalCount - unreadCount}</div>
                  <div className="stat-label">Read</div>
                </div>
              </Card>
            </Col>
          </Row>
        </Col>

        {/* Action Buttons */}
        <Col xs={24} lg={12}>
          <div className="notifications-actions">
            <Segmented
              value={filter}
              onChange={(value) => setFilter(value)}
              options={[
                { label: "All", value: "all" },
                { label: "Unread", value: "unread" },
                { label: "Read", value: "read" },
              ]}
              className="notifications-filter"
            />

            <AntSpace>
              {unreadCount > 0 && (
                <Button
                  type="primary"
                  icon={<CheckOutlined />}
                  onClick={handleMarkAllAsRead}
                  className="action-button-primary"
                >
                  Mark All Read
                </Button>
              )}

              {totalCount > 0 && (
                <Popconfirm
                  title="Delete All Notifications"
                  description="Are you sure you want to delete all notifications? This action cannot be undone."
                  onConfirm={handleDeleteAll}
                  okText="Yes"
                  cancelText="No"
                >
                  <Button
                    danger
                    icon={<DeleteFilled />}
                    className="action-button-danger"
                  >
                    Clear All
                  </Button>
                </Popconfirm>
              )}
            </AntSpace>
          </div>
        </Col>

        {/* Notifications List */}
        <Col xs={24}>
          {errorMessage && (
            <Alert
              type="error"
              showIcon
              className="notifications-error-alert"
              message="Unable to load notifications"
              description={errorMessage}
              style={{ marginBottom: 16 }}
            />
          )}

          {loading ? (
            <Skeleton active paragraph={{ rows: 4 }} />
          ) : notifications.length === 0 ? (
            <Card className="notifications-empty-card" bordered={false}>
              <Empty
                image={Empty.PRESENTED_IMAGE_SIMPLE}
                description={
                  filter === "all"
                    ? "No notifications yet"
                    : `No ${filter} notifications`
                }
              />
            </Card>
          ) : (
            <div className="notifications-list">
              {notifications.map((notif) => (
                <Card
                  key={notif.id}
                  className={`notification-item ${!notif.is_read ? "unread" : ""}`}
                  bordered={false}
                >
                  <Row align="middle" gutter={16} className="notification-content">
                    <Col xs={2} sm={1}>
                      <div
                        className={`notification-icon notification-icon-${getNotificationColor(
                          notif.notification_type
                        )}`}
                      >
                        {getNotificationIcon(notif.notification_type)}
                      </div>
                    </Col>

                    <Col xs={22} sm={17}>
                      <div className="notification-body">
                        <div className="notification-header-row">
                          <Title level={5} className="notification-title">
                            {notif.title}
                          </Title>
                          <Tag
                            color={getNotificationColor(notif.notification_type)}
                            className="notification-tag"
                          >
                            {notif.notification_type.replace(/_/g, " ")}
                          </Tag>
                        </div>

                        <Paragraph className="notification-message">
                          {notif.message}
                        </Paragraph>

                        {(notif.project_name ||
                          notif.task_name ||
                          notif.milestone_name) && (
                          <div className="notification-meta">
                            {notif.project_name && (
                              <div className="meta-item">
                                <span className="meta-label">Project:</span>
                                <span className="meta-value">
                                  {notif.project_name}
                                </span>
                              </div>
                            )}
                            {notif.task_name && (
                              <div className="meta-item">
                                <span className="meta-label">Task:</span>
                                <span className="meta-value">{notif.task_name}</span>
                              </div>
                            )}
                            {notif.milestone_name && (
                              <div className="meta-item">
                                <span className="meta-label">Milestone:</span>
                                <span className="meta-value">
                                  {notif.milestone_name}
                                </span>
                              </div>
                            )}
                          </div>
                        )}

                        <div className="notification-footer">
                          <Text className="notification-time">
                            {notif.time_ago}
                          </Text>
                        </div>
                      </div>
                    </Col>

                    <Col xs={24} sm={6}>
                      <div className="notification-actions-col">
                        {!notif.is_read && (
                          <Button
                            type="text"
                            size="small"
                            icon={<CheckOutlined />}
                            onClick={() => handleMarkAsRead(notif.id)}
                            className="action-icon-button"
                            title="Mark as read"
                          >
                            Read
                          </Button>
                        )}

                        <Popconfirm
                          title="Delete Notification"
                          description="Are you sure you want to delete this notification?"
                          onConfirm={() => handleDelete(notif.id)}
                          okText="Yes"
                          cancelText="No"
                        >
                          <Button
                            type="text"
                            size="small"
                            danger
                            icon={<DeleteOutlined />}
                            className="action-icon-button"
                            title="Delete notification"
                          >
                            Delete
                          </Button>
                        </Popconfirm>
                      </div>
                    </Col>
                  </Row>

                  {!notif.is_read && (
                    <div className="notification-unread-indicator"></div>
                  )}
                </Card>
              ))}
            </div>
          )}
        </Col>
      </Row>
    </div>
  );
};

export default Notifications;
