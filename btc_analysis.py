import ccxt
import pandas as pd
from datetime import datetime
import numpy as np

def fetch_ohlcv(symbol="BTC/USDT", timeframe="1h", limit=100):
    exchange = ccxt.okx()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

def calculate_ema(df, period=21):
    return df["close"].ewm(span=period, adjust=False).mean()

def calculate_rsi(df, period=14):
    delta = df["close"].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def detect_smart_money(df):
    # Простая логика: сильные хвосты или всплеск объёма
    recent = df.iloc[-1]
    body = abs(recent["close"] - recent["open"])
    wick = recent["high"] - recent["low"]
    if recent["volume"] > df["volume"].rolling(20).mean().iloc[-1] * 1.5:
        return True
    if wick > body * 2:
        return True
    return False

def generate_btc_signal():
    df = fetch_ohlcv()
    df["ema21"] = calculate_ema(df)
    df["rsi14"] = calculate_rsi(df)
    
    last = df.iloc[-1]
    prev = df.iloc[-2]

    support = round(df["low"].rolling(20).min().iloc[-1], 2)
    resistance = round(df["high"].rolling(20).max().iloc[-1], 2)

    signal = None
    reasons = []

    if last["close"] > last["ema21"] and last["rsi14"] < 70:
        signal = "LONG"
        reasons.append("Цена выше EMA 21")
    elif last["close"] < last["ema21"] and last["rsi14"] > 30:
        signal = "SHORT"
        reasons.append("Цена ниже EMA 21")

    if last["rsi14"] > 70:
        reasons.append("RSI перекуплен — возможна коррекция")
    elif last["rsi14"] < 30:
        reasons.append("RSI перепродан — возможен разворот")

    if detect_smart_money(df):
        reasons.append("Обнаружен Smart Money импульс")

    entry = round(last["close"], 2)
    sl = round(entry * 0.985 if signal == "LONG" else entry * 1.015, 2)
    tp1 = round(entry * 1.01 if signal == "LONG" else entry * 0.99, 2)
    tp2 = round(entry * 1.02 if signal == "LONG" else entry * 0.98, 2)
    tp3 = round(entry * 1.03 if signal == "LONG" else entry * 0.97, 2)

    reasons_text = "\n- ".join(reasons)
    message = f"""
📊 BTC/USDT Анализ (1H OKX)

🕒 {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC

📈 Сигнал: {signal if signal else 'Нет сигнала'}
🎯 Вход: {entry}
🛡️ Стоп-лосс: {sl}
💰 Тейки:
 • TP1: {tp1}
 • TP2: {tp2}
 • TP3: {tp3}

📉 RSI: {round(last['rsi14'], 2)}
📊 Объём: {round(last['volume'], 2)}
📏 EMA21: {round(last['ema21'], 2)}

📌 Поддержка: {support}
📌 Сопротивление: {resistance}

🔍 Причины:
- {reasons_text}

⏳ {'ВХОДИМ ✅' if signal else 'ЖДЕМ 📉'}
""".strip()

    return message

if __name__ == "__main__":
    print(generate_btc_signal())
