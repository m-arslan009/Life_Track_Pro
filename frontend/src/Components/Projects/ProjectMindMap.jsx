import { CollapseExpandIcon, MindMap, RCNode } from "@ant-design/graphs";
import { Empty, Space, Tag, Typography } from "antd";
import { useMemo } from "react";
import { useSelector } from "react-redux";
import { getSelectedProject } from "../../Services/ProjectSlice";
import { getProjectWorkSummary } from "../../Utils/projectProgress";

const { PlusMinusIcon } = CollapseExpandIcon;
const { TextNode } = RCNode;
const { Title, Text } = Typography;

const updateCollapseExpandBehavior = (options) => {
  return (transforms = []) => {
    const nextTransforms = transforms.filter(
      (transform) => transform?.key !== "collapse-expand-react-node",
    );
    const currentTransform =
      transforms.find(
        (transform) => transform?.key === "collapse-expand-react-node",
      ) || {};

    return [
      ...nextTransforms,
      {
        ...currentTransform,
        ...options,
      },
    ];
  };
};

const toMindMapNode = (id, title, children = []) => ({
  id,
  data: { title },
  children,
});

const buildMindMapTree = (project) => {
  if (!project) return null;

  return toMindMapNode(
    `project-${project.id}`,
    project.project_name || "Untitled Project",
    (project.milestones || []).map((milestone) =>
      toMindMapNode(
        `milestone-${milestone.id}`,
        milestone.title || "Untitled Milestone",
        (milestone.tasks || milestone.milestone_tasks || []).map((task) =>
          toMindMapNode(`task-${task.id}`, task.title || "Untitled Task", []),
        ),
      ),
    ),
  );
};

function ProjectMindMap() {
  const selectedProject = useSelector(getSelectedProject);

  const projectSummary = useMemo(
    () => getProjectWorkSummary(selectedProject),
    [selectedProject],
  );

  const mindMapData = useMemo(
    () => buildMindMapTree(selectedProject),
    [selectedProject],
  );

  const mindMapOptions = useMemo(() => {
    if (!mindMapData) return null;

    const options = {
      type: "linear",
      autoFit: "view",
      data: mindMapData,
      defaultExpandLevel: 1,
      labelField: (datum) => datum?.data?.title || datum?.id,
      node: {
        style: {
          component: (datum) => {
            const label = datum?.data?.title || datum?.id || "";
            const color = datum?.style?.color;

            if (datum?.depth === 0) {
              return (
                <TextNode
                  type="filled"
                  text={label}
                  color="#f1f4f5"
                  style={{ color: "#252525" }}
                />
              );
            }

            return (
              <TextNode
                type="underlined"
                text={label}
                color={color}
                style={{ backgroundColor: "transparent" }}
              />
            );
          },
        },
      },
      transforms: updateCollapseExpandBehavior({
        enable: true,
        iconRender: (isCollapsed) => (
          <PlusMinusIcon isCollapsed={isCollapsed} />
        ),
        iconOffsetX: 8,
      }),
    };

    return options;
  }, [mindMapData]);

  if (!selectedProject) {
    return (
      <div className="mindmap-empty-state">
        <Empty description="Open a project to view the mind map" />
      </div>
    );
  }

  return (
    <div className="project-mindmap-panel">
      <div className="mindmap-header">
        <div>
          <Title level={5} style={{ margin: 0, color: "#d9e2dc" }}>
            Project Mind Map
          </Title>
          <Text style={{ color: "rgba(255,255,255,0.65)" }}>
            Root project, milestone branches, and task leaves only.
          </Text>
        </div>
        <Space wrap>
          <Tag color="blue">{projectSummary.totalMilestones} Milestones</Tag>
          <Tag color="green">{projectSummary.workDone} Done</Tag>
          <Tag color="gold">{projectSummary.remainingWork} Remaining</Tag>
        </Space>
      </div>

      <div className="mindmap-canvas-wrapper">
        <div className="mindmap-canvas">
          {mindMapOptions ? <MindMap {...mindMapOptions} /> : null}
        </div>
      </div>
    </div>
  );
}

export default ProjectMindMap;
