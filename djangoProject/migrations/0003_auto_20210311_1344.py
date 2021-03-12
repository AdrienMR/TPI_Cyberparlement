# Generated by Django 3.1.7 on 2021-03-11 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangoProject', '0002_auto_20210311_1342'),
    ]

    operations = [
        migrations.AddField(
            model_name='personne',
            name='addresscheck',
            field=models.CharField(blank=True, db_column='AddressCheck', max_length=45, null=True),
        ),
        migrations.AddField(
            model_name='personne',
            name='mailcheck',
            field=models.CharField(blank=True, db_column='MailCheck', max_length=45, null=True),
        ),
        migrations.AddField(
            model_name='personne',
            name='passwordcheck',
            field=models.CharField(blank=True, db_column='PasswordCheck', max_length=45, null=True),
        ),
    ]
