import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import psycopg2
import os

# Настройка страницы
st.set_page_config(page_title="Crypto Analytics", layout="wide")
st.title("📈 Crypto Volatility Dashboard")

# 1. Функция с очисткой кэша
@st.cache_data(ttl=600) # Кэш живет 10 минут, если не нажать кнопку

# Функция подключения к БД
def get_data():
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST')
    )

    # 1. Сначала узнаем общее количество строк
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM crypto_stats")
    total_rows = cur.fetchone()[0]
    
    # 2. Выбираем случайную точку старта (отступ), чтобы не выйти за пределы
    import random
    offset = random.randint(0, max(0, total_rows - 300)) 

    # 3. Берем 1000 ПОДРЯД идущих строк — это идеальное количество для экрана
    query = f"SELECT * FROM crypto_stats ORDER BY timestamp ASC LIMIT 1000 OFFSET {offset}"
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Превращаем timestamp (Unix) в понятную дату
    df['date'] = pd.to_datetime(df['timestamp'], unit='s')
    return df

# 2. Кнопка обновления данных
if st.button('🔄 Обновить выборку данных'):
    st.cache_data.clear() # Полностью очищаем кэш Streamlit
    st.rerun()           # Перезапускаем скрипт, чтобы загрузить новые RANDOM строки


try:
    df = get_data()

    # --- БЛОК 1: Метрики ---
    col1, col2, col3 = st.columns(3)
    last_price = df['close'].iloc[-1]
    price_change = df['close'].iloc[-1] - df['open'].iloc[0]
    
    col1.metric("Текущая цена (Close)", f"${last_price:,.2f}")
    col2.metric("Изменение за период", f"${price_change:,.2f}", delta_color="normal")
    
    # Считаем волатильность (разница между High и Low)
    df['volatility'] = (df['high'] - df['low']) / df['low'] * 100
    avg_vol = df['volatility'].mean()
    col3.metric("Средняя волатильность", f"{avg_vol:.2f}%")

    # --- БЛОК 2: График "Японские свечи" ---
    st.subheader("Динамика цены (Candlestick Chart)")
    fig_candle = go.Figure(data=[go.Candlestick(
    	x=df['date'],
    	open=df['open'], 
	high=df['high'],
    	low=df['low'], 
	close=df['close'],
	name="Цена",
    	increasing_line_color= '#26a69a', 
	decreasing_line_color= '#ef5350' # Сочные цвета
    )])
    fig_candle.update_layout(
    	xaxis_rangeslider_visible=False, 
    	height=500,
    	margin=dict(l=10, r=10, t=10, b=10),
    	template="plotly_white" # Чистый белый фон
    )
    st.plotly_chart(fig_candle, use_container_width=True)

    # --- БЛОК 3: Объем торгов и Волатильность ---
    st.subheader("Анализ объема и волатильности")
    c1, c2 = st.columns(2)
    
    with c1:
        st.write("Объем торгов (Volume)")
        st.bar_chart(df.set_index('date')['volume'])
        
    with c2:
        st.write("Внутриминутная волатильность (%)")
        st.line_chart(df.set_index('date')['volatility'])

    # --- БЛОК 4: Выводы ---
    st.divider()
    st.subheader("📋 Аналитический отчет")
    
    max_vol_row = df.loc[df['volatility'].idxmax()]
    
    st.info(f"""
    **Краткие выводы по данным:**
    *   **Максимальный всплеск волатильности:** зафиксирован в `{max_vol_row['date']}` и составил `{max_vol_row['volatility']:.4f}%`.
    *   **Тренд:** На основе последних `{len(df)}` записей, цена движется {'вверх 📈' if price_change > 0 else 'вниз 📉'}.
    *   **Корреляция:** Высокие объемы торгов часто совпадают с периодами повышенной волатильности.
    """)

except Exception as e:
    st.error(f"Ошибка: {e}")
    st.info("Убедитесь, что loader.py уже загрузил данные в таблицу 'crypto_stats'.")
