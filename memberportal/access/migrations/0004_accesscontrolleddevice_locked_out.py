# Generated by Django 2.0.9 on 2018-11-23 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('access', '0003_interlocklog_user_off'),
    ]

    operations = [
        migrations.AddField(
            model_name='accesscontrolleddevice',
            name='locked_out',
            field=models.BooleanField(default=False, verbose_name='Lockout general members'),
        ),
    ]
