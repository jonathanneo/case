# Generated by Django 2.2.4 on 2019-10-04 22:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case_study', '0002_other'),
    ]

    operations = [
        migrations.RenameField(
            model_name='other',
            old_name='body',
            new_name='other_body',
        ),
    ]
