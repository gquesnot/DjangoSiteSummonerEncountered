## WEBAPP IN PYTHON THAT USE DJANGO TO CHECK IF YOU HAVE ALREADY ENCOUNTERED SOMEONE IN YOUR GAME

### if you are not in game show you all Summoner Encountered



#### Installation

```
pip install -r requirements.txt
```
- set up your apiKey in config.json and the region 
- if needed you can also increase the max matches you get the first time your run it for a Summoner

The first time, it will take some time to download all the match history to the database after it will only update the new matches.


#### Run

```
python manage.py runserver
```