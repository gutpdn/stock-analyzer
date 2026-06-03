# data.py — ดึงข้อมูลราคาและข้อมูลพื้นฐานจาก Yahoo Finance

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
    """ดึง metadata และ ratios พื้นฐานจาก Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info if isinstance(info, dict) else {}
    except Exception:
        return {}
