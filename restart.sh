git pull
pkill gunicorn
python manage.py collectstatic -y
gunicorn LolSummonerEncountered.wsgi --bind 0.0.0.0:8000 --workers 1 --timeout 600000 --graceful-timeout 600000 -D