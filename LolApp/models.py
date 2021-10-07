from django.db import models


class GameMap(models.Model):
    mapId = models.IntegerField(primary_key=True)
    mapName = models.TextField(max_length=100)



class GameChamp(models.Model):
    champId = models.IntegerField(primary_key=True)
    champName = models.TextField(max_length=100)

class GameMode(models.Model):
    mode = models.TextField(max_length=100, primary_key=True)
    description = models.TextField(max_length=100)


class GameQueue(models.Model):
    queueId = models.IntegerField(primary_key=True)
    description = models.TextField(max_length=100, null=True)
    map = models.TextField(max_length=100)


class GameRegion(models.Model):
    name = models.TextField(max_length=50)

class GamePlatform(models.Model):
    name = models.TextField(max_length=50)
    region = models.ForeignKey(GameRegion, on_delete=models.CASCADE)
    smallName = models.TextField(max_length=50)




class Summoner(models.Model):
    summonerId = models.TextField(primary_key=True)
    rsummonerId = models.TextField(default="")
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
    champ = models.ForeignKey(GameChamp, null=True, on_delete=models.CASCADE)
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
    mode = models.ForeignKey(GameMode, on_delete=models.CASCADE, null=True)
    queue = models.ForeignKey(GameQueue, on_delete=models.CASCADE, null=True)
    map = models.ForeignKey(GameMap, on_delete=models.CASCADE, null=True)
    duration = models.TextField(default=0)
    participantStats = models.ManyToManyField(Stats)
    date = models.DateTimeField()






