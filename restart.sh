git pull
pkill gunicorn
gunicorn LolSummonerEncountered.wsgi --bind 0.0.0.0:8000 --workers 1 -t 600 -D