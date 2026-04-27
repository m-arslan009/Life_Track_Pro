from config.apps.chatbot.adapters.base import BaseAdapter, BaseAdapterError
from config.apps.milestones.models import Milestone
from config.apps.projects.models import Projects


class MilestoneAdapter(BaseAdapter):
    def get(self, parameters: dict, user_context: dict) -> dict:
        if "project" not in parameters:
            raise BaseAdapterError("project is required")

        project_id = self._parse_int(parameters["project"], "project")
        try:
            project = Projects.objects.get(pk=project_id)
        except Projects.DoesNotExist:
            raise BaseAdapterError(f"Project with id {project_id} not found")

        queryset = Milestone.objects.filter(project=project)

        status_filter = parameters.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        milestone_id = parameters.get("milestone_id")
        if milestone_id:
            queryset = queryset.filter(pk=self._parse_int(milestone_id, "milestone_id"))

        milestones = list(queryset)
        return {
            "milestones": [self._to_dict(m) for m in milestones],
            "count": len(milestones),
        }