# technical.py — คำนวณ indicator เทคนิคอล (MA50, MA200, MACD)

import pandas as pd
from data import get_price_history


def get_technicals(ticker: str) -> dict:
    """
    คืนค่า dict ที่มี:
      - price, ma50, ma200  (ราคาและ moving averages)
      - macd, signal        (MACD line และ Signal line)
      - macd_bullish        (True ถ้า MACD > Signal = bullish crossover)
      - price_vs_ma50/200   (% ห่างจาก MA เป็น + หรือ -)
      - df_price            (DataFrame ราคาเต็มสำหรับ plot กราฟ)
    """
    df = get_price_history(ticker, period="1y")

    if df.empty or len(df) < 50:
        return _empty_result()

    close = df["Close"].squeeze()  # squeeze ป้องกัน DataFrame แทน Series

    # ---- Moving Averages ----
    ma50 = close.rolling(50).mean().iloc[-1]
    # MA200 ต้องการข้อมูลอย่างน้อย 200 วัน → ใช้ 2y ถ้าจะดู MA200 จริง ๆ
    # แต่เพื่อความง่าย คำนวณจากข้อมูลที่มีแล้ว (อาจได้ NaN ถ้าข้อมูลไม่พอ)
    ma200_series = close.rolling(200).mean()
    ma200 = ma200_series.iloc[-1] if not pd.isna(ma200_series.iloc[-1]) else None

    price = close.iloc[-1]

    # ---- MACD (12, 26, 9) ----
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()

    macd_val = macd_line.iloc[-1]
    signal_val = signal_line.iloc[-1]

    # เพิ่ม column ลงใน df สำหรับ plot
    df = df.copy()
    df["MA50"] = close.rolling(50).mean()
    df["MA200"] = close.rolling(200).mean()
    df["MACD"] = macd_line
    df["Signal"] = signal_line
    df["Histogram"] = macd_line - signal_line

    return {
        "price": round(price, 2),
        "ma50": round(ma50, 2) if not pd.isna(ma50) else None,
        "ma200": round(ma200, 2) if ma200 is not None else None,
        "macd": round(macd_val, 4),
        "signal": round(signal_val, 4),
        "macd_bullish": bool(macd_val > signal_val),
        "price_vs_ma50": _pct_vs(price, ma50),
        "price_vs_ma200": _pct_vs(price, ma200),
        "df_price": df,
    }


def _pct_vs(price, ma) -> float | None:
    """% ที่ราคาอยู่เหนือ/ใต้ MA"""
    if ma is None or pd.isna(ma) or ma == 0:
        return None
    return round((price - ma) / ma * 100, 2)


def _empty_result() -> dict:
    return {
        "price": None, "ma50": None, "ma200": None,
        "macd": None, "signal": None, "macd_bullish": None,
        "price_vs_ma50": None, "price_vs_ma200": None,
        "df_price": pd.DataFrame(),
    }
