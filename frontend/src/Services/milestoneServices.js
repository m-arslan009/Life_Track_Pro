const API_BASE_URL = "http://localhost:8000/api";

const getAuthHeaders = () => {
  const token = localStorage.getItem("authToken");
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

export const getMilestones = async (projectId = null) => {
  const query = projectId ? `?project_id=${projectId}` : "";
  const response = await fetch(
    `${API_BASE_URL}/milestones/milestones/${query}`,
    {
      method: "GET",
      headers: getAuthHeaders(),
    },
  );

  const data = await parseResponseBody(response);

  if (!response.ok) {
    throw buildApiError(response, data, "Unable to fetch milestones");
  }

  return data;
};

export const createMilestone = async (payload) => {
  const response = await fetch(`${API_BASE_URL}/milestones/create/`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });

  const data = await parseResponseBody(response);

  if (!response.ok) {
    throw buildApiError(response, data, "Unable to create milestone");
  }

  return data;
};

export const updateMilestone = async (milestoneId, payload) => {
  const response = await fetch(`${API_BASE_URL}/milestones/${milestoneId}/`, {
    method: "PUT",
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });

  const data = await parseResponseBody(response);

  if (!response.ok) {
    throw buildApiError(response, data, "Unable to update milestone");
  }

  return data;
};

export const deleteMilestone = async (milestoneId) => {
  const response = await fetch(`${API_BASE_URL}/milestones/${milestoneId}/`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });

  const data = await parseResponseBody(response);

  if (!response.ok) {
    throw buildApiError(response, data, "Failed to delete milestone");
  }

  return data;
};

export const updateMilestoneStatus = async (milestoneId, status) => {
  const response = await fetch(
    `${API_BASE_URL}/milestones/${milestoneId}/status/`,
    {
      method: "PATCH",
      headers: getAuthHeaders(),
      body: JSON.stringify({ status }),
    },
  );

  const data = await parseResponseBody(response);

  if (!response.ok) {
    throw buildApiError(response, data, "Unable to update milestone status");
  }

  return data;
};

export const createTask = async (payload) => {
  const response = await fetch(`${API_BASE_URL}/tasks/tasks/`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });

  const data = await parseResponseBody(response);

  if (!response.ok) {
    throw buildApiError(response, data, "Unable to create task");
  }

  return data;
};

export const updateTask = async (taskId, payload) => {
  const response = await fetch(`${API_BASE_URL}/tasks/tasks/${taskId}/`, {
    method: "PUT",
    headers: getAuthHeaders(),
    body: JSON.stringify(payload),
  });

  const data = await parseResponseBody(response);

  if (!response.ok) {
    throw buildApiError(response, data, "Unable to update task");
  }

  return data;
};

export const updateTaskStatus = async (taskId, status) => {
  const response = await fetch(
    `${API_BASE_URL}/tasks/tasks/${taskId}/status/`,
    {
      method: "PATCH",
      headers: getAuthHeaders(),
      body: JSON.stringify({ status }),
    },
  );

  const data = await parseResponseBody(response);

  if (!response.ok) {
    throw buildApiError(response, data, "Unable to update task status");
  }

  return data;
};

export const deleteTask = async (taskId) => {
  const response = await fetch(`${API_BASE_URL}/tasks/tasks/${taskId}/`, {
    method: "DELETE",
    headers: getAuthHeaders(),
  });

  const data = await parseResponseBody(response);

  if (!response.ok) {
    throw buildApiError(response, data, "Failed to delete task");
  }

  return data;
};
