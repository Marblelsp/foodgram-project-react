![example workflow](https://github.com/marblelsp/foodgram-project-react/actions/workflows/foodgram-project-react_workflow.yaml/badge.svg) 
# Foodgram

«Продуктовый помощник» (Проект Яндекс.Практикум)

Описание

Foodgram - онлайн сервис, который позволяет пользователям делится своими самыми вкусными рецептами и подпичываться на других авторов. Сервис позволяет сортировать рецепты по тегам, избранным рецептам и добавлять понравившиеся блюда в список покупок.
Так же сервис позволяет скачивать список покупок перед походом в магазин, в котором содержатся все необходимые ингредиенты для приготовления.

-----------------
Установка

1. Клонируйте себе репозиторий с проектом 
```python
git clone https://github.com/Marblelsp/foodgram-project-react.git
```
2. Заполните файл .env в директории backend/foodgram/foodgram/ для работы с бд postgresql.
```python
DB_ENGINE=django.db.backends.postgresql
DB_NAME=foodgram
POSTGRES_DB=foodgram
POSTGRES_USER=your_postgre_user
POSTGRES_PASSWORD=your_postgre_password
DB_HOST=db
DB_PORT=5432
```
3. Перейдите в папку infra и выполните команду
```python
docker-compose up -d --build
```
4. Выполните последовательно следующие команды: миграции, загрузка бд ингредиентов и тегов, подгрузка статики.

```python
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py loaddata ingredients.json
docker-compose exec backend python manage.py loaddata tags.json
```
После выполнения данных шагов сервис готов к работе по адресу: http://127.0.0.1/signin

Работу готового сервиса можете протестировать по адресу http://foodgramex.co.vu/
