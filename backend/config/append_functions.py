"""Append new handler functions to executor.py"""
import sys

append_code = '''

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
    from milestones.models import Milestone
    try:
        milestone_id = payload.get("milestone_id")
        milestone = Milestone.objects.get(id=milestone_id, project__owner_id=user)
        title = milestone.title
        milestone.delete()
        return {"success": True, "deleted": "milestone", "title": title}
    except Milestone.DoesNotExist:
        return {"error": "Milestone not found"}
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
'''

with open('apps/chatbot/executor.py', 'a') as f:
    f.write(append_code)

print('Appended new functions successfully')
