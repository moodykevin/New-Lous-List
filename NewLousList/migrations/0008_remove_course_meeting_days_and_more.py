# Generated by Django 4.1.2 on 2022-11-04 22:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NewLousList', '0007_course_meeting_end_time_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='meeting_days',
        ),
        migrations.RemoveField(
            model_name='course',
            name='meeting_end_time',
        ),
        migrations.RemoveField(
            model_name='course',
            name='meeting_facility_description',
        ),
        migrations.RemoveField(
            model_name='course',
            name='meeting_start_time',
        ),
        migrations.AddField(
            model_name='course',
            name='meetings',
            field=models.JSONField(default=[]),
        ),
    ]
