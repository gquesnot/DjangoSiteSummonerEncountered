## WEBAPP IN PYTHON THAT USE DJANGO TO CHECK IF YOU HAVE ALREADY ENCOUNTERED SOMEONE IN YOUR GAME AND SEE GRADE

##### if you are not in game show you all Summoner Encountered
##### About Grade [see](https://maddcog.medium.com/measure-league-of-legends-performance-with-this-game-grade-778c2fe832cb), i'm not the autor


## Installation


### Python
```
pip install -r requirements.txt
```


### Docker

```
docker-compose -f docker-compose.yml up -d
```

### INSTRUCTIONS
- set up your apiKey in config.json
- if needed you can also increase the max matches you get the first time your run it for a Summoner

The first time, it will take some time to download all the match history to the database after it will only update the new matches.


## Run

```
python manage.py runserver
```

## DEMO

[Link](http://13.37.99.139/)