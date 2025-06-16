import pika
import json
import time
import sqlite3
import pandas as pd

RABBITMQ_HOST = 'localhost'
RABBITMQ_QUEUE = 'test_queue'
DB_PATH = 'data/evraz-hackathon.db'
TABLE_NAME = 'tblData'
INTERVAL = 10  # секунд

# Получение новых данных из базы данных
last_timestamp = None

def get_next_row(conn, last_ts):
    query = f"SELECT * FROM {TABLE_NAME}"
    if last_ts is not None:
        query += f" WHERE timestamp > {last_ts}"
    query += " ORDER BY timestamp ASC LIMIT 1"
    df = pd.read_sql_query(query, conn)
    return df

# Установка соединения с RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
channel = connection.channel()

# Создание очереди, если не существует
channel.queue_declare(queue=RABBITMQ_QUEUE)

# Основной цикл
with sqlite3.connect(DB_PATH) as conn:
    while True:
        df = get_next_row(conn, last_timestamp)
        if not df.empty:
            # Обновляем last_timestamp
            last_timestamp = df['timestamp'].iloc[0]
            # Преобразуем строку в словарь
            data = df.to_dict(orient='records')[0]
            # Отправляем пакет данных
            channel.basic_publish(
                exchange='',
                routing_key=RABBITMQ_QUEUE,
                body=json.dumps(data).encode('utf-8')
            )
            print(f"[x] Отправлена строка с timestamp={last_timestamp}")
        else:
            print("[ ] Новых данных нет")
        time.sleep(INTERVAL)

connection.close() 