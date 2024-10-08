# Generated by Django 5.0.6 on 2024-07-05 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judgement', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='rating',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='problem',
            name='test_file',
            field=models.FileField(default='t', upload_to='test_files/'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='solution',
            name='cycles',
            field=models.PositiveIntegerField(default=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='solution',
            name='ram',
            field=models.PositiveIntegerField(default=12),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='solution',
            name='rom',
            field=models.PositiveIntegerField(default=13),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='problem',
            name='description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='problem',
            name='title',
            field=models.CharField(max_length=280),
        ),
    ]
