# Generated by Django 4.1.7 on 2025-01-08 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_remove_conversation_config_alter_chat_input_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='last_login',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
