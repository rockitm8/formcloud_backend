# Generated by Django 4.1.3 on 2023-01-24 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domain',
            name='contact_form',
            field=models.BooleanField(default=False, null=True, verbose_name='Contact Form'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='contact_page',
            field=models.CharField(default='', max_length=150, null=True, verbose_name='Contact Page'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='emails_found',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Emails Found'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='form_sent',
            field=models.BooleanField(default=False, null=True, verbose_name='Form Sent'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='reached_at',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Reached at'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='sent_manually',
            field=models.BooleanField(default=False, null=True, verbose_name='Sent Manually'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='status',
            field=models.CharField(default='Pending', max_length=30, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='domain',
            name='went_over_manually',
            field=models.BooleanField(default=False, null=True, verbose_name='Went Over Manually'),
        ),
    ]
