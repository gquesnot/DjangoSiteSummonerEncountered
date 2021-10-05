from django.db import models







class Summoner(models.Model):
    summonerId = models.TextField(primary_key=True)
    summonerName = models.TextField(max_length=200)

    def getDict(self):
        return {
            "summonerId": self.summonerId,
            "summonerName": self.summonerName,
        }

    def __str__(self):
        return f"id: {self.summonerId}, name: {self.summonerName}"



class Stats(models.Model):
    summoner = models.ForeignKey(Summoner, on_delete=models.CASCADE)
    champName = models.TextField(max_length=200, default="")
    kills = models.IntegerField()
    deaths = models.IntegerField()
    assists = models.IntegerField()
    win = models.BooleanField()
    gold = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    totalDamage = models.IntegerField(default=0)
    grade = models.FloatField(default=0)

class Match(models.Model):
    matchId = models.TextField(primary_key=True)
    mode = models.TextField(max_length=50, default="NORMAL")
    duration = models.TextField(default=0)
    participantStats = models.ManyToManyField(Stats)
    date = models.DateTimeField()






