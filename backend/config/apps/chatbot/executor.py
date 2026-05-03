"""Executes validated schema plans against the database."""
from datetime import datetime
from django.contrib.auth import get_user_model

User = get_user_model()


def _parse_date(date_str):
    """Convert date string to date object."""
    if not date_str or not isinstance(date_str, str):
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Invalid date format: {}. Expected YYYY-MM-DD".format(date_str))


def _resolve_project(project_id_or_name, user):
    """Resolve project by ID (int) or name (str)."""
    from projects.models import Projects
    if isinstance(project_id_or_name, int) or (isinstance(project_id_or_name, str) and project_id_or_name.isdigit()):
        return Projects.objects.get(id=int(project_id_or_name), owner_id=user)
    else:
        return Projects.objects.get(project_name=project_id_or_name, owner_id=user)


def _resolve_milestone(milestone_id_or_name, project):
    """Resolve milestone by ID (int) or title (str)."""
    from milestones.models import Milestone
    if isinstance(milestone_id_or_name, int) or (isinstance(milestone_id_or_name, str) and milestone_id_or_name.isdigit()):
        return Milestone.objects.get(id=int(milestone_id_or_name), project=project)
    else:
        return Milestone.objects.get(title=milestone_id_or_name, project=project)


def _resolve_task(task_id_or_name, user, project=None):
    """Resolve task by ID (int) or title (str)."""
    from tasks.models import Task
    queryset = Task.objects.filter(project__owner_id=user)
    if project:
        queryset = queryset.filter(project=project)
    if isinstance(task_id_or_name, int) or (isinstance(task_id_or_name, str) and task_id_or_name.isdigit()):
        return queryset.get(id=int(task_id_or_name))
    else:
        return queryset.get(title=task_id_or_name)


def execute_operation(planned_schema, user):
    """Execute a validated schema plan against the database."""
    operation = planned_schema.get("operation")
    payload = planned_schema.get("payload", {})

    if operation == "CREATE_PROJECT":
        return _create_project(payload, user)
    elif operation == "CREATE_TASK":
        return _create_task(payload, user)
    elif operation == "CREATE_MILESTONE":
        return _create_milestone(payload, user)
    elif operation == "UPDATE_PROJECT":
        return _update_project(payload, user)
    elif operation == "UPDATE_TASK":
        return _update_task(payload, user)
    elif operation == "UPDATE_MILESTONE":
        return _update_milestone(payload, user)
    elif operation == "READ":
        return _read_data(payload, user)
    elif operation == "DELETE":
        return _delete_item(payload, user)
    elif operation == "ADD_MEMBER":
        return _add_member(payload, user)
    elif operation == "REMOVE_MEMBER":
        return _remove_member(payload, user)
    elif operation == "UPDATE_MEMBER_ROLE":
        return _update_member_role(payload, user)
    elif operation == "DELETE_MILESTONE":
        return _delete_milestone(payload, user)
    elif operation == "DELETE_TASKS_BY_PROJECT":
        return _delete_tasks_by_project(payload, user)
    elif operation == "DELETE_TASKS_BY_MILESTONE":
        return _delete_tasks_by_milestone(payload, user)
    elif operation == "SHOW_MEMBERS":
        return _show_members(payload, user)
    else:
        return {"error": "Unknown operation: {}".format(operation)}


def _create_project(payload, user):
    from projects.models import Projects

    try:
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


def _create_task(payload, user):
    from projects.models import Projects, TeamMembers
    from milestones.models import Milestone
    from tasks.models import Task

    try:
        project = _resolve_project(payload.get("project_id"), user)

        milestone = None
        if payload.get("milestone_id"):
            milestone = _resolve_milestone(payload.get("milestone_id"), project)

        assignee = None
        if payload.get("assignee_id"):
            assignee = TeamMembers.objects.get(id=payload.get("assignee_id"), project=project)

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


def _create_milestone(payload, user):
    from projects.models import Projects
    from milestones.models import Milestone

    try:
        project = _resolve_project(payload.get("project_id"), user)
        milestone = Milestone.objects.create(
            title=payload.get("title", ""),
            description=payload.get("description", ""),
            start_date=_parse_date(payload.get("start_date")),
            due_date=_parse_date(payload.get("due_date")),
            project=project,
        )
        return {
            "success": True,
            "milestone_id": milestone.id,
            "title": milestone.title,
        }
    except Projects.DoesNotExist:
        return {"error": "Project not found"}
    except Exception as e:
        return {"error": "Failed to create milestone: {}".format(str(e))}


def _update_project(payload, user):
    from projects.models import Projects

    try:
        project = _resolve_project(payload.get("project_id"), user)
        updates = payload.get("updates", {})
        for key, value in updates.items():
            if hasattr(project, key):
                setattr(project, key, value)
        project.save()
        return {
            "success": True,
            "project_id": project.id,
            "project_name": project.project_name,
        }
    except Projects.DoesNotExist:
        return {"error": "Project not found"}
    except Exception as e:
        return {"error": "Failed to update project: {}".format(str(e))}


