import sqlite3
import pandas as pd
from pathlib import Path
import logging
import os

# Настройка логирования
log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs', 'db_reader.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseReader:
    def __init__(self, db_path):
        self.db_path = Path(db_path)
        self.conn = None
        self.cursor = None

    def connect(self):
        """Установка соединения с базой данных"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            logger.info(f"Успешное подключение к базе данных: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Ошибка при подключении к базе данных: {e}")
            raise

    def get_tables(self):
        """Получение списка всех таблиц в базе данных"""
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = self.cursor.fetchall()
            return [table[0] for table in tables]
        except sqlite3.Error as e:
            logger.error(f"Ошибка при получении списка таблиц: {e}")
            return []

    def get_table_schema(self, table_name):
        """Получение схемы таблицы"""
        try:
            self.cursor.execute(f"PRAGMA table_info({table_name});")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Ошибка при получении схемы таблицы {table_name}: {e}")
            return []

    def read_table_to_dataframe(self, table_name):
        """Чтение таблицы в pandas DataFrame"""
        try:
            query = f"SELECT * FROM {table_name}"
            df = pd.read_sql_query(query, self.conn)
            logger.info(f"Успешно прочитана таблица {table_name}, получено {len(df)} строк")
            return df
        except Exception as e:
            logger.error(f"Ошибка при чтении таблицы {table_name}: {e}")
            return None

    def save_to_csv(self, df, output_path):
        """Сохранение DataFrame в CSV файл"""
        try:
            df.to_csv(output_path, index=False)
            logger.info(f"Данные успешно сохранены в {output_path}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении в CSV: {e}")

    def close(self):
        """Закрытие соединения с базой данных"""
        if self.conn:
            self.conn.close()
            logger.info("Соединение с базой данных закрыто")

def main():
    # Путь к базе данных (нужно будет заменить на реальный путь)
    db_path = "data/evraz-hackathon.db"
    
    # Создание экземпляра читателя базы данных
    reader = DatabaseReader(db_path)
    
    try:
        # Подключение к базе данных
        reader.connect()
        
        # Получение списка таблиц
        tables = reader.get_tables()
        logger.info(f"Найдены таблицы: {tables}")
        
        # Для каждой таблицы получаем схему и сохраняем данные
        for table in tables:
            schema = reader.get_table_schema(table)
            logger.info(f"Схема таблицы {table}:")
            for column in schema:
                logger.info(f"  {column}")
            
            # Чтение данных
            df = reader.read_table_to_dataframe(table)
            if df is not None:
                # Сохранение в CSV
                output_path = f"data/{table}.csv"
                reader.save_to_csv(df, output_path)
    
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
    
    finally:
        reader.close()

if __name__ == "__main__":
    main() 