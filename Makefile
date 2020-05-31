build:
	docker-compose build

up:
	docker-compose up -d

up-non-daemon:
	docker-compose up

start:
	docker-compose start

stop:
	docker-compose stop

restart:
	docker-compose stop && docker-compose start

shell-nginx:
	docker exec -ti djshop-nginx /bin/sh

shell-web:
	docker exec -ti djshop-web /bin/sh

shell-db:
	docker exec -ti djshop-postgres /bin/sh

log-nginx:
	docker-compose logs nginx

log-web:
	docker-compose logs web

log-db:
	docker-compose logs db

collectstatic:
	docker exec -it djshop-web /bin/sh -c "python manage.py collectstatic"

createsuperuser:
	docker exec -it djshop-web /bin/sh -c "python manage.py createsuperuser"

pushapi:
	git add .; git commit -m "update"; git push origin master

pushdashboard:
	cd ../djshop_admin; git add .; git commit -m "update"; git push origin master

pushyanxuan:
	cd ../yanxuan; git add .; git commit -m "update"; git push origin master

pushall: pushapi pushdashboard pushyanxuan

deployapi:
	ssh root@118.25.78.11 "cd djshop; git pull origin master; supervisorctl restart djshop_gunicorn; exit"

deploydashboard:
	cd ../djshop_admin; npm run build; scp -r dist/ root@118.25.78.11:/root/djshop_admin/

deployall: deployapi deploydashboard
