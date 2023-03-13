[![Django-app workflow](https://github.com/iPROJEKT/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/iPROJEKT/foodgram-project-react/actions/workflows/main.yml)


#  Проект «Продуктовый помощник»

Привет! Это мой полноценный проект, сделанный на Django + rest framework + Djoser. Этот сайт предназначен для поста рецептов(с описанием, фотографией, тегами, ингридиентами). Он устроен довольно просто. 


# Для того чтоб запустить его на ВМ, нужно:
## Заполнение .env
*Шаблон env файла*
* EMAIL_HOST_PASSWORD= пароль от почты с которой будет отправляться код для подтверждения 
* EMAIL_HOST_USER= логин почты
* DB_ENGINE= испольщзуемая база данных
* DB_NAME= имя базы
* POSTGRES_USER= имя для захода в базу
* POSTGRES_PASSWORD= пароль от базы
* DB_HOST=db
* DB_PORT= порт
# Описание команд для запуска приложения в контейнерах
- ```docker-compose up -d --build``` - для того чтоб забилдить и контейнеры (без логов -d)d
- ```docker-compose exec backend python manage.py migrate``` (миграции)
- ```docker-compose exec backend python manage.py createsuperuser``` (создание суперюзера)
- ```docker-compose exec backend python manage.py collectstatic --no-input``` (сбор статических файлов)
# Для того чтоб посмотеть мой проект
## Перейдите по этой ссылке http://130.193.38.54/

Admin name: root
Admin password: Qwerty123
