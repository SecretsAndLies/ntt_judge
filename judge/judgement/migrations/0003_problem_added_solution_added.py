# Generated by Django 5.0.6 on 2024-07-06 11:54

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judgement', '0002_problem_rating_problem_test_file_solution_cycles_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='added',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='solution',
            name='added',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]