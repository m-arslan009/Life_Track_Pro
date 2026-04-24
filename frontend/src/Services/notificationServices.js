const API_BASE_URL = "http://localhost:8000/api";

const getAuthToken = () => {
  const rawToken = localStorage.getItem("authToken") || localStorage.getItem("token");
  if (!rawToken) {
    throw new Error("Your session has expired. Please log in again.");
  }

  return rawToken.replace(/^Token\s+/i, "").replace(/^Bearer\s+/i, "").trim();
};

const getAuthHeaders = () => {
  const token = getAuthToken();
  return {
    "Content-Type": "application/json",
    Authorization: `Token ${token}`,
  };
};

const parseResponseBody = async (response) => {
  const contentType = response.headers.get("content-type") || "";
  const responseText = await response.text();

  if (!responseText) {
    return null;
  }

  if (contentType.includes("application/json")) {
    return JSON.parse(responseText);
  }

  try {
    return JSON.parse(responseText);
  } catch {
    return responseText;
  }
};

const buildApiError = (response, data, fallbackMessage) => {
  if (data && typeof data === "object") {
    const detail = data.detail || data.Detail;
    if (detail) {
      return new Error(detail);
    }
    return new Error(JSON.stringify(data));
  }

  if (typeof data === "string" && data.trim().length > 0) {
    if (
      data.trim().startsWith("<!DOCTYPE") ||
      data.trim().startsWith("<html")
    ) {
      return new Error(`${fallbackMessage} (HTTP ${response.status})`);
    }
    return new Error(data);
  }

  return new Error(`${fallbackMessage} (HTTP ${response.status})`);
};

export const getNotifications = async (filters = {}) => {
  try {
    const params = new URLSearchParams();

    if (filters.is_read !== undefined) {
      params.append("is_read", filters.is_read);
    }
    if (filters.type) {
      params.append("type", filters.type);
    }

    const queryString = params.toString();
    const url = queryString
      ? `/notifications/?${queryString}`
      : "/notifications/";

    const response = await fetch(`${API_BASE_URL}${url}`, {
      method: "GET",
      headers: getAuthHeaders(),
    });

    const data = await parseResponseBody(response);

    if (!response.ok) {
      throw buildApiError(response, data, "Unable to fetch notifications");
    }

    return data;
  } catch (error) {
    console.error("Error fetching notifications:", error);
    throw error;
  }
};

export const getRecentNotifications = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/notifications/recent/`, {
      method: "GET",
      headers: getAuthHeaders(),
    });

    const data = await parseResponseBody(response);
    if (!response.ok) {
      throw buildApiError(response, data, "Unable to fetch recent notifications");
    }

    return data;
  } catch (error) {
    console.error("Error fetching recent notifications:", error);
    throw error;
  }
};

export const markNotificationAsRead = async (notificationId) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/notifications/mark-as-read/${notificationId}/`,
      {
        method: "POST",
        headers: getAuthHeaders(),
      }
    );

    const data = await parseResponseBody(response);
    if (!response.ok) {
      throw buildApiError(response, data, "Unable to mark notification as read");
    }

    return data;
  } catch (error) {
    console.error("Error marking notification as read:", error);
    throw error;
  }
};

export const markAllNotificationsAsRead = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/notifications/mark-all-as-read/`, {
      method: "POST",
      headers: getAuthHeaders(),
    });

    const data = await parseResponseBody(response);
    if (!response.ok) {
      throw buildApiError(response, data, "Unable to mark all notifications as read");
    }

    return data;
  } catch (error) {
    console.error("Error marking all notifications as read:", error);
    throw error;
  }
};

export const deleteNotification = async (notificationId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/notifications/delete/${notificationId}/`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    });

    const data = await parseResponseBody(response);
    if (!response.ok) {
      throw buildApiError(response, data, "Unable to delete notification");
    }

    return { success: true };
  } catch (error) {
    console.error("Error deleting notification:", error);
    throw error;
  }
};

export const deleteAllNotifications = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/notifications/delete-all/`, {
      method: "POST",
      headers: getAuthHeaders(),
    });

    const data = await parseResponseBody(response);
    if (!response.ok) {
      throw buildApiError(response, data, "Unable to delete all notifications");
    }

    return { success: true };
  } catch (error) {
    console.error("Error deleting all notifications:", error);
    throw error;
  }
};
