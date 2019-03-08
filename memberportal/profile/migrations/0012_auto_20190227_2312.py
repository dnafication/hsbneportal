# Generated by Django 2.1.5 on 2019-02-27 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0011_auto_20190225_0045'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='special_circumstance',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='special_circumstance_note',
            field=models.TextField(max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='income_bracket',
            field=models.CharField(choices=[('low', '$0/wk to $550/wk'), ('medium', '$550/wk to $950/wk'), ('high', '$950/wk or more')], default='high', max_length=10),
        ),
    ]
