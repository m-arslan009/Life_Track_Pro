from typing import Iterable, Optional

from config.apps.projects.models import TeamMembers

from .models import Notification


def _actor_label(actor) -> str:
    if not actor:
        return "System"

    full_name = f"{actor.first_name} {actor.last_name}".strip()
    return full_name or actor.username


def project_recipient_ids(project) -> list[int]:
    recipient_ids = {project.owner_id_id}
    member_ids = TeamMembers.objects.filter(Projects=project).values_list("user_id", flat=True)
    recipient_ids.update(member_ids)
    return list(recipient_ids)


def send_notification(
    *,
    user_ids: Iterable[int],
    notification_type: str,
    title: str,
    message: str,
    project=None,
    task=None,
    milestone=None,
) -> None:
    unique_ids = list({uid for uid in user_ids if uid})
    if not unique_ids:
        return

    notifications = [
        Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            project_id=getattr(project, "id", None),
            project_name=getattr(project, "project_name", None),
            task_id=getattr(task, "id", None),
            task_name=getattr(task, "title", None),
            milestone_id=getattr(milestone, "id", None),
            milestone_name=getattr(milestone, "title", None),
        )
        for user_id in unique_ids
    ]
    Notification.objects.bulk_create(notifications)


def notify_project_event(
    *,
    project,
    notification_type: str,
    title: str,
    message: str,
    recipients: Optional[Iterable[int]] = None,
    task=None,
    milestone=None,
) -> None:
    recipient_ids = list(recipients) if recipients is not None else project_recipient_ids(project)
    send_notification(
        user_ids=recipient_ids,
        notification_type=notification_type,
        title=title,
        message=message,
        project=project,
        task=task,
        milestone=milestone,
    )


def actor_message(actor, fallback: str) -> str:
    return f"{_actor_label(actor)} {fallback}"
