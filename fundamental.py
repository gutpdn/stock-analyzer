# fundamental.py — คำนวณ ratios พื้นฐานจากงบการเงิน

from __future__ import annotations
from typing import Optional
import numpy as np
from data import get_info, get_financials


def safe_pct(new, old) -> Optional[float]:
    """คำนวณ % growth ป้องกัน ZeroDivision และค่า None"""
    try:
        if old and old != 0:
            return (new - old) / abs(old) * 100
    except Exception:
        pass
    return None


def get_fundamentals(ticker: str) -> dict:
    """
    รวม ratios ที่ต้องการทั้งหมดไว้ใน dict เดียว
    ถ้าข้อมูลไม่มี จะ return None สำหรับ key นั้น ๆ
    """
    info = get_info(ticker)
    income, _ = get_financials(ticker)

    result = {}

    # ---- Revenue growth YoY ----
    try:
        rev = income.loc["Total Revenue"]
        # คอลัมน์เรียงจากล่าสุด → เก่าสุด
        result["revenue_growth"] = safe_pct(rev.iloc[0], rev.iloc[1])
    except Exception:
        result["revenue_growth"] = None

    # ---- EPS growth YoY (จาก info เพราะ Yahoo ให้ trailing/forward EPS) ----
    try:
        eps_ttm = info.get("trailingEps")
        # Yahoo ไม่มี prior-year EPS โดยตรง — ใช้ earningsGrowth แทน
        eps_growth = info.get("earningsGrowth")
        result["eps_growth"] = eps_growth * 100 if eps_growth is not None else None
    except Exception:
        result["eps_growth"] = None

    # ---- Margins ----
    result["gross_margin"] = _pct_from_info(info, "grossMargins")
    result["operating_margin"] = _pct_from_info(info, "operatingMargins")
    result["net_margin"] = _pct_from_info(info, "profitMargins")

    # ---- ROE ----
    result["roe"] = _pct_from_info(info, "returnOnEquity")

    # ---- PEG ----
    result["peg"] = info.get("pegRatio")

    # ---- ข้อมูลทั่วไป ----
    result["name"] = info.get("longName", ticker)
    result["sector"] = info.get("sector", "N/A")
    result["market_cap"] = info.get("marketCap")
    result["pe_trailing"] = info.get("trailingPE")
    result["price"] = info.get("currentPrice") or info.get("regularMarketPrice")

    return result


def _pct_from_info(info: dict, key: str) -> Optional[float]:
    """Yahoo เก็บ ratio เป็น decimal (0.25) → แปลงเป็น % (25.0)"""
    val = info.get(key)
    if val is not None:
        return round(val * 100, 2)
    return None
