# Generated by Django 3.2.13 on 2023-04-19 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0002_alter_users_passphrase'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='passphrase',
            field=models.TextField(),
        ),
    ]
