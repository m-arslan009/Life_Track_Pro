import { createSlice } from "@reduxjs/toolkit";

const API_BASE_URL = "http://localhost:8000/api";

const getAuthHeaders = () => {
  const token = localStorage.getItem("authToken");

  return {
    "Content-Type": "application/json",
    Authorization: `Token ${token}`,
  };
};

const parseApiError = async (response, fallbackMessage) => {
  try {
    const errorData = await response.json();
    return errorData.detail || errorData.Detail || JSON.stringify(errorData);
  } catch {
    return `${fallbackMessage} (HTTP ${response.status})`;
  }
};

const initialState = {
  projects: [],
  selectedProject: null,
  isLoading: false,
  error: null,
};

const appendUniqueById = (items = [], newItem) => {
  if (!newItem?.id) {
    return [...items, newItem];
  }

  const alreadyExists = items.some((item) => item?.id === newItem.id);
  return alreadyExists ? items : [...items, newItem];
};

const projectSlice = createSlice({
  name: "project",
  initialState,
  reducers: {
    fetchStart: (state) => {
      state.isLoading = true;
      state.error = null;
    },
    fetchSuccess: (state, action) => {
      state.isLoading = false;
      state.projects = action.payload || [];
    },
    addProjectSuccess: (state, action) => {
      state.isLoading = false;
      state.projects.unshift(action.payload);
    },
    updateProjectSuccess: (state, action) => {
      state.isLoading = false;
      const updatedProject = action.payload;
      const index = state.projects.findIndex((p) => p.id === updatedProject.id);

      if (index !== -1) {
        state.projects[index] = updatedProject;
      }

      if (state.selectedProject?.id === updatedProject.id) {
        state.selectedProject = updatedProject;
      }
    },
    setSelectedProject: (state, action) => {
      state.selectedProject = action.payload;
    },
    deleteProjectSuccess: (state, action) => {
      state.isLoading = false;
      state.projects = state.projects.filter((p) => p.id !== action.payload);

      if (state.selectedProject?.id === action.payload) {
        state.selectedProject = null;
      }
    },
    fetchError: (state, action) => {
      state.isLoading = false;
      state.error = action.payload || "Unexpected error";
    },
    clearProjectError: (state) => {
      state.error = null;
    },
    addProjectMileStone: (state, action) => {
      const { project_id, newMileStone } = action.payload;
      const projectIndex = state.projects.findIndex(
        (pro) => pro.id === project_id,
      );

      if (projectIndex === -1) return;

      const targetProject = state.projects[projectIndex];
      const currentMilestones = targetProject.milestones || [];
      targetProject.milestones = appendUniqueById(
        currentMilestones,
        newMileStone,
      );

      if (state.selectedProject?.id === project_id) {
        const selectedMilestones = state.selectedProject.milestones || [];
        state.selectedProject.milestones = appendUniqueById(
          selectedMilestones,
          newMileStone,
        );
      }
    },

    addProjectMileStoneTask: (state, action) => {
      const { project_id, milestone_id, mileStoneTask } = action.payload;
      const projectIndex = state.projects.findIndex(
        (pro) => pro.id === project_id,
      );

      if (projectIndex === -1) return;

      const milestones = state.projects[projectIndex].milestones || [];
      const mileStoneIndex = milestones.findIndex(
        (ms) => ms.id === milestone_id,
      );

      if (mileStoneIndex === -1) return;

      const milestone = milestones[mileStoneIndex];
      const currentTasks = milestone.tasks || [];
      milestone.tasks = appendUniqueById(currentTasks, mileStoneTask);

      if (state.selectedProject?.id === project_id) {
        const selectedMilestones = state.selectedProject.milestones || [];
        const selectedMilestoneIndex = selectedMilestones.findIndex(
          (ms) => ms.id === milestone_id,
        );

        if (selectedMilestoneIndex !== -1) {
          const selectedMilestone = selectedMilestones[selectedMilestoneIndex];
          selectedMilestone.tasks = appendUniqueById(
            selectedMilestone.tasks || [],
            mileStoneTask,
          );
        }
      }
    },
  },
});

