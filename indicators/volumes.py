def analyze_volume(df):
    avg_volume = df['volume'].rolling(20).mean()
    if df['volume'].iloc[-1] > 1.5 * avg_volume.iloc[-1]:
        if df['close'].iloc[-1] > df['open'].iloc[-1]:
            return "buy"
        else:
            return "sell"
    return "neutral"
