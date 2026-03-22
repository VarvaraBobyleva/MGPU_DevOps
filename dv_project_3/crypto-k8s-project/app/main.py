import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os
import random

engine = create_engine(f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:5432/{os.getenv('DB_NAME')}")

st.title("📈 Crypto Time-Series Analytics Bitcoin")

@st.cache_data(ttl=600)
def load_random_time_window():
    with engine.connect() as conn:
        # 1. Находим границы времени
        res = pd.read_sql("SELECT MIN(timestamp) as mn, MAX(timestamp) as mx FROM crypto_stats", conn)
        mn, mx = int(res['mn'][0]), int(res['mx'][0])
        
        # 2. Выбираем случайное окно в 500 записей (минут)
        window_size = 500
        start_t = random.randint(mn, mx - (window_size * 60))
        
        # 3. Загружаем данные
        query = f"SELECT * FROM crypto_stats WHERE timestamp >= {start_t} LIMIT {window_size}"
        df = pd.read_sql(query, conn)
        
        # Превращаем timestamp в понятную дату
        df['date'] = pd.to_datetime(df['timestamp'], unit='s')
        return df

# Добавим кнопку для ручного обновления выборки
if st.button('🔄 Сгенерировать новую выборку'):
    st.cache_data.clear()
    st.rerun()

try:
    df = load_random_time_window()

    # 1. Линейный график цены (вместо карты)
    st.subheader("Динамика цены закрытия (Close)")
    fig_price = px.line(df, x='date', y='close', title="Price Movement")
    st.plotly_chart(fig_price, use_container_width=True)

    # 2. График объема торгов (Area Chart)
    st.subheader("Изменение объемов торгов (Volume)")
    fig_vol = px.area(df, x='date', y='volume', title="Trading Volume Over Time", color_discrete_sequence=['orange'])
    st.plotly_chart(fig_vol, use_container_width=True)

    # 3. Выводы по конкретному периоду
    st.divider()
    st.write(f"**Анализ периода:** с {df['date'].min()} по {df['date'].max()}")
    st.write(f"- Максимальная цена в этом окне: **{df['close'].max():.2f}**")
    st.write(f"- Средний объем торгов: **{df['volume'].mean():.2f}**")

except Exception as e:
    st.error(f"Ошибка: {e}")
