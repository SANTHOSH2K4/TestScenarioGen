# Generated by Django 4.1.7 on 2025-01-09 02:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0006_remove_user_is_active_remove_user_is_staff_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chat',
            old_name='cid',
            new_name='chid',
        ),
    ]
