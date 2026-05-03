"""Executes validated schema plans against the database."""
from datetime import datetime
from django.contrib.auth import get_user_model

User = get_user_model()


def _parse_date(date_str):
    """Convert date string to date object. Supports YYYY-MM-DD format."""
    if not date_str or not isinstance(date_str, str):
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Invalid date format: {}. Expected YYYY-MM-DD".format(date_str))


def execute_operation(planned_schema, user):
    """
    Execute a validated schema plan against the database.

    Args:
        planned_schema: Output from schema_planner.plan_schema()
        user: The authenticated Django user making the request.

    Returns:
        Dict with operation result or error
    """
    operation = planned_schema.get("operation")
    payload = planned_schema.get("payload", {})

    if operation == "CREATE_PROJECT":
        return _create_project(payload, user)
    elif operation == "CREATE_TASK":
        return _create_task(payload, user)
    elif operation == "UPDATE_TASK":
        return _update_task(payload, user)
    elif operation == "READ":
        return _read_data(payload, user)
    else:
        return {"error": "Unknown operation: {}".format(operation)}


def _create_project(payload, user):
    from projects.models import Projects

    try:
        # Convert date strings to date objects
        start_date = _parse_date(payload.get("start_date"))
        due_date = _parse_date(payload.get("due_date"))

        project = Projects.objects.create(
            project_name=payload.get("project_name"),
            project_description=payload.get("project_description", ""),
            status=payload.get("status", "active"),
            progress=payload.get("progress", 0),
            start_date=start_date,
            due_date=due_date,
            owner_id=user,
        )
        return {
            "success": True,
            "project_id": project.id,
            "project_name": project.project_name,
        }
    except Exception as e:
        return {"error": "Failed to create project: {}".format(str(e))}


def _resolve_project(project_id_or_name, user):
    """Resolve project by ID (int) or name (str)."""
    from projects.models import Projects
    if isinstance(project_id_or_name, int) or (isinstance(project_id_or_name, str) and project_id_or_name.isdigit()):
        return Projects.objects.get(id=int(project_id_or_name), owner_id=user)
    else:
        return Projects.objects.get(project_name=project_id_or_name, owner_id=user)


def _create_task(payload, user):
    from projects.models import Projects, TeamMembers
    from milestones.models import Milestone
    from tasks.models import Task

    try:
        project = _resolve_project(payload.get("project_id"), user)
        milestone = None
        if payload.get("milestone_id"):
            milestone = Milestone.objects.get(id=payload.get("milestone_id"), project=project)

        assignee = None
        if payload.get("assignee_id"):
            assignee = TeamMembers.objects.get(id=payload.get("assignee_id"), Projects=project)

        task = Task.objects.create(
            title=payload.get("title"),
            description=payload.get("description", ""),
            status=payload.get("status", "todo"),
            project=project,
            milestone=milestone,
            assignee=assignee,
        )
        return {
            "success": True,
            "task_id": task.id,
            "task_title": task.title,
        }
    except Projects.DoesNotExist:
        return {"error": "Project not found"}
    except Milestone.DoesNotExist:
        return {"error": "Milestone not found"}
    except TeamMembers.DoesNotExist:
        return {"error": "Team member not found"}
    except Exception as e:
        return {"error": "Failed to create task: {}".format(str(e))}


def _update_task(payload, user):
    from tasks.models import Task

    try:
        task_id = payload.get("task_id")
        updates = payload.get("updates", {})

        task = Task.objects.get(id=task_id)

        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)
        task.save()

        return {
            "success": True,
            "task_id": task.id,
            "task_title": task.title,
        }
    except Task.DoesNotExist:
        return {"error": "Task not found"}
    except Exception as e:
        return {"error": "Failed to update task: {}".format(str(e))}


def _read_data(payload, user):
    from projects.models import Projects
    from tasks.models import Task
    from milestones.models import Milestone

    query_type = payload.get("query_type", "")
    project_filter = payload.get("project_filter", "")

    try:
        if query_type == "projects":
            projects = Projects.objects.filter(owner_id=user)
            if project_filter:
                projects = projects.filter(project_name__icontains=project_filter)
            results = [{"id": p.id, "name": p.project_name, "status": p.status} for p in projects]
            return {"success": True, "projects": results}

        elif query_type == "tasks":
            tasks = Task.objects.filter(project__owner_id=user)
            if project_filter:
                tasks = tasks.filter(project__project_name__icontains=project_filter)
            results = [{"id": t.id, "title": t.title, "status": t.status} for t in tasks]
            return {"success": True, "tasks": results}

        elif query_type == "milestones":
            milestones = Milestone.objects.filter(project__owner_id=user)
            if project_filter:
                milestones = milestones.filter(project__project_name__icontains=project_filter)
            results = [{"id": m.id, "title": m.title, "status": m.status} for m in milestones]
            return {"success": True, "milestones": results}

        else:
            return {"error": "Unknown query type: {}".format(query_type)}

    except Exception as e:
        return {"error": "Failed to read data: {}".format(str(e))}
