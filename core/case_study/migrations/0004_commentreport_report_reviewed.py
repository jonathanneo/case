# Generated by Django 2.2.4 on 2019-10-11 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('case_study', '0003_commentreport'),
    ]

    operations = [
        migrations.AddField(
            model_name='commentreport',
            name='report_reviewed',
            field=models.BooleanField(default=False),
        ),
    ]