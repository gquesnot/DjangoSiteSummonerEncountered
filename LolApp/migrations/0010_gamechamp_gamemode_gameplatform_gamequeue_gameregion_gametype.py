# Generated by Django 3.2.7 on 2021-10-07 18:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('LolApp', '0009_summoner_rsummonerid'),
    ]

    operations = [
        migrations.CreateModel(
            name='GameChamp',
            fields=[
                ('champId', models.IntegerField(primary_key=True, serialize=False)),
                ('champName', models.TextField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='GameMode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mode', models.TextField(max_length=100)),
                ('description', models.TextField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='GameQueue',
            fields=[
                ('queueId', models.IntegerField(primary_key=True, serialize=False)),
                ('description', models.TextField(max_length=100)),
                ('map', models.TextField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='GameRegion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='GameType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.TextField(max_length=100)),
                ('description', models.TextField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='GamePlatform',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=50)),
                ('smallName', models.TextField(max_length=50)),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='LolApp.gameregion')),
            ],
        ),
    ]