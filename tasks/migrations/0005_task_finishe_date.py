# Generated by Django 4.1.3 on 2023-01-26 08:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_task_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='finishe_date',
            field=models.DateTimeField(null=True, verbose_name='Reached at'),
        ),
    ]