def _update_task(payload, user):
    from tasks.models import Task

    try:
        task_id_or_name = payload.get("task_id")
        task = _resolve_task(task_id_or_name, user)
        updates = payload.get("updates", {})
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


def _update_milestone(payload, user):
    try:
        milestone_id_or_name = payload.get("milestone_id")
        project = _resolve_project(payload.get("project_id"), user)
        milestone = _resolve_milestone(milestone_id_or_name, project)
        updates = payload.get("updates", {})
        for key, value in updates.items():
            if hasattr(milestone, key):
                setattr(milestone, key, value)
        milestone.save()
        return {
            "success": True,
            "milestone_id": milestone.id,
            "title": milestone.title,
        }
    except Exception as e:
        return {"error": "Failed to update milestone: {}".format(str(e))}


def _read_data(payload, user):
    from projects.models import Projects
    from tasks.models import Task
    from milestones.models import Milestone
    from notifications.models import Notification
    from projects.models import TeamMembers

    query_type = payload.get("query_type", "")
    project_filter = payload.get("project_filter", "")
    milestone_filter = payload.get("milestone_filter", "")
    member_filter = payload.get("member_filter", "")

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
            if milestone_filter:
                tasks = tasks.filter(milestone__title__icontains=milestone_filter)
            results = [{"id": t.id, "title": t.title, "status": t.status} for t in tasks]
            return {"success": True, "tasks": results}

        elif query_type == "milestones":
            milestones = Milestone.objects.filter(project__owner_id=user)
            if project_filter:
                milestones = milestones.filter(project__project_name__icontains=project_filter)
            results = [{"id": m.id, "title": m.title, "status": m.status} for m in milestones]
            return {"success": True, "milestones": results}

        elif query_type == "notifications":
            notifications = Notification.objects.filter(recipient=user, is_read=False)
            results = [{"id": n.id, "message": n.message, "created_at": str(n.created_at)} for n in notifications]
            return {"success": True, "notifications": results}

        elif query_type == "project_members":
            project = _resolve_project(payload.get("project_id"), user)
            members = TeamMembers.objects.filter(project=project)
            if member_filter == "available":
                members = members.filter(availability="available")
            results = [{"id": m.id, "username": m.user.username, "role": m.role} for m in members]
            return {"success": True, "members": results}

        elif query_type == "project_milestones":
            project = _resolve_project(payload.get("project_id"), user)
            milestones = Milestone.objects.filter(project=project)
            results = [{"id": m.id, "title": m.title, "status": m.status} for m in milestones]
            return {"success": True, "milestones": results}

        elif query_type == "milestone_tasks":
            milestone = _resolve_milestone(payload.get("milestone_id"), _resolve_project(payload.get("project_id"), user))
            tasks = Task.objects.filter(milestone=milestone)
            results = [{"id": t.id, "title": t.title, "status": t.status} for t in tasks]
            return {"success": True, "tasks": results}

        elif query_type == "member_tasks":
            member = TeamMembers.objects.get(id=payload.get("member_id"), project__owner_id=user)
            tasks = Task.objects.filter(assignee=member, project__owner_id=user)
            results = [{"id": t.id, "title": t.title, "status": t.status} for t in tasks]
            return {"success": True, "tasks": results}

        else:
            return {"error": "Unknown query type: {}".format(query_type)}

    except Exception as e:
        return {"error": "Failed to read data: {}".format(str(e))}


def _delete_item(payload, user):
    from projects.models import Projects
    from tasks.models import Task
    from milestones.models import Milestone

    delete_type = payload.get("delete_type", "")

    try:
        if delete_type == "project":
            if payload.get("delete_all"):
                projects = Projects.objects.filter(owner_id=user)
                count = projects.count()
                projects.delete()
                return {"success": True, "deleted": "projects", "count": count}
            else:
                project = _resolve_project(payload.get("project_id"), user)
                project_name = project.project_name
                project.delete()
                return {"success": True, "deleted": "project", "name": project_name}

        elif delete_type == "task":
            if payload.get("delete_all"):
                tasks = Task.objects.filter(project__owner_id=user)
                count = tasks.count()
                tasks.delete()
                return {"success": True, "deleted": "tasks", "count": count}
            else:
                task_id_or_name = payload.get("task_id")
                task = _resolve_task(task_id_or_name, user)
                task_title = task.title
                task.delete()
                return {"success": True, "deleted": "task", "name": task_title}

        elif delete_type == "milestone":
            if payload.get("delete_all") and payload.get("project_id"):
                project = _resolve_project(payload.get("project_id"), user)
                milestones = Milestone.objects.filter(project=project)
                count = milestones.count()
                milestones.delete()
                return {"success": True, "deleted": "milestones", "count": count, "project": project.project_name}
            else:
                milestone_id = payload.get("milestone_id")
                milestone = Milestone.objects.get(id=milestone_id, project__owner_id=user)
                title = milestone.title
                milestone.delete()
                return {"success": True, "deleted": "milestone", "title": title}

        else:
            return {"error": "Unknown delete type: {}".format(delete_type)}

    except Projects.DoesNotExist:
        return {"error": "Project not found"}
    except Task.DoesNotExist:
        return {"error": "Task not found"}
    except Exception as e:
        return {"error": "Failed to delete: {}".format(str(e))}


