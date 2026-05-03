# Life Track Pro - Database Schema Documentation

## Overview
This document describes the complete database schema for the Life Track Pro project management system. The backend uses Django ORM with SQLite (configured in `settings.py`), and the database file is located at `backend/config/db.sqlite3`.

---

## Database Technology
- **Engine**: SQLite3
- **Location**: `backend/config/db.sqlite3`
- **ORM**: Django ORM
- **Authentication**: Django's built-in auth system extended with custom User model

---

## Entity Relationship Diagram (Text-Based)

```
Users (Custom User Model)
    ↓
Projects (owner_id: ForeignKey → User)
    ↓
TeamMembers (Projects: FK → Projects, user: FK → User)
    ↓
Milestones (project: FK → Projects, members: M2M → TeamMembers)
    ↓
Tasks (project: FK → Projects, milestone: FK → Milestones, assignee: FK → TeamMembers)
    
Notifications (user: FK → User) - standalone, references project/task/milestone by ID
```

---

## Table Definitions

### 1. Users Table (`users_user`)
**Model**: `users.models.User` (extends `AbstractUser`)  
**AUTH_USER_MODEL**: `'users.User'`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| `username` | VARCHAR(150) | UNIQUE, NOT NULL | Unique username for login |
| `email` | VARCHAR(254) | UNIQUE, NOT NULL | User's email address |
| `first_name` | VARCHAR(150) | NOT NULL | User's first name |
| `last_name` | VARCHAR(150) | NOT NULL | User's last name |
| `password` | VARCHAR(128) | NOT NULL | Hashed password |
| `role` | VARCHAR(20) | NOT NULL | Role: `manager`, `developer`, `viewer` |
| `account_status` | VARCHAR(30) | NOT NULL | Status: `active`, `suspended` |
| `is_staff` | BOOLEAN | NOT NULL | Django admin access flag |
| `is_active` | BOOLEAN | NOT NULL | Account active flag |
| `is_superuser` | BOOLEAN | NOT NULL | Superuser flag |
| `date_joined` | DATETIME | NOT NULL | Account creation timestamp |
| `last_login` | DATETIME | NULL | Last login timestamp |

**Role Choices:**
- `manager` - Project management privileges
- `developer` - Default role, can work on tasks
- `viewer` - Read-only access

**Account Status Choices:**
- `active` - Normal active account
- `suspended` - Account temporarily disabled

**Related Django Auth Tables (auto-created):**
- `users_user_groups` - Many-to-many relationship with auth groups
- `users_user_user_permissions` - Many-to-many relationship with permissions

---

### 2. Projects Table (`projects_projects`)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| `project_name` | VARCHAR(100) | NOT NULL | Name of the project |
| `project_description` | TEXT | NOT NULL | Detailed description |
| `status` | VARCHAR(15) | NOT NULL | Status of the project |
| `progress` | INTEGER | NOT NULL, 0-100 | Completion percentage |
| `start_date` | DATE | NOT NULL | Project start date |
| `due_date` | DATE | NOT NULL | Project deadline |
| `owner_id` | INTEGER | FK → users_user.id, CASCADE | Project owner/creator |

**Status Choices:**
- `active` - Project is ongoing
- `on_track` - Project progressing as planned
- `at_risk` - Project facing potential issues
- `complete` - Project finished

**Relationships:**
- `owner_id` → `users_user.id` (One project has one owner, one user can own multiple projects)
- Related name: `owned_projects` (access via `user.owned_projects.all()`)

---

### 3. Team Members Table (`projects_teammembers`)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| `Projects_id` | INTEGER | FK → projects_projects.id, CASCADE | Associated project |
| `user_id` | INTEGER | FK → users_user.id, CASCADE | Associated user |
| `role` | VARCHAR(50) | NOT NULL | Role within the project |

**Relationships:**
- `Projects_id` → `projects_projects.id` (Many-to-one: one project has many team members)
- `user_id` → `users_user.id` (Many-to-one: one user can be in multiple projects)
- Related names: `teamMembers` (from project), default (from user)

**Note**: The field is named `Projects` (capital P) in the model, which Django converts to `Projects_id` in the database.

---