export const {
  fetchStart,
  fetchSuccess,
  addProjectSuccess,
  updateProjectSuccess,
  deleteProjectSuccess,
  fetchError,
  clearProjectError,
  setSelectedProject,
  addProjectMileStone,
  addProjectMileStoneTask,
} = projectSlice.actions;

export const fetchProjects = () => {
  return async (dispatch) => {
    dispatch(fetchStart());

    try {
      const response = await fetch(`${API_BASE_URL}/projects/projects/`, {
        method: "GET",
        headers: getAuthHeaders(),
      });

      if (!response.ok) {
        const errorMessage = await parseApiError(
          response,
          "Unable to fetch projects",
        );
        throw new Error(errorMessage);
      }

      const data = await response.json();
      dispatch(fetchSuccess(data));
      return data;
    } catch (error) {
      dispatch(fetchError(error.message));
      throw error;
    }
  };
};

export const createProjectThunk = (projectData) => {
  return async (dispatch) => {
    dispatch(fetchStart());

    try {
      const response = await fetch(`${API_BASE_URL}/projects/create/`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify(projectData),
      });

      if (!response.ok) {
        const errorMessage = await parseApiError(
          response,
          "Unable to create project",
        );
        throw new Error(errorMessage);
      }

      const data = await response.json();
      dispatch(addProjectSuccess(data));
      return data;
    } catch (error) {
      dispatch(fetchError(error.message));
      throw error;
    }
  };
};

export const updateProjectThunk = ({ projectId, projectData }) => {
  return async (dispatch) => {
    dispatch(fetchStart());

    try {
      const response = await fetch(`${API_BASE_URL}/projects/${projectId}/`, {
        method: "PUT",
        headers: getAuthHeaders(),
        body: JSON.stringify(projectData),
      });

      if (!response.ok) {
        const errorMessage = await parseApiError(
          response,
          "Unable to update project",
        );
        throw new Error(errorMessage);
      }

      const data = await response.json();
      dispatch(updateProjectSuccess(data));
      return data;
    } catch (error) {
      dispatch(fetchError(error.message));
      throw error;
    }
  };
};

export const updateProjectStatusThunk = ({ projectId, status }) => {
  return async (dispatch) => {
    dispatch(fetchStart());

    try {
      const response = await fetch(
        `${API_BASE_URL}/projects/${projectId}/status/`,
        {
          method: "PATCH",
          headers: getAuthHeaders(),
          body: JSON.stringify({ status }),
        },
      );

      if (!response.ok) {
        const errorMessage = await parseApiError(
          response,
          "Unable to update project status",
        );
        throw new Error(errorMessage);
      }

      const data = await response.json();
      dispatch(updateProjectSuccess(data));
      return data;
    } catch (error) {
      dispatch(fetchError(error.message));
      throw error;
    }
  };
};

export const deleteProjectThunk = (projectId) => {
  return async (dispatch) => {
    dispatch(fetchStart());

    try {
      const response = await fetch(`${API_BASE_URL}/projects/${projectId}/`, {
        method: "DELETE",
        headers: getAuthHeaders(),
      });

      if (!response.ok) {
        const errorMessage = await parseApiError(
          response,
          "Unable to delete project",
        );
        throw new Error(errorMessage);
      }

      dispatch(deleteProjectSuccess(projectId));
      return projectId;
    } catch (error) {
      dispatch(fetchError(error.message));
      throw error;
    }
  };
};

export const selectProjects = (state) => state.project.projects;
export const selectProjectsLoading = (state) => state.project.isLoading;
export const selectProjectsError = (state) => state.project.error;
export const getSelectedProject = (state) => state.project.selectedProject;

export default projectSlice.reducer;
