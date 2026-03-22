const API_BASE_URL = "http://localhost:8000/api";

export const createProject = async (projectData) => {
  try {
    const token = localStorage.getItem("authToken");
    const response = await fetch(`${API_BASE_URL}/projects/create/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Token ${token}`,
      },
      body: JSON.stringify(projectData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || JSON.stringify(errorData));
    }

    return await response.json();
  } catch (error) {
    throw error;
  }
};

export const getAllProjects = async () => {
    try {
        const token = localStorage.getItem("authToken");
        const response = await fetch(`${API_BASE_URL}/projects/projects/`, {
            method:'GET',
            headers: {
                'Content-type': 'application/json',
                Authorization: `Token ${token}`
            }
        })
        if(!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Unable to fetch projects");
        }

        return await response.json()
    } catch (error) {
        throw error
    }
}

export const deleteProject = async (projectId) => {
    try {
        const token = localStorage.getItem("authToken");
        const response = await fetch(`${API_BASE_URL}/projects/${projectId}/`, {
            method: "DELETE",
            headers: {
                'Content-type': 'application/json',
                Authorization: `Token ${token}`
            }
        })
        if (!response.ok) {
            const errorData = await response.json()
            throw new Error(errorData.Detail || "Error occurred while deleting project")
        }
        return await response.json();
    } catch (error) {
        throw error
    }
}

export const updateProject = async (projectId, projectData) => {
    try {
        const token = localStorage.getItem("authToken");
        const response = await fetch(`${API_BASE_URL}/projects/${projectId}/`, {
            method: "PUT",
            headers: {
                'Content-type': 'application/json',
                Authorization: `Token ${token}`
            },
            body: JSON.stringify(projectData)
        })

        if (!response.ok) {
            const errorData = await response.json()
            throw new Error(errorData.Detail || "Error occurred while updating project")
        }
        return await response.json();
    } catch (error) {
        throw error
    }
}