### 4. Milestones Table (`milestones_milestone`)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| `title` | VARCHAR(120) | NOT NULL | Milestone title |
| `description` | TEXT | BLANK | Detailed description |
| `status` | VARCHAR(20) | NOT NULL | Current status |
| `start_date` | DATE | NOT NULL | Milestone start date |
| `due_date` | DATE | NULL | Milestone deadline |
| `project_id` | INTEGER | FK → projects_projects.id, CASCADE | Parent project |
| `created_at` | DATETIME | AUTO_NOW_ADD | Creation timestamp |
| `updated_at` | DATETIME | AUTO_NOW | Last update timestamp |

**Status Choices:**
- `planned` - Milestone is planned
- `in_progress` - Currently working on it
- `completed` - Milestone finished
- `delayed` - Milestone is behind schedule

**Relationships:**
- `project_id` → `projects_projects.id` (Many-to-one: one project has many milestones)
- `members` → `projects_teammembers.id` (Many-to-many: milestones can have multiple team members)
- Related names: `milestones` (from project), `milestones` (from team member)

**Ordering**: By `due_date`, then `id`

---

### 5. Tasks Table (`tasks_task`)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| `title` | VARCHAR(120) | NOT NULL | Task title |
| `description` | TEXT | BLANK | Task description |
| `status` | VARCHAR(20) | NOT NULL | Current status |
| `project_id` | INTEGER | FK → projects_projects.id, CASCADE | Parent project |
| `milestone_id` | INTEGER | FK → milestones_milestone.id, CASCADE | Parent milestone |
| `assignee_id` | INTEGER | FK → projects_teammembers.id, SET_NULL | Assigned team member |
| `created_at` | DATETIME | AUTO_NOW_ADD | Creation timestamp |
| `updated_at` | DATETIME | AUTO_NOW | Last update timestamp |

**Status Choices:**
- `todo` - Task not yet started
- `in_progress` - Currently being worked on
- `done` - Task completed
- `blocked` - Task cannot proceed

**Relationships:**
- `project_id` → `projects_projects.id` (Many-to-one: one project has many tasks)
- `milestone_id` → `milestones_milestone.id` (Many-to-one: one milestone has many tasks)
- `assignee_id` → `projects_teammembers.id` (Many-to-one: one team member can have many tasks)
- If team member is deleted, task's assignee becomes NULL (SET_NULL)
- Related names: `tasks` (from project, milestone, and team member)

**Ordering**: By `id`

---

### 6. Notifications Table (`notifications_notification`)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| `user_id` | INTEGER | FK → users_user.id, CASCADE | Notification recipient |
| `notification_type` | VARCHAR(30) | NOT NULL | Type of notification |
| `title` | VARCHAR(200) | NOT NULL | Notification title |
| `message` | TEXT | NOT NULL | Notification body |
| `project_id` | INTEGER | NULL, BLANK | Related project ID (optional) |
| `project_name` | VARCHAR(100) | NULL, BLANK | Related project name (denormalized) |
| `task_id` | INTEGER | NULL, BLANK | Related task ID (optional) |
| `task_name` | VARCHAR(120) | NULL, BLANK | Related task name (denormalized) |
| `milestone_id` | INTEGER | NULL, BLANK | Related milestone ID (optional) |
| `milestone_name` | VARCHAR(150) | NULL, BLANK | Related milestone name (denormalized) |
| `created_at` | DATETIME | AUTO_NOW_ADD | Creation timestamp |
| `is_read` | BOOLEAN | DEFAULT=False | Read status |

**Notification Types:**
- `project_created` - New project created
- `project_updated` - Project details updated
- `project_completed` - Project marked complete
- `milestone_created` - New milestone added
- `milestone_completed` - Milestone marked complete
- `task_assigned` - Task assigned to user
- `task_completed` - Task marked complete
- `task_blocked` - Task marked as blocked
- `team_member_added` - User added to project team
- `project_at_risk` - Project status changed to at-risk
- `project_overdue` - Project has passed due date

**Relationships:**
- `user_id` → `users_user.id` (Many-to-one: one user has many notifications)
- Related name: `notifications` (access via `user.notifications.all()`)

**Ordering**: By `-created_at` (newest first)

---

