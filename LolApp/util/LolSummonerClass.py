from datetime import datetime, timedelta
import json
from datetime import datetime
from riotwatcher import LolWatcher, ApiError
from ..models import Summoner, Stats, Match
import pytz
import locale


class LolSummoner():
    max = 40
    count = 20
    founds = None

    def __init__(self, summonerName):
        try:
            with open("config.json", "r") as f:
                self.config = json.load(f)
                print(self.config)
                self.apiKey = self.config['apiKey']
                self.myRegion = self.config['myRegion']
                self.region = self.config['region']
                self.summonerName = summonerName
                try:
                    self.lol_watcher = LolWatcher(self.apiKey, default_match_v5=True)
                    self.summoner = self.createOrGetSummoner(summonerName)
                    self.matches = Match.objects.filter(participantStats__summoner=self.summoner)
                    self.matchIds = set([match.matchId for match in self.matches])
                    self.confOk = True
                except:
                    self.confOk = False

        except:
            self.confOk = False

    def createOrGetSummoner(self, summonerName):
        summ = self.lol_watcher.summoner.by_name(self.myRegion, summonerName)
        summoner = Summoner.objects.filter(summonerId=summ['puuid']).first()
        if not summoner:
            summoner = Summoner(summonerName=summonerName, summonerId=summ['puuid'])
        elif summoner.summonerName != summonerName:
            summoner.summonerName = summonerName
        summoner.save()
        return summoner

    def updateHistory(self):
        start = 0
        result = dict()

        stop = False
        for i in range(round(self.max / self.count)):
            # if stop:
            #     break
            for match in self.lol_watcher.match_v5.matchlist_by_puuid(self.region, self.summoner.summonerId,
                                                                      start=start, count=self.count):
                print(match)
                if match in self.matchIds:
                    # stop = True
                    break
                rMatch = self.lol_watcher.match_v5.by_id(region=self.region, match_id=match)
                matchModel = Match(matchId=match, mode=rMatch['info']['gameMode'],
                                   date=datetime.utcfromtimestamp(
                                       rMatch['info']['gameStartTimestamp'] / 1000).astimezone(pytz.UTC))
                matchModel.save()

                winTeamCode = rMatch['info']["teams"][0]['teamId'] if rMatch['info']["teams"][0]['win'] else \
                    rMatch['info']["teams"][1]['teamId']

                tmpParticipants = []
                for participant in rMatch['info']['participants']:
                    if participant['summonerName'] != self.summonerName:
                        summoner = self.createOrGetSummoner(participant['summonerName'])
                    else:
                        summoner = self.summoner
                    statsModel = Stats(
                        summoner=summoner,
                        champName=participant['championName'],
                        kills=participant['kills'],
                        deaths=participant['deaths'],
                        assists=participant['assists'],
                        win=winTeamCode == participant['teamId']
                    )
                    statsModel.save()
                    matchModel.participantStats.add(statsModel)
                matchModel.save()
        self.matches = Match.objects.filter(participantStats__summoner=self.summoner).order_by('-date')

    def convertMatchHistoryToSummonerNameDictWithMatch(self):
        res = dict()
        idx = 0
        #locale.setlocale(locale.LC_ALL, 'fr_FR')
        for idx, match in enumerate(self.matches):
            # print(match)
            allParticiants = match.participantStats.all()
            myStats = match.participantStats.filter(summoner=self.summoner).first()
            for stats in match.participantStats.all():
                if stats != myStats:
                    ddate = match.date + timedelta(hours=4)
                    tmpRes = {
                        "lastSeen": idx,
                        "mode": match.mode,
                        "time": ddate.strftime("%d-%m-%Y %H:%M"),
                        "win": myStats.win,
                        "vs": myStats.win != stats.win,
                        "myScore": f"{myStats.kills}.{myStats.deaths}.{myStats.assists}",
                        "myChamp": myStats.champName,
                        "score": f"{stats.kills}.{stats.deaths}.{stats.assists}",
                        "champ": stats.champName
                    }
                    if stats.summoner.summonerName not in res.keys():
                        res[stats.summoner.summonerName] = {
                            "found": 1,
                            "matches": [tmpRes]
                        }
                    else:
                        res[stats.summoner.summonerName]['found'] += 1
                        res[stats.summoner.summonerName]['matches'].append(tmpRes)
            idx += 1
        res = dict(sorted(res.items(), key=lambda item: item[1]['found'], reverse=True))
        # for k, v in res.items():
        #     if v['found'] > 1:
        #         print(v['found'], k, ":")
        #         for match in v['matches']:
        #             print('   ', printMatch(match))
        with open(f"LolApp/util/json/{self.summonerName}_found.json", "w+") as f:
            json.dump(res, f, indent=4)
        print("done update founds")
        self.founds = res
        return res

    def findSummonnerInActiveMatch(self):
        result = list()
        try:
            actualMatch = self.lol_watcher.spectator.by_summoner(self.myRegion, self.summoner.summonerId)
            print("GAME STARTED")
            for participant in actualMatch['participants']:

                # print(participant['summonerName'],  participant['summonerName'] in founds.keys())
                if participant['summonerName'] in self.founds.keys():
                    found = self.founds[participant['summonerName']]
                    result.append(found)
            return result
        except:
            return self.founds

    @staticmethod
    def printMatch(match):
        t = match['time'] / 1000
        return f"{match['lastSeen']} {datetime.fromtimestamp(t).strftime('%d-%m-%Y %H:%M:%S')} {match['mode']} {'W' if match['win'] else 'L'} {'VS' if match['vs'] else 'WITH'} {match['myChamp']} {match['myScore']} vs {match['champ']} {match['score']}"
