from collections import defaultdict
from datetime import date

from django.db.models import Avg, Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.apps.milestones.models import Milestone
from config.apps.projects.models import Projects
from config.apps.tasks.models import Task


def _visible_projects(user):
	return Projects.objects.filter(
		Q(owner_id=user) | Q(teamMembers__user=user)
	).distinct()


def _month_start(year, month):
	return date(year, month, 1)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def reportsOverview(request):
	today = timezone.localdate()

	visible_projects = _visible_projects(request.user)
	active_projects = visible_projects.filter(status__in=["active", "on_track", "at_risk"])
	completed_projects = visible_projects.filter(status="complete")

	active_projects_annotated = (
		active_projects
		.annotate(
			milestone_count=Count("milestones", distinct=True),
			completed_milestone_count=Count(
				"milestones",
				filter=Q(milestones__status="completed"),
				distinct=True,
			),
			overdue_milestone_count=Count(
				"milestones",
				filter=Q(milestones__due_date__lt=today) & ~Q(milestones__status="completed"),
				distinct=True,
			),
			task_count=Count("tasks", distinct=True),
			completed_task_count=Count(
				"tasks",
				filter=Q(tasks__status="done"),
				distinct=True,
			),
			blocked_task_count=Count(
				"tasks",
				filter=Q(tasks__status="blocked"),
				distinct=True,
			),
		)
		.order_by("due_date", "-id")
	)

	task_scope = Task.objects.filter(project__in=visible_projects)
	milestone_scope = Milestone.objects.filter(project__in=visible_projects)

	task_status_counts = {
		"todo": task_scope.filter(status="todo").count(),
		"in_progress": task_scope.filter(status="in_progress").count(),
		"done": task_scope.filter(status="done").count(),
		"blocked": task_scope.filter(status="blocked").count(),
	}

	milestone_status_counts = {
		"planned": milestone_scope.filter(status="planned").count(),
		"in_progress": milestone_scope.filter(status="in_progress").count(),
		"completed": milestone_scope.filter(status="completed").count(),
		"delayed": milestone_scope.filter(status="delayed").count(),
	}

	total_tasks = sum(task_status_counts.values())
	completed_tasks = task_status_counts["done"]

	total_milestones = sum(milestone_status_counts.values())
	completed_milestones = milestone_status_counts["completed"]

	average_progress = (
		active_projects.aggregate(avg_progress=Avg("progress")).get("avg_progress") or 0
	)
	average_progress = round(float(average_progress), 1)

	overdue_projects = active_projects.filter(due_date__lt=today).count()
	at_risk_projects = active_projects.filter(status="at_risk").count()

	ongoing_issues = []
	project_summaries = []
	progress_chart = []

	for project in active_projects_annotated:
		days_remaining = None
		if project.due_date:
			days_remaining = (project.due_date - today).days

		task_completion_rate = (
			round((project.completed_task_count / project.task_count) * 100)
			if project.task_count
			else 0
		)
		milestone_completion_rate = (
			round((project.completed_milestone_count / project.milestone_count) * 100)
			if project.milestone_count
			else 0
		)

		is_overdue = bool(days_remaining is not None and days_remaining < 0)

		project_summaries.append(
			{
				"id": project.id,
				"project_name": project.project_name,
				"status": project.status,
				"progress": project.progress,
				"start_date": project.start_date,
				"due_date": project.due_date,
				"days_remaining": days_remaining,
				"is_overdue": is_overdue,
				"task_count": project.task_count,
				"completed_tasks": project.completed_task_count,
				"blocked_tasks": project.blocked_task_count,
				"milestone_count": project.milestone_count,
				"completed_milestones": project.completed_milestone_count,
				"overdue_milestones": project.overdue_milestone_count,
				"task_completion_rate": task_completion_rate,
				"milestone_completion_rate": milestone_completion_rate,
			}
		)

		progress_chart.append(
			{
				"project_name": project.project_name,
				"progress": project.progress,
				"status": project.status,
			}
		)

		if project.status == "at_risk":
			ongoing_issues.append(
				{
					"project_id": project.id,
					"project_name": project.project_name,
					"severity": "high",
					"issue_type": "delivery_risk",
					"message": "Project is marked at risk and needs immediate attention.",
				}
			)

		if is_overdue:
			ongoing_issues.append(
				{
					"project_id": project.id,
					"project_name": project.project_name,
					"severity": "high",
					"issue_type": "overdue_project",
					"message": "Project due date has passed but work is still ongoing.",
				}
			)

		if project.blocked_task_count > 0:
			ongoing_issues.append(
				{
					"project_id": project.id,
					"project_name": project.project_name,
					"severity": "medium",
					"issue_type": "blocked_tasks",
					"message": f"{project.blocked_task_count} blocked task(s) may slow delivery.",
				}
			)

		if project.overdue_milestone_count > 0:
			ongoing_issues.append(
				{
					"project_id": project.id,
					"project_name": project.project_name,
					"severity": "medium",
					"issue_type": "overdue_milestones",
					"message": f"{project.overdue_milestone_count} milestone(s) are past due.",
				}
			)

	severity_rank = {"high": 0, "medium": 1, "low": 2}
	ongoing_issues.sort(key=lambda issue: (severity_rank.get(issue["severity"], 9), issue["project_name"]))

	month_cursor = today.replace(day=1)
	month_points = []
	for _ in range(6):
		month_points.append(month_cursor)
		if month_cursor.month == 1:
			month_cursor = _month_start(month_cursor.year - 1, 12)
		else:
			month_cursor = _month_start(month_cursor.year, month_cursor.month - 1)
	month_points.reverse()

	task_trend_rows = (
		task_scope.filter(status="done", updated_at__date__gte=month_points[0])
		.annotate(month=TruncMonth("updated_at"))
		.values("month")
		.annotate(completed=Count("id"))
		.order_by("month")
	)

	completed_tasks_by_month = defaultdict(int)
	for row in task_trend_rows:
		month_value = row.get("month")
		if month_value:
			completed_tasks_by_month[month_value.date().isoformat()] = row["completed"]

	completed_projects_by_month = defaultdict(int)

	completion_trend = []
	for point in month_points:
		key = point.isoformat()
		completion_trend.append(
			{
				"month": point.strftime("%b %Y"),
				"completed_tasks": completed_tasks_by_month.get(key, 0),
				"completed_projects": completed_projects_by_month.get(key, 0),
			}
		)

	response_payload = {
		"summary": {
			"total_visible_projects": visible_projects.count(),
			"active_projects": active_projects.count(),
			"completed_projects": completed_projects.count(),
			"at_risk_projects": at_risk_projects,
			"overdue_projects": overdue_projects,
			"average_progress": average_progress,
			"task_completion_rate": round((completed_tasks / total_tasks) * 100, 1) if total_tasks else 0,
			"milestone_completion_rate": round((completed_milestones / total_milestones) * 100, 1)
			if total_milestones
			else 0,
			"blocked_tasks": task_status_counts["blocked"],
			"delayed_milestones": milestone_status_counts["delayed"],
		},
		"project_summaries": project_summaries,
		"ongoing_issues": ongoing_issues,
		"insights": [
			{
				"title": "Portfolio Health",
				"value": f"{average_progress}% average progress across active projects",
			},
			{
				"title": "Execution Signal",
				"value": f"{task_status_counts['blocked']} blocked task(s) and {milestone_status_counts['delayed']} delayed milestone(s)",
			},
			{
				"title": "Delivery Risk",
				"value": f"{overdue_projects} overdue project(s) and {at_risk_projects} at-risk project(s)",
			},
		],
		"charts": {
			"task_status": [
				{"status": "To Do", "value": task_status_counts["todo"]},
				{"status": "In Progress", "value": task_status_counts["in_progress"]},
				{"status": "Done", "value": task_status_counts["done"]},
				{"status": "Blocked", "value": task_status_counts["blocked"]},
			],
			"milestone_status": [
				{"status": "Planned", "value": milestone_status_counts["planned"]},
				{"status": "In Progress", "value": milestone_status_counts["in_progress"]},
				{"status": "Completed", "value": milestone_status_counts["completed"]},
				{"status": "Delayed", "value": milestone_status_counts["delayed"]},
			],
			"project_progress": progress_chart,
			"completion_trend": completion_trend,
		},
	}

	return Response(response_payload, status=status.HTTP_200_OK)
