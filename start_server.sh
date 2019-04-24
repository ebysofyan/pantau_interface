export MYSQL_PASSWORD=mysql123 
cd /home/eby/pemilu2019/pantau_interface
exec /opt/anaconda3/bin/gunicorn config.wsgi -b 0.0.0.0:2019 
