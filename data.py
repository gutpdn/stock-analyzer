# data.py — ดึงข้อมูลราคาและข้อมูลพื้นฐานจาก Yahoo Finance

import time
import yfinance as yf
import streamlit as st
from config import CACHE_TTL


@st.cache_data(ttl=CACHE_TTL)
def get_price_history(ticker: str, period: str = "1y") -> "pd.DataFrame":
    """ดึงข้อมูลราคาย้อนหลัง (OHLCV) — ใช้สำหรับคำนวณ indicator เทคนิคอล"""
    df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
    return df


@st.cache_data(ttl=CACHE_TTL)
def get_info(ticker: str) -> dict:
    """
    ดึง metadata และ ratios พื้นฐานจาก Yahoo Finance

    บางครั้ง Yahoo คืนข้อมูลไม่ครบ (skeleton ~13 keys ไม่มี marketCap/PE/PEG)
    เพราะโดน rate-limit ชั่วคราว เราจึง:
      1) ลองซ้ำได้สูงสุด 3 ครั้ง
      2) ถ้ายังไม่ครบ จะ raise เพื่อ "ไม่ให้ cache ค่าเสีย"
         (ถ้า cache ค่าเสียจะค้าง N/A ยาวถึง 1 ชม. ตาม CACHE_TTL)
    ตัวที่ raise จะถูกดึงใหม่ในรอบถัดไป แทนที่จะค้าง
    """
    for attempt in range(3):
        try:
            info = yf.Ticker(ticker).info
        except Exception:
            info = {}
        # ใช้ marketCap เป็นตัวชี้ว่าข้อมูลครบ (skeleton จะไม่มี field นี้)
        if isinstance(info, dict) and info.get("marketCap") is not None:
            return info
        time.sleep(0.6 * (attempt + 1))  # backoff ก่อนลองใหม่

    raise RuntimeError(f"incomplete Yahoo data for {ticker}")
