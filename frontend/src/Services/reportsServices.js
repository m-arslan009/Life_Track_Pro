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

export const getReportsOverview = async () => {
  const response = await fetch(`${API_BASE_URL}/reports/overview/`, {
    method: "GET",
    headers: getAuthHeaders(),
  });

  const data = await parseResponseBody(response);

  if (!response.ok) {
    throw buildApiError(response, data, "Unable to fetch reports overview");
  }

  return data;
};
