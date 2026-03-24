import psycopg2
import pandas as pd
import os
import time

# Даем базе 5 секунд на прогрев
time.sleep(5)

# Путь к файлу внутри контейнера (из bind mount)
FILE_PATH = 'dv_project_4/CryptoDash_CI/data/crypto_data.csv'

def load_csv_to_db():
    try:
        # 1. Читаем CSV через pandas
        df = pd.read_csv(FILE_PATH)
        
        # Подключаемся к БД
        conn = psycopg2.connect(
            dbname=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            host=os.getenv('DB_HOST')
        )
        cur = conn.cursor()

        # 2. Создаем таблицу под твой формат данных
        cur.execute("""
            CREATE TABLE IF NOT EXISTS crypto_stats (
                timestamp BIGINT,
                asset_id INT,
                open FLOAT,
                high FLOAT,
                low FLOAT,
                close FLOAT,
                volume FLOAT
            );
        """)

        # 3. Загружаем данные (берем основные колонки для примера)
        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO crypto_stats (timestamp, asset_id, open, high, low, close, volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    int(row['timestamp']),          # Превращаем в обычный int
                    int(row['Asset_ID']),           # Превращаем в обычный int
                    float(row['Open']),             # Превращаем в обычный float
                    float(row['High']),             # Превращаем в обычный float
                    float(row['Low']),              # Превращаем в обычный float
                    float(row['Close']),            # Превращаем в обычный float
                    float(row['Volume'])            # Превращаем в обычный float
            ))

        conn.commit()
        print(f"Успешно загружено {len(df)} строк!")
        
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Ошибка при загрузке: {e}")

if __name__ == "__main__":
    load_csv_to_db()
