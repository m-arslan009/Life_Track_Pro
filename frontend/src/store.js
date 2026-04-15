import { configureStore } from "@reduxjs/toolkit";
import projectReducer from "./Services/ProjectSlice";

const store = configureStore({
  reducer: {
    project: projectReducer,
  },
});

export default store;
