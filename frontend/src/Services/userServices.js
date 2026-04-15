const API_BASE_URL = "http://localhost:8000/api";

const AUTH_USER_KEY = "authUser";

export const registerUser = async (userData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/users/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: userData.username,
        email: userData.email,
        password: userData.password,
        first_name: userData?.firstName ?? "",
        last_name: userData?.lastName ?? "",
        role: "developer",
      }),
    });

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch (parseError) {
        throw new Error(
          `Server error (${response.status}). Please try again later.`,
        );
      }

      throw new Error(
        errorData.detail ||
          errorData.username?.[0] ||
          errorData.email?.[0] ||
          "Registration failed. Please try again.",
      );
    }

    return await response.json();
  } catch (error) {
    throw error;
  }
};

export const loginUser = async (username, password) => {
  try {
    const response = await fetch(`${API_BASE_URL}/users/login/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username,
        password,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(
        errorData.non_field_errors?.[0] ||
          errorData.detail ||
          "Invalid credentials.",
      );
    }

    const data = await response.json();

    if (data.token) {
      localStorage.setItem("authToken", data.token);
    }

    if (data.user) {
      localStorage.setItem(AUTH_USER_KEY, JSON.stringify(data.user));
    }

    return data;
  } catch (error) {
    throw error;
  }
};

export const getCurrentUser = async () => {
  try {
    const token = localStorage.getItem("authToken");
    if (!token) throw new Error("No authentication token found.");

    const response = await fetch(`${API_BASE_URL}/users/me/`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Token ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to fetch user data.");
    }

    const data = await response.json();
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(data));
    return data;
  } catch (error) {
    throw error;
  }
};

export const getStoredAuthUser = () => {
  const raw = localStorage.getItem(AUTH_USER_KEY);
  if (!raw) return null;

  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
};

export const getStoredAuthUserId = () => getStoredAuthUser()?.id ?? null;

export const getAllUsers = async () => {
  try {
    const token = localStorage.getItem("authToken");
    if (!token) throw new Error("No authentication token found.");

    const response = await fetch(`${API_BASE_URL}/users/users/`, {
      method: "GET",
      headers: {
        "Content-type": "application/json",
        Authorization: `Token ${token}`,
      },
    });
    if (!response.ok) {
      throw new Error("Something is wrong. Unable to fetch all the users");
    }
    return await response.json();
  } catch (error) {
    throw error;
  }
};

export const logoutUser = () => {
  localStorage.removeItem("authToken");
  localStorage.removeItem(AUTH_USER_KEY);
};
