# Generated by Django 3.2.7 on 2021-10-07 19:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('LolApp', '0012_auto_20211007_2136'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='map',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='LolApp.gamemap'),
        ),
    ]
