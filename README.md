# instagramDownloader
Download all profile photos to archive with Celery


1) Install requirments from requirments.txt
2) rabbitmq-server
3) Run python3 manage.py makemigrations   
4) Run python3 manage.py migrate
5) Run python3 manage.py runserver
6) Run celery in other window celery worker -A instagramDownloader --loglevel=info
7) Run celery-beat in iother window celery beat -A instagrDownloader --loglevel=info
8) Go to 127.0.0.1:8000  type user nickname
