# Foodgram - Продуктовый помощник

Foodgram — сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Технологии

- Python 3.11
- Django 4.2
- Django REST Framework
- Djoser (аутентификация по токену)
- PostgreSQL
- Nginx
- Docker / Docker Compose
- GitHub Actions (CI/CD)

## Запуск проекта

### Локальный запуск (Docker Compose)

1. Клонируйте репозиторий:
```bash
git clone <repo_url>
cd foodgram-main
```

2. Создайте файл `.env` в директории `infra/`:
```bash
cp infra/.env.example infra/.env
# Заполните переменные в .env
```

3. Запустите контейнеры:
```bash
cd infra
docker-compose up -d --build
```

4. Загрузите ингредиенты:
```bash
docker-compose exec backend python manage.py load_ingredients
```

5. Создайте суперпользователя:
```bash
docker-compose exec backend python manage.py createsuperuser
```

6. Проект доступен по адресу: http://localhost/

## Документация API

Документация API доступна по адресу: http://localhost/api/docs/

## Структура проекта

```
foodgram-main/
├── backend/          # Django бэкенд
│   ├── foodgram_project/  # Настройки проекта
│   ├── users/        # Приложение пользователей
│   ├── recipes/      # Приложение рецептов
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/         # React фронтенд
├── infra/            # Инфраструктура
│   ├── docker-compose.yml
│   ├── nginx.conf
│   └── .env.example
├── data/             # Данные для загрузки
└── docs/             # Документация API
```
