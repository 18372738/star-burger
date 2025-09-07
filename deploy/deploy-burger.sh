#!/bin/bash
set -e

PROJECT_DIR="/opt/star-burger"
VENV_DIR="$PROJECT_DIR/myvenv"

cd "$PROJECT_DIR"

echo "Обновление репозитория..."
git pull

echo "Активация виртуального окружения..."

echo "Установка Python-зависимостей..."
pip install -r requirements.txt

echo "Установка Node.js-зависимостей..."
npm ci --dev

echo "Сборка JS-кода..."
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

echo "Сборка статики Django..."
python manage.py collectstatic --noinput

echo "Применение миграций..."
python manage.py migrate

echo "Перезапуск сервиса..."
sudo systemctl restart star-burger.service

echo "Деплой завершён успешно!"

bash /opt/star-burger/deploy/message_rollbar.sh
