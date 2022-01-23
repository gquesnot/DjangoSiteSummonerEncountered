import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from LolApp.models import GameChamp, GameMode, GameQueue, GameMap, GamePlatform
from LolApp.util.LolSummonerClass import LolSummoner
import requests


def updateChamp(version):

    champs = requests.get(f"http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json").json()['data']
    for champName, champ in champs.items():
        champId = int(champ['key'])
        try:
            myChamp = GameChamp.objects.get(champId=champId)
            myChamp.champName = champName
            myChamp.save()
        except:
            GameChamp(champName=champName, champId=champId).save()


def updateGameQueue():
    gameQueues = requests.get("https://static.developer.riotgames.com/docs/lol/queues.json").json()
    for queue in gameQueues:
        id_ = queue['queueId']

        try:
            myQueue = GameQueue.objects.get(queueId=id_)
            myQueue.description = queue['description']
            myQueue.map = queue['map']
            myQueue.save()
        except:
            GameQueue(queueId=id_, description=queue['description'], map=queue['map']).save()


def updateGameMode():
    gameModes = requests.get("https://static.developer.riotgames.com/docs/lol/gameModes.json").json()
    for mode in gameModes:
        try:
            myMode = GameMode.objects.get(mode=mode['gameMode'])
            myMode.description = mode['description']
            myMode.save()
        except:
            GameMode(mode=mode['gameMode'], description=mode['description']).save()


def updateGameMap():
    gameMaps = requests.get("https://static.developer.riotgames.com/docs/lol/maps.json").json()
    for map in gameMaps:
        try:
            myMode = GameMap.objects.get(mapId=map['mapId'])
            myMode.mapName = map['mapName']
            myMode.save()
        except:
            GameMap(mapId=map['mapId'], mapName=map['mapName']).save()


def updateData(request):
    f = open("config.json", "r")

    config = json.load(f)
    f.close()
    version = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]
    print(version, config['version'])
    if version != config['version']:
        updateChamp(version)
        updateGameMode()
        updateGameQueue()
        updateGameMap()
        config['version'] = version
        f = open("config.json", "w+")
        json.dump(config, f)
        f.close()

        return JsonResponse({"message": 'updated'})
    else:
        return JsonResponse({"message": 'no change'})


class Home(View):

    def get(self, request):
        self.platforms = GamePlatform.objects.all()
        return render(request, "home.html", {"platforms": self.platforms})

    def post(self, request):
        self.platforms = GamePlatform.objects.all()
        platform = self.platforms.filter(id=request.POST['myPlatform']).get()
        region = platform.region
        summonerName = request.POST['summonerName']
        gameType = request.POST['gameType']
        response = {
            "summonerName": summonerName,
            "platforms": self.platforms
        }
        ls = LolSummoner(summonerName, region=region.name, platform=platform.name.lower(), gameType=gameType)

        if ls.confOk:
            summonerName = ls.summoner.summonerName
            ls.updateHistory()
            response['gGrade'], founds = ls.convertMatchHistoryToSummonerNameDictWithMatch()
            if len(founds) != 0:
                response['inGame'], currentFounds = ls.findSummonnerInActiveMatch()
                response['datas'] = zip(range(len(currentFounds.keys())), currentFounds.keys(), currentFounds.values())

                return render(request, "home.html", response)
            else:
                response['message'] = "no match found with those filter"
        else:
            response['message'] = "Bad API KEY retry later"
        return render(request, "home.html", response)
