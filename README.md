# Foodgram — Продуктовый помощник

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
git clone https://github.com/surok111/foodgram
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

### Деплой на сервер

Проект разворачивается автоматически через GitHub Actions при пуше в ветку `main`.

Необходимые секреты в репозитории (`Settings → Secrets and variables → Actions`):

| Секрет | Описание |
|---|---|
| `DOCKER_USERNAME` | Логин на Docker Hub |
| `DOCKER_PASSWORD` | Пароль или access-token Docker Hub |
| `HOST` | IP-адрес сервера |
| `USER` | Пользователь для SSH |
| `SSH_KEY` | Приватный SSH-ключ |
| `SSH_PASSPHRASE` | Пароль от SSH-ключа (если есть) |
| `TELEGRAM_TO` | ID Telegram-чата для уведомлений |
| `TELEGRAM_TOKEN` | Токен Telegram-бота |

На сервере заранее создайте файл `~/foodgram/.env`:
```
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_HOST=db
DB_PORT=5432
SECRET_KEY=ваш_секретный_ключ
DEBUG=False
ALLOWED_HOSTS=ваш_домен_или_ip,localhost,127.0.0.1
DOCKER_USERNAME=surok111
```

## Документация API

Документация API доступна по адресу: http://localhost/api/docs/

## Примеры запросов к API

### Регистрация пользователя

```
POST /api/users/
```
```json
{
  "email": "user@example.com",
  "username": "username",
  "first_name": "Иван",
  "last_name": "Иванов",
  "password": "Qwerty123"
}
```

### Получение токена

```
POST /api/auth/token/login/
```
```json
{
  "email": "user@example.com",
  "password": "Qwerty123"
}
```

### Список рецептов

```
GET /api/recipes/
```
Поддерживает фильтрацию: `?is_favorited=1`, `?is_in_shopping_cart=1`, `?author=1`, `?tags=breakfast`

### Создание рецепта

```
POST /api/recipes/
Authorization: Token <ваш_токен>
```
```json
{
  "ingredients": [{"id": 1, "amount": 200}],
  "tags": [1, 2],
  "image": "data:image/png;base64,...",
  "name": "Омлет",
  "text": "Приготовить омлет",
  "cooking_time": 10
}
```

### Добавить рецепт в избранное

```
POST /api/recipes/{id}/favorite/
Authorization: Token <ваш_токен>
```

### Скачать список покупок

```
GET /api/recipes/download_shopping_cart/
Authorization: Token <ваш_токен>
```

Возвращает `.txt`-файл со списком ингредиентов.

### Подписаться на автора

```
POST /api/users/{id}/subscribe/
Authorization: Token <ваш_токен>
```

## Структура проекта

```
foodgram-main/
├── backend/               # Django бэкенд
│   ├── foodgram_project/  # Настройки проекта
│   ├── users/             # Приложение пользователей
│   ├── recipes/           # Приложение рецептов
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/              # React фронтенд
├── infra/                 # Инфраструктура
│   ├── docker-compose.yml
│   ├── docker-compose.production.yml
│   ├── nginx.conf
│   └── Dockerfile
├── .github/workflows/     # CI/CD pipeline
│   └── main.yml
├── data/                  # Данные для загрузки
├── docs/                  # Документация API
└── tests.yml              # Конфигурация тестов
```

## Автор

**surok111** — [GitHub](https://github.com/surok111)
