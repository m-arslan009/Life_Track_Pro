const API_BASE_URL = "http://localhost:8000/api";

export const sendChatMessage = async (message, sessionId, context = {}) => {
  const token = localStorage.getItem("authToken");
  const authUser = JSON.parse(localStorage.getItem("authUser") || "{}");

  const response = await fetch(`${API_BASE_URL}/chatbot/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Token ${token}` }),
    },
    body: JSON.stringify({
      message,
      session_id: sessionId,
      user_id: authUser.id || null,
      context,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Server error (${response.status})`);
  }

  return response.json();
};