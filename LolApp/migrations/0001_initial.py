# Generated by Django 3.2.7 on 2021-10-04 20:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Summoner',
            fields=[
                ('summonerId', models.IntegerField(primary_key=True, serialize=False)),
                ('summonerName', models.TextField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Stats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kills', models.IntegerField()),
                ('deaths', models.IntegerField()),
                ('assists', models.IntegerField()),
                ('win', models.BooleanField()),
                ('summoner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='LolApp.summoner')),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('matchId', models.IntegerField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField()),
                ('participantStats', models.ManyToManyField(to='LolApp.Stats')),
            ],
        ),
    ]
