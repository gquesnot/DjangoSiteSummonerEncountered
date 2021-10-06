pkill gunicorn
git pull
python manage.py collectstatic --no-input --clear && gunicorn LolSummonerEncountered.wsgi --workers 1 -t 6000 --bind 0.0.0.0:8000 -D