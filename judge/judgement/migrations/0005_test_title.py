# Generated by Django 5.0.6 on 2024-07-06 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judgement', '0004_remove_problem_test_file_test'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='title',
            field=models.CharField(default='Title Goes Here', max_length=280),
            preserve_default=False,
        ),
    ]
