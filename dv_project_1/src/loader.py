import pandas as pd
import os

def load_bitcoin_data():
    path = 'data/bitcoin_data.csv' # Укажите название вашего файла
    if os.path.exists(path):
        # В учебных целях просто имитируем чтение
        print(f"Загрузка данных из {path}...")
        # df = pd.read_csv(path) 
        print("Данные успешно загружены. Начинаем анализ волатильности.")
    else:
        print("Файл с данными не найден!")

if __name__ == "__main__":
    load_bitcoin_data()
