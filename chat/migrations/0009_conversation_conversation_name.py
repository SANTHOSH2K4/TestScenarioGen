# Generated by Django 4.1.7 on 2025-01-09 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0008_rename_chid_chat_cid'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='conversation_name',
            field=models.CharField(default='conversation name', max_length=255),
        ),
    ]
