import {
  Navigate,
  RouterProvider,
  createBrowserRouter,
} from "react-router-dom";
import { ConfigProvider, theme } from "antd";
import "./App.css";

// Outer Pages
import { SignUp } from "./Pages/Sign Up/SIgnUp";
import { Login } from "./Pages/Login/Login";

// Layout
import SideBar from "./Components/Layout/SideBar";

// Sidebar Pages
import Dashboard from "./Pages/Dashboard/Dashboard";
import MyProjects from "./Pages/My Projects/MyProjects";
import CalendarView from "./Pages/Calendar/Calendar";
import Reports from "./Pages/Reports/Reports";
import AIAssistant from "./Pages/AI Assistant/AIAssistant";
import Notifications from "./Pages/Notifications/Notifications";
import Settings from "./Pages/Settings/Settings";
import { getAllUsers } from "./Services/userServices";

const router = createBrowserRouter([
  {
    path: "/",
    element: <Navigate to="/login" replace />,
  },
  {
    path: "/signup",
    element: <SignUp />,
  },
  {
    path: "/login",
    element: <Login />,
  },
  {
    element: <SideBar />,
    children: [
      { path: "/dashboard", element: <Dashboard /> },
      {
        path: "/projects",
        element: <MyProjects />,
        loader: async () => {
          const users = await getAllUsers();
          return { users };
        },
      },
      { path: "/calendar", element: <CalendarView /> },
      { path: "/reports", element: <Reports /> },
      { path: "/assistant", element: <AIAssistant /> },
      { path: "/notifications", element: <Notifications /> },
      { path: "/settings", element: <Settings /> },
    ],
  },
]);

function App() {
  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorPrimary: "#00C9FF",
          colorBgBase: "#141414",
        },
      }}
    >
      <RouterProvider router={router} />
    </ConfigProvider>
  );
}

export default App;
