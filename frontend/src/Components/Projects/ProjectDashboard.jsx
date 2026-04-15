import { Modal, Tabs } from "antd";
import { useSelector } from "react-redux";
import MilestoneCard from "./MilestoneCard";
import OverviewCard from "./OverviewCard";
import ProjectMindMap from "./ProjectMindMap";
import "./ProjectDashboard.css";
import { getSelectedProject } from "../../Services/ProjectSlice";

function ProjectDashboard({ isOpen, onClose }) {
  const project = useSelector(getSelectedProject);

  const tabItem = [
    {
      key: "1",
      label: "Overview",
      children: <OverviewCard />,
    },
    {
      key: "2",
      label: "Milestones",
      children: (
        <MilestoneCard
          key={project?.id ?? "project-empty"}
          teamMembers={project?.teamMembers ?? []}
          initialMilestones={project?.milestones ?? []}
        />
      ),
    },
    {
      key: "3",
      label: "Mind Map",
      children: <ProjectMindMap />,
    },
  ];
  return (
    <Modal
      width={"80vw"}
      open={isOpen}
      onCancel={onClose}
      okButtonProps={{ style: { display: "none" } }}
      footer={null}
      centered
      className="project-dashboard-modal"
      styles={{
        content: {
          height: "80vh",
          maxHeight: "80vh",
          overflow: "hidden",
          display: "flex",
          flexDirection: "column",
          backgroundColor: "transparent",
        },
        body: {
          flex: 1,
          minHeight: 0,
          overflow: "hidden",
          display: "flex",
        },
      }}
    >
      <Tabs
        items={tabItem}
        defaultActiveKey="1"
        className="project-dashboard-tabs"
      />
    </Modal>
  );
}

export default ProjectDashboard;
