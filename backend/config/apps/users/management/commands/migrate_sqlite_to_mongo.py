import datetime
import sqlite3
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from milestones.models import Milestone
from projects.models import Projects, TeamMembers
from users.models import User


def _parse_date(value):
    if not value:
        return None
    if isinstance(value, datetime.date):
        return value
    return datetime.date.fromisoformat(str(value)[:10])


def _table_exists(cursor, table_name):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", [table_name])
    return cursor.fetchone() is not None


class Command(BaseCommand):
    help = "Migrate legacy SQLite app data into MongoDB collections."

    def add_arguments(self, parser):
        parser.add_argument(
            "--sqlite-path",
            default=str(Path(settings.BASE_DIR) / "db.sqlite3"),
            help="Path to legacy SQLite database file.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing Mongo app data before import.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        sqlite_path = Path(options["sqlite_path"]).resolve()
        if not sqlite_path.exists():
            raise CommandError(f"SQLite file not found: {sqlite_path}")

        self.stdout.write(self.style.NOTICE(f"Reading SQLite database: {sqlite_path}"))

        conn = sqlite3.connect(str(sqlite_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if options["clear"]:
            self.stdout.write(self.style.WARNING("Clearing existing Mongo app data..."))
            Milestone.objects.all().delete()
            TeamMembers.objects.all().delete()
            Projects.objects.all().delete()
            User.objects.exclude(is_superuser=True).delete()

        legacy_user_map = {}
        legacy_project_map = {}

        users_count = self._migrate_users(cursor, legacy_user_map)
        projects_count = self._migrate_projects(cursor, legacy_user_map, legacy_project_map)
        members_count = self._migrate_team_members(cursor, legacy_user_map, legacy_project_map)
        milestones_count = self._migrate_milestones(cursor, legacy_project_map)

        conn.close()

        self.stdout.write(self.style.SUCCESS("SQLite to Mongo migration completed."))
        self.stdout.write(
            f"Imported users={users_count}, projects={projects_count}, team_members={members_count}, milestones={milestones_count}"
        )

    def _migrate_users(self, cursor, legacy_user_map):
        table_name = "users_user"
        if not _table_exists(cursor, table_name):
            self.stdout.write(self.style.WARNING(f"Skipping {table_name}: table not found."))
            return 0

        rows = cursor.execute(f"SELECT * FROM {table_name}").fetchall()
        imported = 0
        for row in rows:
            username = row["username"]
            defaults = {
                "email": row["email"] or f"{username}@example.com",
                "first_name": row["first_name"] or "",
                "last_name": row["last_name"] or "",
                "role": row["role"] if "role" in row.keys() and row["role"] else "developer",
                "account_status": row["account_status"] if "account_status" in row.keys() and row["account_status"] else "active",
                "is_staff": bool(row["is_staff"]),
                "is_active": bool(row["is_active"]),
                "is_superuser": bool(row["is_superuser"]),
                "last_login": row["last_login"],
                "date_joined": row["date_joined"],
            }

            user, _ = User.objects.update_or_create(username=username, defaults=defaults)
            if row["password"]:
                user.password = row["password"]
                user.save(update_fields=["password"])

            legacy_user_map[row["id"]] = user
            imported += 1

        return imported

    def _migrate_projects(self, cursor, legacy_user_map, legacy_project_map):
        table_name = "projects_projects"
        if not _table_exists(cursor, table_name):
            self.stdout.write(self.style.WARNING(f"Skipping {table_name}: table not found."))
            return 0

        rows = cursor.execute(f"SELECT * FROM {table_name}").fetchall()
        imported = 0
        for row in rows:
            owner = legacy_user_map.get(row["owner_id_id"])
            if not owner:
                continue

            project = Projects.objects.create(
                project_name=row["project_name"],
                project_description=row["project_description"] or "",
                status=row["status"],
                progress=row["progress"],
                start_date=_parse_date(row["start_date"]),
                due_date=_parse_date(row["due_date"]),
                owner_id=owner,
            )
            legacy_project_map[row["id"]] = project
            imported += 1

        return imported

    def _migrate_team_members(self, cursor, legacy_user_map, legacy_project_map):
        table_name = "projects_teammembers"
        if not _table_exists(cursor, table_name):
            self.stdout.write(self.style.WARNING(f"Skipping {table_name}: table not found."))
            return 0

        rows = cursor.execute(f"SELECT * FROM {table_name}").fetchall()
        imported = 0
        for row in rows:
            project = legacy_project_map.get(row["Projects_id"])
            user = legacy_user_map.get(row["user_id"])
            if not project or not user:
                continue

            TeamMembers.objects.get_or_create(
                Projects=project,
                user=user,
                defaults={"role": row["role"] or "developer"},
            )
            imported += 1

        return imported

    def _migrate_milestones(self, cursor, legacy_project_map):
        table_name = "milestones_milestone"
        if not _table_exists(cursor, table_name):
            self.stdout.write(self.style.WARNING(f"Skipping {table_name}: table not found."))
            return 0

        rows = cursor.execute(f"SELECT * FROM {table_name}").fetchall()
        imported = 0
        for row in rows:
            project = legacy_project_map.get(row["project_id"])
            if not project:
                continue

            Milestone.objects.create(
                project=project,
                title=row["title"],
                description=row["description"] or "",
                status=row["status"] or "planned",
                weight=row["weight"] or 1,
                start_date=_parse_date(row["start_date"]),
                due_date=_parse_date(row["due_date"]),
                completed_at=_parse_date(row["completed_at"]),
            )
            imported += 1

        return imported
