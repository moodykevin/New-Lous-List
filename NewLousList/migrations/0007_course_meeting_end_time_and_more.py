# Generated by Django 4.1.2 on 2022-10-31 00:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('NewLousList', '0006_remove_course_meeting_end_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='meeting_end_time',
            field=models.CharField(default=' ', max_length=200),
        ),
        migrations.AddField(
            model_name='course',
            name='meeting_facility_description',
            field=models.CharField(default=' ', max_length=200),
        ),
        migrations.AddField(
            model_name='course',
            name='meeting_start_time',
            field=models.CharField(default=' ', max_length=200),
        ),
    ]
