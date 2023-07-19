[![Django-app workflow](https://github.com/iPROJEKT/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/iPROJEKT/foodgram-project-react/actions/workflows/main.yml)
# Проект «Продуктовый помощник»
Дипломный проект — сайт Foodgram, «Продуктовый помощник». На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд. В этом проекте так же мы использовали Docker + compose для отправки на вм. Помимо "сухого" backenda, тут присутсвует frontend на реакте
### Для того чтоб запустить его на ВМ, нужно:
 Заполнение .env
*Шаблон env файла*
```
* EMAIL_HOST_PASSWORD= пароль от почты с которой будет отправляться код для подтверждения 
* EMAIL_HOST_USER= логин почты
* DB_ENGINE= испольщзуемая база данных
* DB_NAME= имя базы
* POSTGRES_USER= имя для захода в базу
* POSTGRES_PASSWORD= пароль от базы
* DB_HOST=db
* DB_PORT= порт
```
### Описание команд для запуска приложения в контейнерах
```
docker-compose up -d --build` - для того чтоб забилдить и контейнеры (без логов -d)
docker-compose exec backend python manage.py migrate (миграции)
docker-compose exec backend python manage.py createsuperuser (создание суперюзера)
docker-compose exec backend python manage.py collectstatic --no-input (сбор статических файлов)
```

### python + DRF + Djoser
