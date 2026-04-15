const COMPLETED_TASK_STATUSES = new Set([
  "done",
  "completed",
  "complete",
  "closed",
]);

const normalizeText = (value) => String(value || "").trim();

export const isTaskComplete = (task) =>
  COMPLETED_TASK_STATUSES.has(normalizeText(task?.status).toLowerCase());

export const getMilestoneWorkSummary = (milestone) => {
  const tasks = milestone?.tasks || milestone?.milestone_tasks || [];
  const totalWork = tasks.length;
  const workDone = tasks.filter(isTaskComplete).length;
  const remainingWork = Math.max(totalWork - workDone, 0);
  const completionPercent = totalWork
    ? Math.round((workDone / totalWork) * 100)
    : 0;

  return {
    workDone,
    totalWork,
    remainingWork,
    completionPercent,
  };
};

export const getProjectWorkSummary = (project) => {
  const milestones = project?.milestones || [];
  const milestoneSummaries = milestones.map((milestone) => ({
    milestone,
    ...getMilestoneWorkSummary(milestone),
  }));

  const totalWork = milestoneSummaries.reduce(
    (sum, milestoneSummary) => sum + milestoneSummary.totalWork,
    0,
  );
  const workDone = milestoneSummaries.reduce(
    (sum, milestoneSummary) => sum + milestoneSummary.workDone,
    0,
  );
  const remainingWork = Math.max(totalWork - workDone, 0);
  const completionPercent = totalWork
    ? Math.round((workDone / totalWork) * 100)
    : 0;
  const completedMilestones = milestoneSummaries.filter(
    (item) => item.totalWork > 0 && item.workDone === item.totalWork,
  ).length;

  return {
    milestoneSummaries,
    workDone,
    totalWork,
    remainingWork,
    completionPercent,
    totalMilestones: milestones.length,
    completedMilestones,
  };
};

export const buildMindMapDisplayLines = (node) => {
  const lines = [normalizeText(node?.title || node?.id)];

  if (node?.progressLabel) {
    lines.push(node.progressLabel);
  }

  if (Array.isArray(node?.members) && node.members.length > 0) {
    lines.push(`Users: ${node.members.join(", ")}`);
  }

  if (node?.description) {
    lines.push(node.description);
  }

  return lines;
};

export const estimateMindMapNodeSize = (node) => {
  const lines = buildMindMapDisplayLines(node);
  const longestLineLength = lines.reduce(
    (longest, line) => Math.max(longest, normalizeText(line).length),
    0,
  );
  const width = Math.max(
    node?.nodeType === "project" ? 280 : 220,
    Math.min(460, longestLineLength * 8 + 56),
  );
  const height = Math.max(
    node?.nodeType === "project" ? 96 : 76,
    lines.length * 18 + 24,
  );

  return [width, height];
};

export const buildProjectMindMapTree = (project, teamMemberLabelById) => {
  if (!project) return null;

  const projectSummary = getProjectWorkSummary(project);
  const milestones = project?.milestones || [];

  return {
    id: `project-${project.id}`,
    title: project.project_name,
    nodeType: "project",
    description: project.project_description || "No project description",
    progressLabel: `${projectSummary.workDone}/${projectSummary.totalWork} work items complete`,
    members:
      project.teamMembers?.map(
        (member) =>
          teamMemberLabelById.get(member.id) ||
          `${member.user?.first_name || member.user?.username || "User"} ${member.user?.last_name || ""}`.trim(),
      ) || [],
    summary: projectSummary,
    children: milestones.map((milestone) => {
      const milestoneSummary = getMilestoneWorkSummary(milestone);
      const milestoneMembers = (
        milestone.teamMembers ||
        milestone.team_members ||
        []
      ).map(
        (memberId) => teamMemberLabelById.get(memberId) || `Member ${memberId}`,
      );

      return {
        id: `milestone-${milestone.id}`,
        title: milestone.title,
        nodeType: "milestone",
        description:
          `${milestone.start_date || ""} - ${milestone.due_date || ""}`.trim(),
        progressLabel: `${milestoneSummary.workDone}/${milestoneSummary.totalWork} tasks complete`,
        members: milestoneMembers,
        summary: milestoneSummary,
        children: (milestone.tasks || milestone.milestone_tasks || []).map(
          (task) => {
            const assigneeLabel = task.assignee
              ? teamMemberLabelById.get(task.assignee) ||
                `Member ${task.assignee}`
              : "Unassigned";

            return {
              id: `task-${task.id}`,
              title: task.title,
              nodeType: "task",
              description: task.status || "todo",
              progressLabel: `Assignee: ${assigneeLabel}`,
              assignee: assigneeLabel,
              status: task.status || "todo",
              children: [],
            };
          },
        ),
      };
    }),
  };
};
