#!/bin/bash

PROJECT_DIR="/opt/star-burger"
VENV_DIR="$PROJECT_DIR/myvenv"

cd "$PROJECT_DIR" || {
    echo "Каталог $PROJECT_DIR не найден!"
    exit 1
}

echo "Обновление репозитория..."
git pull
if [ $? -ne 0 ];
then
    echo "Ошибка при обновлении репозитория!"
    exit 1
else
    echo "Репозиторий успешно обновлён!"
fi

echo "Активация виртуального окружения..."
source "$VENV_DIR/bin/activate" || {
    echo "Не удалось активировать виртуальное окружение!"
    exit 1
}

echo "Установка Python-зависимостей..."
pip install -r requirements.txt
if [ $? -ne 0 ];
then
    echo "Ошибка при установке Python-зависимостей!"
    exit 1
fi

echo "Установка Node.js-зависимостей..."
npm ci --dev
if [ $? -ne 0 ];
then
    echo "Ошибка при установке Node.js-зависимостей!"
    exit 1
fi

echo "Сборка JS-кода..."
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
if [ $? -ne 0 ];
then
    echo "Ошибка при сборке JS-кода!"
    exit 1
fi

echo "Сборка статики Django..."
python manage.py collectstatic --noinput
if [ $? -ne 0 ];
then
    echo "Ошибка при сборке статики!"
    exit 1
fi

echo "Применение миграций..."
python manage.py migrate
if [ $? -ne 0 ];
then
    echo "Ошибка при применении миграций!"
    exit 1
fi

echo "Перезапуск сервисов..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx
if [ $? -ne 0 ];
then
    echo "Ошибка при перезапуске сервисов!"
    exit 1
fi

echo "Деплой завершён успешно!"
