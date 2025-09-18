def calculate_ema(df, period=50):
    df['ema_50'] = df['close'].ewm(span=period).mean()
    return df
