# Generated by Django 5.2 on 2025-05-21 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_rename_subscription_usersubscription_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.TextField(blank=True, help_text='Загрузите ваш аватар', null=True, verbose_name='Аватар'),
        ),
    ]
