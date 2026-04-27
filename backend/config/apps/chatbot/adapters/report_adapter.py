from config.apps.chatbot.adapters.base import BaseAdapter, BaseAdapterError
from config.apps.projects.models import Projects
from config.apps.tasks.models import Task
from config.apps.milestones.models import Milestone
from config.apps.risks.models import Risk


class ReportAdapter(BaseAdapter):
    def generate(self, parameters: dict, user_context: dict) -> dict:
        if "project_id" not in parameters:
            raise BaseAdapterError("project_id is required")

        project_id = self._parse_int(parameters["project_id"], "project_id")
        try:
            project = Projects.objects.get(pk=project_id)
        except Projects.DoesNotExist:
            raise BaseAdapterError(f"Project with id {project_id} not found")

        tasks = Task.objects.filter(project=project)
        milestones = Milestone.objects.filter(project=project)
        risks = Risk.objects.filter(project=project)

        task_stats = {
            "total": tasks.count(),
            "todo": tasks.filter(status=Task.STATUS_TODO).count(),
            "in_progress": tasks.filter(status=Task.STATUS_IN_PROGRESS).count(),
            "done": tasks.filter(status=Task.STATUS_DONE).count(),
            "blocked": tasks.filter(status=Task.STATUS_BLOCKED).count(),
        }

        milestone_stats = {
            "total": milestones.count(),
            "planned": milestones.filter(status=Milestone.STATUS_PLANNED).count(),
            "in_progress": milestones.filter(status=Milestone.STATUS_IN_PROGRESS).count(),
            "completed": milestones.filter(status=Milestone.STATUS_COMPLETED).count(),
            "delayed": milestones.filter(status=Milestone.STATUS_DELAYED).count(),
        }

        risk_stats = {
            "total": risks.count(),
            "low": risks.filter(severity=Risk.SEVERITY_LOW).count(),
            "medium": risks.filter(severity=Risk.SEVERITY_MEDIUM).count(),
            "high": risks.filter(severity=Risk.SEVERITY_HIGH).count(),
            "critical": risks.filter(severity=Risk.SEVERITY_CRITICAL).count(),
            "open": risks.filter(status=Risk.STATUS_OPEN).count(),
            "mitigated": risks.filter(status=Risk.STATUS_MITIGATED).count(),
            "closed": risks.filter(status=Risk.STATUS_CLOSED).count(),
        }

        return {
            "project": self._to_dict(project),
            "overview": {
                "progress": project.progress,
                "status": project.status,
                "task_completion_rate": self._calculate_completion_rate(task_stats),
            },
            "tasks": task_stats,
            "milestones": milestone_stats,
            "risks": risk_stats,
        }

    def _calculate_completion_rate(self, task_stats: dict) -> float:
        total = task_stats.get("total", 0)
        if total == 0:
            return 0.0
        done = task_stats.get("done", 0)
        return round((done / total) * 100, 2)