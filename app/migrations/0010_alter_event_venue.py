# Generated by Django 5.1.1 on 2025-05-01 19:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_event_venue'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='venue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='app.venue'),
        ),
    ]
