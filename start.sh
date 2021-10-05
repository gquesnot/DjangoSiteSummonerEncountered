pkill gunicorn
gunicorn LolSummonerEncountered.wsgi --bind 0.0.0.0:8000 --workers 1 --timeout 60000 --graceful-timeout 60000