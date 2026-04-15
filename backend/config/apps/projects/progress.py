from tasks.models import Task


COMPLETED_TASK_STATUSES = {"done", "completed", "complete", "closed"}


def recalculate_project_progress(project):
    """Update project.progress based on completed tasks / total tasks."""
    total_tasks = Task.objects.filter(project=project).count()

    if total_tasks == 0:
        progress = 0
    else:
        completed_tasks = Task.objects.filter(
            project=project,
            status__in=COMPLETED_TASK_STATUSES,
        ).count()
        progress = round((completed_tasks / total_tasks) * 100)

    if project.progress != progress:
        project.progress = progress
        project.save(update_fields=["progress"])

    return progress
