# Проект Foodgram "Продуктовый помощник"

## Описание

Foodgram — это онлайн-платформа, где пользователи могут делиться своими кулинарными рецептами, следить за творчеством других авторов, отмечать понравившиеся рецепты и составлять список необходимых продуктов для их приготовления.

Проект реализован с использованием Django REST Framework для серверной части и React — для клиентской стороны.

## Стек технологий
# Backend
*   Python (основной язык)
*   Django (веб-фреймворк)
*   Django REST Framework (DRF) (API)
*   PostgreSQL (база данных)
*   Docker (контейнеризация)
*   Nginx (веб-сервер)
*   Gunicorn (WSGI-сервер)
# Аутентификация и безопасность
*   JWT (JSON Web Tokens) (djangorestframework-simplejwt)
*   Django Auth System (стандартная аутентификация)
# Дополнительные библиотеки
*   Pillow (работа с изображениями)
*   Django Filter (фильтрация данных)
*   Psycopg2 (PostgreSQL адаптер)
*   python-dotenv (переменные окружения)
# Инфраструктура
*   Docker Compose (оркестрация контейнеров)
*   GitHub Actions (CI/CD)
## Основные возможности

*   Регистрация и вход в систему через токен.
*   Просмотр, создание, редактирование и удаление кулинарных рецептов.
*   Фильтрация рецептов по авторам, избранным публикациям и спискам покупок.
*   Добавление рецептов в закладки.
*   Составление списка покупок с возможностью экспорта ингредиентов в виде .txt файла.
*   Подписка на интересных авторов.
*   Просмотр профилей пользователей и контент-мейкеров.
*   Загрузка и удаление аватара через API.
*   Административная панель Django с полнотекстовым поиском и возможностью управлять данными.
*   Подробная документация по API (ReDoc).

## Установка и запуск (Docker Compose)

**Требования:**

*   Установленный и запущенный Docker Desktop (или Docker Engine + Docker Compose).

**Инструкции:**

1.  **Клонируйте репозиторий:**
    ```bash
    git clone git@github.com:pozabeth/foodgram-st.git
    cd foodgram-st
    ```

2.  **Создайте файл `.env` для бэкенда:**
    В директории `backend/` создайте файл `.env` и заполните его по следующему образцу:
    ```dotenv
    # backend/.env

    # Django settings
    SECRET_KEY='your_django_secret_key'
    DEBUG=False
    ALLOWED_HOSTS=localhost,127.0.0.1

    # PostgreSQL settings (должны совпадать с infra/.env)
    POSTGRES_DB=foodgram_db
    POSTGRES_USER=foodgram_user
    POSTGRES_PASSWORD='your_db_password'
    DB_HOST=db
    DB_PORT=5432
    ```
    *(Замените значения-заглушки на ваши реальные данные)*.

3.  **Создайте файл `.env` для инфраструктуры:**
    В директории `infra/` создайте файл `.env` и заполните его переменными для базы данных:
    ```dotenv
    # infra/.env
    POSTGRES_DB=foodgram_db
    POSTGRES_USER=foodgram_user
    POSTGRES_PASSWORD='your_db_password'
    ```
    *(Замените значение-заглушку на ваш реальный пароль)*.

4.  **Соберите и запустите контейнеры:**
    Находясь в корневой директории проекта (`foodgram-st`), выполните команду:
    ```bash
    docker compose -f infra/docker-compose.yml up --build
    ```
    *(При первом запуске или после изменений в коде используйте `--build`. Для последующих запусков достаточно `up`)*.

5.  **Выполните первоначальную настройку бэкенда (в отдельном терминале):**
    *   Применение миграций (выполняется автоматически при запуске):
        ```bash
        docker compose -f infra/docker-compose.yml exec backend python manage.py migrate
        ```
    *   Создание суперпользователя Django:
        ```bash
        docker compose -f infra/docker-compose.yml exec backend python manage.py createsuperuser
        ```
    *   Загрузка ингредиентов в базу данных:
        ```bash
        docker compose -f infra/docker-compose.yml exec backend python manage.py loaddata data/ingredients.json
        docker compose -f infra/docker-compose.yml exec backend python manage.py loaddata data/users.json
        docker compose -f infra/docker-compose.yml exec backend python manage.py loaddata data/recipes.json
        docker compose -f infra/docker-compose.yml exec backend python manage.py loaddata data/recipe_ingredients.json
        docker compose -f infra/docker-compose.yml exec backend python manage.py loaddata data/favorites.json
        docker compose -f infra/docker-compose.yml exec backend python manage.py loaddata data/shopping_cart.json
        docker compose -f infra/docker-compose.yml exec backend python manage.py loaddata data/subscriptions.json
        ```
    *   Сбор статики (выполняется автоматически при запуске):
        ```bash
        docker compose -f infra/docker-compose.yml exec backend python manage.py collectstatic --noinput
        ```

6.  **Доступ к приложению:**
    *   Сайт: [http://localhost](http://localhost)
    *   Админ-панель: [http://localhost/admin/](http://localhost/admin/)
    *   Документация API: [http://localhost/api/docs/](http://localhost/api/docs/)

## Образ Docker Hub

Образ бэкенда доступен на Docker Hub:
[https://hub.docker.com/r/pozabeth/foodgram_backend](https://hub.docker.com/r/pozabeth/foodgram_backend)

## Автор

*   [Сигорская Полина](https://github.com/pozabeth)