### 7. Chatbot App
**Status**: Currently no database models  
The chatbot app (`backend/config/apps/chatbot/`) exists but has no models. It returns a simple "ok" response without persisting chat history. Future implementation may include:
- Chat sessions
- Message history
- Conversation context

---

## Relationship Summary

### One-to-Many Relationships
1. **User → Projects** (as owner): `User.id` → `Projects.owner_id`
2. **User → TeamMembers**: `User.id` → `TeamMembers.user_id`
3. **Project → TeamMembers**: `Projects.id` → `TeamMembers.Projects_id`
4. **Project → Milestones**: `Projects.id` → `Milestone.project_id`
5. **Project → Tasks**: `Projects.id` → `Task.project_id`
6. **Milestone → Tasks**: `Milestone.id` → `Task.milestone_id`
7. **TeamMember → Tasks** (as assignee): `TeamMembers.id` → `Task.assignee_id`
8. **User → Notifications**: `User.id` → `Notification.user_id`

### Many-to-Many Relationships
1. **Milestone ↔ TeamMembers**: Through `milestones_milestone_members` intermediate table

### Denormalized References (Stored as Integer + CharField, not FKs)
- `Notification.project_id` + `project_name`
- `Notification.task_id` + `task_name`
- `Notification.milestone_id` + `milestone_name`

---

## Model Files Location

| App | Model File | Table(s) |
|-----|-----------|----------|
| users | `backend/config/apps/users/models.py` | `users_user`, `users_user_groups`, `users_user_user_permissions` |
| projects | `backend/config/apps/projects/models.py` | `projects_projects`, `projects_teammembers` |
| milestones | `backend/config/apps/milestones/models.py` | `milestones_milestone` + M2M table |
| tasks | `backend/config/apps/tasks/models.py` | `tasks_task` |
| notifications | `backend/config/apps/notifications/models.py` | `notifications_notification` |
| risks | `backend/config/apps/risks/models.py` | *(empty - no models yet)* |
| reports | `backend/config/apps/reports/models.py` | *(empty - no models yet)* |
| chatbot | `backend/config/apps/chatbot/models.py` | *(no models yet)* |

---

## Database Constraints

### Unique Constraints
- `users_user.username` - Unique
- `users_user.email` - Unique

### Foreign Key Constraints (CASCADE)
- Projects → User (owner): Delete project if owner is deleted
- TeamMembers → Project: Delete team member if project is deleted
- TeamMembers → User: Delete team member if user is deleted
- Milestones → Project: Delete milestones if project is deleted
- Tasks → Project: Delete tasks if project is deleted
- Tasks → Milestone: Delete tasks if milestone is deleted
- Notifications → User: Delete notifications if user is deleted

### Foreign Key Constraints (SET_NULL)
- Tasks → TeamMembers (assignee): Set to NULL if team member is deleted

### Foreign Key Constraints (DEFERRABLE INITIALLY DEFERRED)
- Django auth m2m tables use deferred constraints

---

## Default Values

| Field | Default Value |
|-------|---------------|
| `User.role` | `'developer'` |
| `User.account_status` | `'active'` |
| `User.is_active` | `True` |
| `User.is_staff` | `False` |
| `User.is_superuser` | `False` |
| `Project.status` | *(no default - required)* |
| `Project.progress` | *(no default - required, 0-100)* |
| `Milestone.status` | `'planned'` |
| `Task.status` | `'todo'` |
| `Notification.is_read` | `False` |

---

## Indexes

Django automatically creates indexes on:
- Primary keys (`id`)
- Foreign keys
- Unique fields

Custom ordering defined in Meta:
- `Task.Meta.ordering = ["id"]`
- `Milestone.Meta.ordering = ["due_date", "id"]`
- `Notification.Meta.ordering = ["-created_at"]`

---

## Future Considerations

1. **Risks App**: Currently empty, may need models for project risk tracking
2. **Reports App**: Currently empty, may need models for generated reports
3. **Chatbot App**: No models yet, may need:
   - `ChatSession` - Store conversation sessions
   - `ChatMessage` - Store message history
   - `ChatContext` - Store conversation context
4. **Missing Fields in Current Schema**:
   - No timestamp fields on `Projects` model (could add `created_at`, `updated_at`)
   - No priority field on `Tasks`
   - No file attachment support
   - No comments system