def _add_member(payload, user):
    from projects.models import Projects, TeamMembers
    from django.contrib.auth import get_user_model

    User = get_user_model()

    try:
        project = _resolve_project(payload.get("project_id"), user)
        user_id_or_name = payload.get("user_id")
        role = payload.get("role", "developer")

        if isinstance(user_id_or_name, str) and not user_id_or_name.isdigit():
            member_user = User.objects.get(username=user_id_or_name)
        else:
            member_user = User.objects.get(id=int(user_id_or_name))

        TeamMembers.objects.create(
            project=project,
            user=member_user,
            role=role,
        )
        return {
            "success": True,
            "project": project.project_name,
            "user": member_user.username,
            "role": role,
        }
    except Projects.DoesNotExist:
        return {"error": "Project not found"}
    except User.DoesNotExist:
        return {"error": "User not found"}
    except Exception as e:
        return {"error": "Failed to add member: {}".format(str(e))}


def _remove_member(payload, user):
    from projects.models import Projects, TeamMembers
    try:
        project = _resolve_project(payload.get("project_id"), user)
        member_id = payload.get("member_id")
        member = TeamMembers.objects.get(id=member_id, project=project)
        username = member.user.username
        member.delete()
        return {"success": True, "removed": username, "project": project.project_name}
    except TeamMembers.DoesNotExist:
        return {"error": "Member not found"}
    except Exception as e:
        return {"error": "Failed to remove member: {}".format(str(e))}


def _update_member_role(payload, user):
    from projects.models import Projects, TeamMembers
    try:
        project = _resolve_project(payload.get("project_id"), user)
        member_id = payload.get("member_id")
        new_role = payload.get("role", "developer")
        member = TeamMembers.objects.get(id=member_id, project=project)
        member.role = new_role
        member.save()
        return {"success": True, "member": member.user.username, "new_role": new_role}
    except TeamMembers.DoesNotExist:
        return {"error": "Member not found"}
    except Exception as e:
        return {"error": "Failed to update member role: {}".format(str(e))}


def _delete_milestone(payload, user):
    try:
        milestone_id_or_name = payload.get("milestone_id")
        project = _resolve_project(payload.get("project_id"), user)
        milestone = _resolve_milestone(milestone_id_or_name, project)
        title = milestone.title
        milestone.delete()
        return {"success": True, "deleted": "milestone", "title": title}
    except Exception as e:
        return {"error": "Failed to delete milestone: {}".format(str(e))}


def _delete_tasks_by_project(payload, user):
    from projects.models import Projects
    from tasks.models import Task
    try:
        project = _resolve_project(payload.get("project_id"), user)
        tasks = Task.objects.filter(project=project)
        count = tasks.count()
        tasks.delete()
        return {"success": True, "deleted": "tasks", "count": count, "project": project.project_name}
    except Projects.DoesNotExist:
        return {"error": "Project not found"}
    except Exception as e:
        return {"error": "Failed to delete tasks: {}".format(str(e))}


def _delete_tasks_by_milestone(payload, user):
    from milestones.models import Milestone
    from tasks.models import Task
    try:
        milestone = _resolve_milestone(payload.get("milestone_id"), _resolve_project(payload.get("project_id"), user))
        tasks = Task.objects.filter(milestone=milestone)
        count = tasks.count()
        tasks.delete()
        return {"success": True, "deleted": "tasks", "count": count, "milestone": milestone.title}
    except Exception as e:
        return {"error": "Failed to delete tasks: {}".format(str(e))}


def _show_members(payload, user):
    from projects.models import Projects, TeamMembers
    try:
        project = _resolve_project(payload.get("project_id"), user)
        members = TeamMembers.objects.filter(project=project)
        filter_by = payload.get("member_filter", "")
        if filter_by == "available":
            members = members.filter(availability="available")
        results = [{"id": m.id, "username": m.user.username, "role": m.role, "availability": getattr(m, "availability", "N/A")} for m in members]
        return {"success": True, "members": results, "project": project.project_name}
    except Projects.DoesNotExist:
        return {"error": "Project not found"}
    except Exception as e:
        return {"error": "Failed to show members: {}".format(str(e))}
