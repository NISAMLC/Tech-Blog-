# Generated by Django 4.2.3 on 2024-06-07 05:49

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='publish',
            field=models.DateTimeField(verbose_name=datetime.datetime(2024, 6, 7, 5, 49, 37, 897744, tzinfo=datetime.timezone.utc)),
        ),
    ]