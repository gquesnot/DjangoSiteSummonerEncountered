from django.shortcuts import render
from django.views import View

from LolApp.util.LolSummonerClass import LolSummoner


class Home(View):


    def get(self, request):
        return render(request, "home.html")

    def post(self, request):
        myRegion = request.POST['myRegion']

        summonerName = request.POST['summonerName']
        ls = LolSummoner(summonerName, myRegion)
        if ls.confOk:
            ls.updateHistory()
            globalGrade, founds = ls.convertMatchHistoryToSummonerNameDictWithMatch()
            inGame, currentFounds = ls.findSummonnerInActiveMatch()
            return render(request, "home.html", {"gGrade":globalGrade,"datas": zip(range(len(currentFounds.keys())),currentFounds.keys(), currentFounds.values()), "inGame": inGame, "summonerName": summonerName})
        else:
            print("badCOnfig")
            return render(request, "home.html", {"summonerName": summonerName})