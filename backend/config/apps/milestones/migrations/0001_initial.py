from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0002_alter_projects_project_description_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Milestone',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('description', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('planned', 'Planned'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('delayed', 'Delayed')], default='planned', max_length=20)),
                ('weight', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)])),
                ('start_date', models.DateField()),
                ('due_date', models.DateField()),
                ('completed_at', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='milestones', to='projects.projects')),
            ],
            options={
                'ordering': ['due_date', 'id'],
            },
        ),
    ]
