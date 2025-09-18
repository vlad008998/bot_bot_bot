import ccxt
import pandas as pd
import ta

def generate_btc_signal():
    exchange = ccxt.okx({
        'enableRateLimit': True,
    })

    symbol = 'BTC/USDT'
    timeframe = '1h'
    limit = 100

    # Получаем исторические данные OHLCV
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

    df['ema20'] = ta.trend.ema_indicator(df['close'], window=20)
    df['ema50'] = ta.trend.ema_indicator(df['close'], window=50)
    df['rsi'] = ta.momentum.rsi(df['close'], window=14)

    last = df.iloc[-1]
    previous = df.iloc[-2]

    support = df['low'].rolling(window=20).min().iloc[-1]
    resistance = df['high'].rolling(window=20).max().iloc[-1]

    signal = "NO TRADE"
    reason = ""

    if last['ema20'] > last['ema50'] and last['rsi'] > 55:
        signal = "LONG"
        reason = "EMA20 > EMA50 и RSI > 55"
    elif last['ema20'] < last['ema50'] and last['rsi'] < 45:
        signal = "SHORT"
        reason = "EMA20 < EMA50 и RSI < 45"

    tp1 = round(last['close'] * 1.01, 2)
    tp2 = round(last['close'] * 1.015, 2)
    tp3 = round(last['close'] * 1.02, 2)
    sl = round(last['close'] * 0.985, 2)

    message = f"""📊 BTC/USDT [{timeframe}]
Цена: {last['close']:.2f}
EMA20: {last['ema20']:.2f}, EMA50: {last['ema50']:.2f}
RSI: {last['rsi']:.2f}
Объём: {last['volume']:.2f}

Уровни:
🔻 Поддержка: {support:.2f}
🔺 Сопротивление: {resistance:.2f}

📈 Сигнал: {signal}
Причина: {reason}

🎯 TP1: {tp1}
🎯 TP2: {tp2}
🎯 TP3: {tp3}
🛑 SL: {sl}
"""
    return message

if __name__ == "__main__":
    print(generate_btc_signal())
