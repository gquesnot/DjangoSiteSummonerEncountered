# Generated by Django 3.2.7 on 2021-10-05 22:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LolApp', '0008_alter_stats_grade'),
    ]

    operations = [
        migrations.AddField(
            model_name='summoner',
            name='rsummonerId',
            field=models.TextField(default=''),
        ),
    ]
