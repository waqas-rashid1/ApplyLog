# Generated by Django 5.2 on 2025-06-15 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0008_alter_savedjob_deadline'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='deadline',
            field=models.DateField(blank=True, null=True),
        ),
    ]
