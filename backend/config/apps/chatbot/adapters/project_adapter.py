from typing import Optional
from django.contrib.auth import get_user_model
from django.db import IntegrityError, OperationalError
from django.db.models import Q

from config.apps.chatbot.adapters.base import BaseAdapter, BaseAdapterError
from config.apps.projects.models import Projects, TeamMembers

User = get_user_model()


FIELD_HELP_MESSAGES = {
    "project_name": "What would you like to name the project?",
    "project_description": "Could you provide a description for the project?",
    "status": "What status should the project have? (active, on_track, at_risk, complete)",
    "start_date": "When should the project start? (YYYY-MM-DD format)",
    "due_date": "When should the project be due? (YYYY-MM-DD format)",
}

MISSING_FIELD_PROMPTS = {
    "start_date": "Sure! Could you specify a start date for the project? (YYYY-MM-DD)",
    "due_date": "Got it! What's the due date for this project? (YYYY-MM-DD)",
}


class ProjectAdapter(BaseAdapter):
    def create(self, parameters: dict, user_context: dict) -> dict:
        required_fields = ["project_name"]
        errors = self._validate_params(parameters, required_fields)
        if errors:
            raise BaseAdapterError(", ".join(errors), missing_fields=errors)

        owner_id = user_context.get("user_id")
        if not owner_id:
            raise BaseAdapterError("User context must include user_id")

        try:
            owner = User.objects.get(pk=owner_id)
        except User.DoesNotExist:
            raise BaseAdapterError(f"User with id {owner_id} not found")

        start_date = parameters.get("start_date")
        due_date = parameters.get("due_date")

        project_name = parameters.get("project_name", "Untitled Project")
        project_description = parameters.get("project_description") or project_name

        try:
            project = Projects.objects.create(
                project_name=project_name,
                project_description=project_description,
                status=parameters.get("status", "active"),
                progress=parameters.get("progress", 0),
                start_date=self._parse_date(start_date) if start_date else None,
                due_date=self._parse_date(due_date) if due_date else None,
                owner_id=owner,
            )
        except (IntegrityError, OperationalError) as e:
            error_msg = str(e)
            if "start_date" in error_msg.lower() or "NOT NULL" in error_msg:
                raise BaseAdapterError(
                    "Could you specify a start date for the project?",
                    missing_fields=["start_date"]
                )
            elif "due_date" in error_msg.lower():
                raise BaseAdapterError(
                    "Could you specify a due date for the project?",
                    missing_fields=["due_date"]
                )
            raise BaseAdapterError(f"I had trouble creating the project: {error_msg}")

        team_members = parameters.get("team_members", [])
        for member_data in team_members:
            user_id = member_data.get("user_id") or member_data.get("id")
            role = member_data.get("role", "member")
            if user_id:
                try:
                    user = User.objects.get(pk=user_id)
                    TeamMembers.objects.create(
                        Projects=project,
                        user=user,
                        role=role,
                    )
                except User.DoesNotExist:
                    continue

        return self._to_dict(project)

    def update(self, parameters: dict, user_context: dict) -> dict:
        project_id = parameters.get("pk") or parameters.get("project_id")
        if not project_id:
            raise BaseAdapterError("pk or project_id is required")

        project = self._safe_get(Projects, project_id, "Project")

        if "project_name" in parameters:
            project.project_name = parameters["project_name"]
        if "project_description" in parameters:
            project.project_description = parameters["project_description"]
        if "status" in parameters:
            project.status = parameters["status"]
        if "progress" in parameters:
            project.progress = self._parse_int(parameters["progress"], "progress")
        if "start_date" in parameters:
            project.start_date = self._parse_date(parameters["start_date"])
        if "due_date" in parameters:
            project.due_date = self._parse_date(parameters["due_date"])

        if "team_members" in parameters:
            project.teamMembers.all().delete()
            for member_data in parameters["team_members"]:
                user_id = member_data.get("user_id") or member_data.get("id")
                role = member_data.get("role", "member")
                if user_id:
                    try:
                        user = User.objects.get(pk=user_id)
                        TeamMembers.objects.create(
                            Projects=project,
                            user=user,
                            role=role,
                        )
                    except User.DoesNotExist:
                        continue

        project.save()
        return self._to_dict(project)

    def delete(self, parameters: dict, user_context: dict) -> dict:
        project_id = parameters.get("pk") or parameters.get("project_id")
        if not project_id:
            raise BaseAdapterError("pk or project_id is required")

        project = self._safe_get(Projects, project_id, "Project")
        return self._safe_delete(project, "Project")

    def list(self, parameters: dict, user_context: dict) -> dict:
        queryset = Projects.objects.select_related("owner_id").prefetch_related("teamMembers").all()

        status_filter = parameters.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        project_id = parameters.get("project_id") or parameters.get("pk")
        if project_id:
            queryset = queryset.filter(pk=project_id)

        projects = list(queryset)
        return {
            "projects": [self._to_dict(p) for p in projects],
            "count": len(projects),
        }