from datetime import datetime, timedelta
import json
from datetime import datetime
from math import ceil

from riotwatcher import LolWatcher, ApiError
from ..models import Summoner, Stats, Match
import pytz
import locale


class LolSummoner():
    max = 40
    count = 50
    founds = None
    regionByMyRegion = {
        "euw1": "EUROPE",
        "eun1": "EUROPE",
        "na1": "AMERICAS",
        "kr": "ASIA",
    }
    def __init__(self, summonerName, myRegion=None):
        try:
            if myRegion is not None:
                region = self.regionByMyRegion[myRegion]
            else:
                region = None
            with open("config.json", "r") as f:
                self.config = json.load(f)
                self.apiKey = self.config['apiKey']
                self.myRegion = myRegion
                self.region = region
                self.max = self.config['max']
                if self.max < self.count:
                    self.count = self.max

                self.summonerName = summonerName
                try:
                    self.lol_watcher = LolWatcher(self.apiKey, default_match_v5=True)
                    self.summoner = self.createOrGetSummoner(summonerName)
                    try:
                        self.matches = Match.objects.filter(participantStats__summoner=self.summoner)
                        self.matchIds = set([match.matchId for match in self.matches])
                    except:
                        self.matches = []
                        self.matchIds = set()
                    self.confOk = True
                except:
                    self.confOk = False

        except:
            self.confOk = False

    def createOrGetSummoner(self, summonerName, summonerId=None, rSummonerId=None):
        if summonerId is None:
            summ = self.lol_watcher.summoner.by_name(self.myRegion, summonerName)
            summonerId = summ['puuid']
            rSummonerId = summ['id']
        summoner = Summoner.objects.filter(summonerId=summonerId).first()
        if not summoner:
            summoner = Summoner(summonerName=summonerName, summonerId=summonerId, rsummonerId=rSummonerId)
        elif summoner.summonerName != summonerName:
            summoner.summonerName = summonerName
        summoner.save()
        return summoner

    def updateHistory(self):
        start = 0
        result = dict()

        stop = False
        for i in range(ceil(self.max / self.count)):
            # if stop:
            #     break
            for match in self.lol_watcher.match_v5.matchlist_by_puuid(self.region, self.summoner.summonerId,
                                                                      start=start, count=self.count):
                if match not in self.matchIds:

                    rMatch = self.lol_watcher.match_v5.by_id(region=self.region, match_id=match)
                    duration = round(rMatch['info']['gameDuration'] / 1000)
                    matchModel = Match(matchId=match, mode=rMatch['info']['gameMode'], duration=duration,
                                       date=datetime.utcfromtimestamp(
                                           rMatch['info']['gameStartTimestamp'] / 1000).astimezone(pytz.UTC))
                    matchModel.save()

                    winTeamCode = rMatch['info']["teams"][0]['teamId'] if rMatch['info']["teams"][0]['win'] else \
                        rMatch['info']["teams"][1]['teamId']

                    tmpParticipants = []
                    for participant in rMatch['info']['participants']:
                        if participant['summonerName'] != self.summonerName:
                            summoner = self.createOrGetSummoner(participant['summonerName'], participant['puuid'], participant['summonerId'])
                        else:
                            summoner = self.summoner
                        gold = participant['goldEarned']
                        level = participant['champLevel']
                        totalDamage = participant['totalDamageDealt']
                        kills = participant['kills']
                        deaths = participant['deaths']
                        assists = participant['assists']
                        durationM = round(duration / 60)
                        if durationM == 0:
                            grade= 0
                        else:

                            grade = 0.336 - (1.437 * (deaths / durationM)) + (0.000117 * (gold / durationM)) + (
                                    0.443 * ((kills + assists) / durationM)) + (0.264 * (level / durationM)) + (
                                            0.000013 * (totalDamage / durationM))
                        grade = round(grade, 2)
                        statsModel = Stats(
                            summoner=summoner,
                            champName=participant['championName'],
                            kills=kills,
                            deaths=deaths,
                            assists=assists,
                            win=winTeamCode == participant['teamId'],
                            gold=gold,
                            level=level,
                            totalDamage=totalDamage,
                            grade=grade *10,
                        )
                        statsModel.save()
                        matchModel.participantStats.add(statsModel)
                    matchModel.save()
            start += self.count
        self.matches = Match.objects.filter(participantStats__summoner=self.summoner).order_by('-date')

    def convertMatchHistoryToSummonerNameDictWithMatch(self):
        res = dict()
        idx = 0
        # locale.setlocale(locale.LC_ALL, 'fr_FR')
        globalGrade = 0
        for idx, match in enumerate(self.matches):
            allParticiants = match.participantStats.all()
            myStats = match.participantStats.filter(summoner=self.summoner).first()
            globalGrade += myStats.grade
            for stats in match.participantStats.all():
                if stats != myStats:
                    ddate = match.date + timedelta(hours=4)
                    tmpRes = {
                        "lastSeen": idx,
                        "mode": match.mode,
                        "time": ddate.strftime("%d-%m-%Y %H:%M"),
                        "win": myStats.win,
                        "myGrade": round(myStats.grade * 10, 2),
                        "grade": round(stats.grade  * 10, 2),
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
        globalGrade = round(globalGrade / len(self.matches), 2)
        res = dict(sorted(res.items(), key=lambda item: item[1]['found'], reverse=True))
        for k, v in res.items():
            tmpGrade = 0
            myTmpGrade = 0
            tmpLen = len(v['matches'])
            for match in v['matches']:
                tmpGrade += match['grade']
                myTmpGrade += match['myGrade']
            res[k]['grade'] = round(tmpGrade / tmpLen, 2)
            res[k]['myGrade'] = round(myTmpGrade / tmpLen, 2)

        # for k, v in res.items():
        #     if v['found'] > 1:
        #         print(v['found'], k, ":")
        #         for match in v['matches']:
        #             print('   ', printMatch(match))
        # with open(f"LolApp/util/json/{self.summonerName}_found.json", "w+") as f:
        #     json.dump(res, f, indent=4)
        print(f"done update {len(self.matches)} founds")
        self.founds = res
        return globalGrade, res

    def findSummonnerInActiveMatch(self):
        result = dict()

        try:
            actualMatch = self.lol_watcher.spectator.by_summoner(self.myRegion, self.summoner.rsummonerId)
            print("GAME STARTED")
            for participant in actualMatch['participants']:

                # print(participant['summonerName'],  participant['summonerName'] in founds.keys())
                if participant['summonerName'] in self.founds.keys():
                    result[participant['summonerName']] = self.founds[participant['summonerName']]
            return True, result
        except:
            return False, self.founds

    @staticmethod
    def printMatch(match):
        t = match['time'] / 1000
        return f"{match['lastSeen']} {datetime.fromtimestamp(t).strftime('%d-%m-%Y %H:%M:%S')} {match['mode']} {'W' if match['win'] else 'L'} {'VS' if match['vs'] else 'WITH'} {match['myChamp']} {match['myScore']} vs {match['champ']} {match['score']}"
