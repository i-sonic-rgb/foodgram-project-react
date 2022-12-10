ReadMe
# Проект Foodgram
![event parameter](https://github.com/i-sonic-rgb/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg?event=push)

https://github.com/i-sonic-rgb/foodgram-project-react

## Общее описание
Проект сайта для рецептов и списков покупок. Авторизованные пользователи могут
создавать рецепты с использованием предустановленных ингридиентов и тэгов. 
Незарегистрированные пользователи могут просматривать рецепты. Авторизованные
пользователи могут подписываться на других пользователей, добавлять рецепты
в избранное и список покупок, а также скачивать список покупок, который состоит
из перечня ингридиентов необходимых для приготовления блюда (pdf).

Проект доступен по адресу: http://sonicyap.myftp.org или по IP: 158.160.12.170 

### Технологии
- Python 
- Django 
- DjangoRest Framework
- Nginx
- Gunicorn
- Docker, Docker compose
- GitHub Workflow

## Инструкция по запуску на локальном компьютере
### Шаблон .env файла
- DB_ENGINE - указывается вид БД (по умолчанию - 'django.db.backends.postgresql')
- DB_NAME - имя базы данных (по умолчанию - 'postgres')
- POSTGRES_USER - логин для подключения к базе данных (по умолчанию - 'postgres')
- POSTGRES_PASSWORD - пароль для подключения к БД (установите свой)
- DB_HOST - название сервиса БД (контейнера; по умолчанию 'db')
- DB_PORT - порт доступа к БД (по умолчанию - 5432)
- DJANGO_SECRET_KEY - секретный код для доступа к Джанго (settings.py SECRET_KEY)

### Запуск docker контейнеров
- клонируйте проект в рабочую папку: sudo git clone ...
- установите docker и docker-compose: https://docs.docker.com/compose/install/
- в терминале откройте папку /infra/
- запустите контейнеры: sudo docker-compose up
- если после запуска потребуется обновить код - внесите правки и в терминале наберите sudo docker-compose up -d --build
- чтобы удалить контейнеры и зависимости: sudo docker-compose down -v

## Инструкция по запуску на сервере
- На сервере должны быть установлены Docker, docker-compose
- После развертывания контейнеров рекомендуется выполнить команду sudo docker-compose exec web python manage.py migrate
- для загрузки предустановленных данных, включая список ингредиентов, тэгов, пользователей и суперпользователя, наберите sudo docker-compose exec web python manage.py uploaddata
- Если в .env указано DEBUG=True, рабочая БД - SQLite, в иных случаях = Postgres

## Доступные эндпоинты
- 158.160.12.170/admin/ - панель администирования
- 158.160.12.170/api/ - api сайта

## Автор
### Бэкенд, инфраструктура, workflow и развертывание на сервере:
- Igor Poliakov
### Фронтэнд, перечень рецептов
- Предоставлен Яндекс Практикум (https://practicum.yandex.ru) 
