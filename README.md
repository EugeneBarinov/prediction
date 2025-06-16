# Проект обработки данных

## Описание
Проект для чтения данных из базы данных, их обработки через RabbitMQ и визуализации.

## Структура проекта
```
projectel/
├── src/
│   ├── database/     # Модули для работы с БД
│   ├── rabbitmq/     # Модули для работы с RabbitMQ
│   ├── web/          # Веб-приложение
│   └── utils/        # Вспомогательные функции
├── data/            # Директория для CSV файлов
├── logs/            # Директория для логов
└── config/          # Конфигурационные файлы
```

## Установка
1. Создать виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

2. Установить зависимости:
```bash
pip install -r requirements.txt
```

## Использование
1. Настройка конфигурации в файле .env
2. Запуск скриптов:
   - Чтение из БД: `python src/database/reader.py`
   - Отправка в RabbitMQ: `python src/rabbitmq/publisher.py`
   - Получение из RabbitMQ: `python src/rabbitmq/consumer.py`
   - Запуск веб-приложения: `python src/web/app.py` 