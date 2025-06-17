import pika
import json
import pandas as pd
import os

RABBITMQ_HOST = 'localhost'
RABBITMQ_QUEUE = 'test_queue'
CSV_FILE = 'data/rabbitmq_log.csv'

# Проверяем, существует ли файл CSV
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=['number', 'text'])
    df.to_csv(CSV_FILE, index=False)

# Функция обработки сообщений
def callback(ch, method, properties, body):
    message = json.loads(body.decode('utf-8'))
    print(f"[x] Получено: {message}")
    # Добавляем сообщение в CSV
    df = pd.read_csv(CSV_FILE)
    df = pd.concat([df, pd.DataFrame([message])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

# Установка соединения с RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
channel = connection.channel()

# Подписка на очередь
channel.queue_declare(queue=RABBITMQ_QUEUE)
channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback, auto_ack=True)

print('[*] Ожидание сообщений. Для выхода нажмите CTRL+C')
channel.start_consuming() 