def detect_smart_money(df):
    last = df.iloc[-1]
    wick_top = last['high'] - max(last['close'], last['open'])
    wick_bottom = min(last['close'], last['open']) - last['low']

    if wick_bottom > wick_top * 2:
        return "long"
    elif wick_top > wick_bottom * 2:
        return "short"
    return "neutral"
