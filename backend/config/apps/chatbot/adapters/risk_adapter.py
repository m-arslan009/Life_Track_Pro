from django.contrib.auth import get_user_model

from config.apps.chatbot.adapters.base import BaseAdapter, BaseAdapterError
from config.apps.risks.models import Risk
from config.apps.projects.models import Projects

User = get_user_model()


class RiskAdapter(BaseAdapter):
    def create(self, parameters: dict, user_context: dict) -> dict:
        required_fields = ["project_id", "description"]
        errors = self._validate_params(parameters, required_fields)
        if errors:
            raise BaseAdapterError(", ".join(errors))

        project_id = self._parse_int(parameters["project_id"], "project_id")
        try:
            project = Projects.objects.get(pk=project_id)
        except Projects.DoesNotExist:
            raise BaseAdapterError(f"Project with id {project_id} not found")

        user_id = user_context.get("user_id")
        identified_by = None
        if user_id:
            try:
                identified_by = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                pass

        risk = Risk.objects.create(
            description=parameters["description"],
            severity=parameters.get("severity", Risk.SEVERITY_MEDIUM),
            project=project,
            identified_by=identified_by,
        )

        return self._to_dict(risk)