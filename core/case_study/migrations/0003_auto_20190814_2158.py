# Generated by Django 2.2.4 on 2019-08-14 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('case_study', '0002_auto_20190814_0917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='casestudy',
            name='scr',
            field=models.FloatField(blank=True),
        ),
        migrations.AlterField(
            model_name='casestudy',
            name='weight',
            field=models.FloatField(blank=True),
        ),
    ]
