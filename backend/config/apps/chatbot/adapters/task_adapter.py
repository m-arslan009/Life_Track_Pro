from typing import Optional
from django.contrib.auth import get_user_model

from config.apps.chatbot.adapters.base import BaseAdapter, BaseAdapterError
from config.apps.tasks.models import Task
from config.apps.projects.models import Projects, TeamMembers
from config.apps.milestones.models import Milestone

User = get_user_model()


class TaskAdapter(BaseAdapter):
    def create(self, parameters: dict, user_context: dict) -> dict:
        required_fields = ["title", "project", "milestone"]
        errors = self._validate_params(parameters, required_fields)
        if errors:
            raise BaseAdapterError(", ".join(errors))

        project_id = self._parse_int(parameters["project"], "project")
        milestone_id = self._parse_int(parameters["milestone"], "milestone")

        try:
            project = Projects.objects.get(pk=project_id)
        except Projects.DoesNotExist:
            raise BaseAdapterError(f"Project with id {project_id} not found")

        try:
            milestone = Milestone.objects.get(pk=milestone_id)
        except Milestone.DoesNotExist:
            raise BaseAdapterError(f"Milestone with id {milestone_id} not found")

        assignee = None
        assignee_id = parameters.get("assignee")
        if assignee_id:
            try:
                assignee = TeamMembers.objects.get(pk=self._parse_int(assignee_id, "assignee"))
            except TeamMembers.DoesNotExist:
                pass

        task = Task.objects.create(
            title=parameters["title"],
            description=parameters.get("description", ""),
            status=parameters.get("status", Task.STATUS_TODO),
            project=project,
            milestone=milestone,
            assignee=assignee,
        )

        return self._to_dict(task)

    def update(self, parameters: dict, user_context: dict) -> dict:
        if "pk" not in parameters:
            raise BaseAdapterError("pk is required")

        task = self._safe_get(Task, parameters["pk"], "Task")

        if "title" in parameters:
            task.title = parameters["title"]
        if "description" in parameters:
            task.description = parameters["description"]
        if "status" in parameters:
            task.status = parameters["status"]

        if "project" in parameters:
            project_id = self._parse_int(parameters["project"], "project")
            try:
                task.project = Projects.objects.get(pk=project_id)
            except Projects.DoesNotExist:
                raise BaseAdapterError(f"Project with id {project_id} not found")

        if "milestone" in parameters:
            milestone_id = self._parse_int(parameters["milestone"], "milestone")
            try:
                task.milestone = Milestone.objects.get(pk=milestone_id)
            except Milestone.DoesNotExist:
                raise BaseAdapterError(f"Milestone with id {milestone_id} not found")

        if "assignee" in parameters:
            assignee_id = parameters.get("assignee")
            if assignee_id:
                try:
                    task.assignee = TeamMembers.objects.get(pk=self._parse_int(assignee_id, "assignee"))
                except TeamMembers.DoesNotExist:
                    task.assignee = None
            else:
                task.assignee = None

        task.save()
        return self._to_dict(task)

    def delete(self, parameters: dict, user_context: dict) -> dict:
        task_id = parameters.get("pk") or parameters.get("task_id")
        if not task_id:
            raise BaseAdapterError("pk or task_id is required")

        task = self._safe_get(Task, task_id, "Task")
        return self._safe_delete(task, "Task")

    def list(self, parameters: dict, user_context: dict) -> dict:
        queryset = Task.objects.select_related("project", "milestone", "assignee").all()

        project_id = parameters.get("project")
        if project_id:
            project_id = self._parse_int(project_id, "project")
            queryset = queryset.filter(project_id=project_id)

        status_filter = parameters.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        task_id = parameters.get("task_id") or parameters.get("pk")
        if task_id:
            queryset = queryset.filter(pk=self._parse_int(task_id, "task_id"))

        tasks = list(queryset)
        return {
            "tasks": [self._to_dict(t) for t in tasks],
            "count": len(tasks),
        }