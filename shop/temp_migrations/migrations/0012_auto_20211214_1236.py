# Generated by Django 3.2.4 on 2021-12-14 06:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0011_auto_20211214_1150'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='country',
            new_name='district',
        ),
        migrations.RemoveField(
            model_name='order',
            name='state',
        ),
    ]
