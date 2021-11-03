from datetime import datetime, timedelta
import json
from datetime import datetime
from math import ceil
from time import sleep

from riotwatcher import LolWatcher, ApiError, Handlers

from ..models import Summoner, Stats, Match, GameChamp, GameQueue, GameMode, GameMap
import pytz
import locale


class LolSummoner():
    max = 40
    count = 50
    founds = None

    def __init__(self, summonerName=None, region=None, platform=None, gameType=None):
        try:
            self.region = region
            self.platform = platform
            self.gameType = gameType

            with open("config.json", "r") as f:
                self.config = json.load(f)
                self.apiKey = self.config['apiKey']
                self.max = self.config['max']
                if self.max < self.count:
                    self.count = self.max
                if summonerName is not None:
                    self.summonerName = summonerName
                    try:
                        self.lol_watcher = LolWatcher(self.apiKey, default_match_v5=True)

                        self.summoner = self.createOrGetSummoner(summonerName)
                        self.summonerName = self.summoner.summonerName

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
            summ = self.lol_watcher.summoner.by_name(self.platform, summonerName)
            summonerId = summ['puuid']
            rSummonerId = summ['id']
            summonerName = summ['name']

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
                    try:
                        rMatch = self.lol_watcher.match_v5.by_id(region=self.region, match_id=match)
                    except:
                        sleep(5)
                        try:
                            rMatch = self.lol_watcher.match_v5.by_id(region=self.region, match_id=match)

                        except:
                            sleep(5)
                            continue
                    duration = rMatch['info']['gameDuration']
                    if duration > 100000:
                        duration = duration / 1000
                    mode = GameMode.objects.get(mode=rMatch['info']['gameMode'])
                    queue = GameQueue.objects.get(queueId=rMatch['info']['queueId'])
                    map_ = GameMap.objects.get(mapId=rMatch['info']['mapId'])
                    matchModel = Match(matchId=match, mode=mode, queue=queue, map=map_, duration=duration,
                                       date=datetime.utcfromtimestamp(
                                           rMatch['info']['gameStartTimestamp'] / 1000).astimezone(pytz.UTC))
                    matchModel.save()

                    winTeamCode = rMatch['info']["teams"][0]['teamId'] if rMatch['info']["teams"][0]['win'] else \
                        rMatch['info']["teams"][1]['teamId']

                    tmpParticipants = []
                    for participant in rMatch['info']['participants']:
                        if participant['summonerName'] != self.summonerName:
                            summoner = self.createOrGetSummoner(participant['summonerName'], participant['puuid'],
                                                                participant['summonerId'])
                        else:
                            summoner = self.summoner
                        gold = participant['goldEarned']
                        level = participant['champLevel']
                        totalDamage = participant['totalDamageDealt']
                        kills = participant['kills']
                        deaths = participant['deaths']
                        assists = participant['assists']
                        durationM = round(duration / 60)

                        # if durationM == 0:
                        #     grade = 0.5
                        #     gradeString = ""
                        # else:

                        # grade = 0.336 - (1.437 * (deaths / durationM)) + (0.000117 * (gold / durationM)) + (
                        #         0.443 * ((kills + assists) / durationM)) + (0.264 * (level / durationM)) + (
                        #                 0.000013 * (totalDamage / durationM))
                        # gradeString = f"=> 0.336 - ( 1.437 * (deaths / gameDurationInMinute)  + (0.000117 * (golds / gameDurationInMinute)) + (0.443 * ((kills + assists) / gameDurationInMinute)) + (0.264 * (levels / gameDurationInMinute)) + (0.000013 * (totalDamages / gameDurationInMinute)))<br>" + \
                        #               f"=> 0.336 - ( 1.437 * ({deaths} / {durationM})  + (0.000117 * ({gold} / {durationM})) + (0.443 * (({kills} + {assists}) / {durationM})) + (0.264 * ({level} / {durationM})) + (0.000013 * ({totalDamage} / {durationM})))<br>" + \
                        #               f"=> 0.336 - {round(1.437 * (deaths / durationM), 5)}  + {round(0.000117 * (gold / durationM),5)} + {round(0.443 * ((kills + assists) / durationM),5)} + {round(0.264 * (level / durationM),5)} + {round(0.000013 * (totalDamage / durationM),5)}<br>" +\
                        #               f"=> {grade}<br>"
                        grade = (kills + assists) / deaths if deaths != 0 else kills + assists
                        grade = round(grade, 2)
                        statsModel = Stats(
                            summoner=summoner,
                            champ=GameChamp.objects.get(champId=participant['championId']),
                            kills=kills,
                            deaths=deaths,
                            assists=assists,
                            win=winTeamCode == participant['teamId'],
                            gold=gold,
                            level=level,
                            totalDamage=totalDamage,
                            grade=grade,
                            gradeString=""
                        )
                        statsModel.save()
                        matchModel.participantStats.add(statsModel)
                    matchModel.save()
            start += self.count
        self.getMatches()

    def getMatches(self):
        if self.gameType == "NORMAL":
            self.matches = Match.objects.filter(participantStats__summoner=self.summoner, mode__mode="CLASSIC").exclude(
                queue__description__contains="Ranked").order_by('-date')

        elif self.gameType == "Ranked":
            self.matches = Match.objects.filter(participantStats__summoner=self.summoner, mode__mode="CLASSIC",
                                                queue__description__contains="Ranked").order_by('-date')

        elif self.gameType == "ARAM":
            self.matches = Match.objects.filter(participantStats__summoner=self.summoner, mode__mode="ARAM").order_by(
                '-date')

        elif self.gameType == "GAME MODE":

            self.matches = Match.objects.filter(participantStats__summoner=self.summoner).exclude(
                mode__mode__in=["CLASSIC", "ARAM", "TUTORIAL"]).order_by('-date')
        else:
            self.matches = Match.objects.filter(participantStats__summoner=self.summoner).order_by('-date')

    def convertMatchHistoryToSummonerNameDictWithMatch(self):

        res = dict()
        idx = 0
        # locale.setlocale(locale.LC_ALL, 'fr_FR')
        globalGrade = 0
        if len(self.matches):
            for idx, match in enumerate(self.matches):

                allParticiants = match.participantStats.all()

                myStats = match.participantStats.filter(summoner=self.summoner).first()
                globalGrade += myStats.grade
                for stats in match.participantStats.all():
                    if stats != myStats:
                        ddate = match.date + timedelta(hours=4)
                        tmpRes = {
                            "lastSeen": idx,
                            "mode": match.queue,
                            "time": ddate.strftime("%d-%m-%Y %H:%M"),
                            "win": myStats.win,
                            "myGrade": myStats.grade,
                            "grade": stats.grade,
                            "gradeString": stats.gradeString,
                            "myGradeString": myStats.gradeString,
                            "vs": myStats.win != stats.win,
                            "myScore": f"{myStats.kills}.{myStats.deaths}.{myStats.assists}",
                            "myChamp": myStats.champ,
                            "score": f"{stats.kills}.{stats.deaths}.{stats.assists}",
                            "champ": stats.champ
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
            globalGrade = round((globalGrade / len(self.matches)), 2)
            res = dict(sorted(res.items(), key=lambda item: item[1]["matches"][0]['lastSeen'], reverse=False))
            for k, v in res.items():
                tmpGrade = 0
                myTmpGrade = 0
                tmpLen = len(v['matches'])
                for match in v['matches']:
                    tmpGrade += match['grade']
                    myTmpGrade += match['myGrade']
                res[k]['grade'] = round(tmpGrade / tmpLen, 2)
                res[k]['myGrade'] = round(myTmpGrade / tmpLen, 2)

            i = 0
            rres = dict()
            for k, v in res.items():
                if i == 50:
                    break
                rres[k] = v
                i += 1
            self.founds = rres
            return globalGrade, rres
        return 0, []

    def findSummonnerInActiveMatch(self):
        result = dict()

        try:
            actualMatch = self.lol_watcher.spectator.by_summoner(self.platform, self.summoner.rsummonerId)
            print("GAME STARTED")
            for participant in actualMatch['participants']:
                champ = GameChamp.objects.get(champId=participant['championId'])
                participantName = participant['summonerName']
                # print(participant['summonerName'],  participant['summonerName'] in founds.keys())
                if participantName in self.founds.keys():
                    result[participantName] = self.founds[participantName]
                    result[participantName]['champ'] = champ
                    result[participantName]['notFound'] = False

                else:
                    result[participantName] = dict()
                    result[participantName]['champ'] = champ
                    result[participantName]['notFound'] = True
            return True, result
        except:
            return False, self.founds

    def updateData(self):
        pass

    @staticmethod
    def printMatch(match):
        t = match['time'] / 1000
        return f"{match['lastSeen']} {datetime.fromtimestamp(t).strftime('%d-%m-%Y %H:%M:%S')} {match['mode']} {'W' if match['win'] else 'L'} {'VS' if match['vs'] else 'WITH'} {match['myChamp']} {match['myScore']} vs {match['champ']} {match['score']}"
