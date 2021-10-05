from django.shortcuts import render
from django.views import View

from LolApp.util.LolSummonerClass import LolSummoner


class Home(View):

    def get(self, request):
        return render(request, "home.html")

    def post(self, request):
        ls = LolSummoner(request.POST['summonerName'])
        ls.updateHistory()
        founds = ls.convertMatchHistoryToSummonerNameDictWithMatch()
        inGame, currentFounds = ls.findSummonnerInActiveMatch()
        if currentFounds is not None:
            return render(request, "home.html", {"datas": zip(range(len(currentFounds.keys())),currentFounds.keys(), currentFounds.values()), "inGame": inGame})
        else:

            return render(request, "home.html", {"inGame": inGame})