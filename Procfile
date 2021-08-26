web: gunicorn lputormis.wsgi --timeout 1200
beat: celery -A lputormis beat -l info
worker: celery -A lputormis worker -l INFO
