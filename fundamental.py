# fundamental.py — คำนวณ ratios พื้นฐานจากข้อมูลของ Yahoo Finance

from __future__ import annotations
from typing import Optional
from data import get_info


def get_fundamentals(ticker: str) -> dict:
    """
    รวม ratios ที่ต้องการทั้งหมดไว้ใน dict เดียว
    ถ้าข้อมูลไม่มี จะ return None สำหรับ key นั้น ๆ
    """
    # get_info อาจ raise ถ้า Yahoo ส่งข้อมูลไม่ครบ → ถือเป็นว่างไว้ก่อน
    # (ค่าที่ได้จะเป็น N/A เฉพาะรอบนี้ และจะถูกลองใหม่รอบหน้า เพราะไม่ถูก cache)
    try:
        info = get_info(ticker)
    except Exception:
        info = {}

    result = {}

    # ---- Revenue growth YoY ----
    # Yahoo ให้ค่านี้ใน info อยู่แล้ว (decimal เช่น 0.166 = 16.6%)
    # ไม่ต้องดึงงบการเงินแยก ช่วยลด network call ต่อหุ้น
    rev_growth = info.get("revenueGrowth")
    result["revenue_growth"] = rev_growth * 100 if rev_growth is not None else None

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
    # ใช้ pegRatio เป็นหลัก ถ้าไม่มีค่อย fallback เป็น trailingPegRatio
    peg = info.get("pegRatio")
    if peg is None:
        peg = info.get("trailingPegRatio")
    result["peg"] = peg

    # ---- ข้อมูลทั่วไป ----
    result["name"] = info.get("longName", ticker)
    result["sector"] = info.get("sector", "N/A")
    result["market_cap"] = info.get("marketCap")
    result["pe_trailing"] = info.get("trailingPE")
    result["pe_forward"] = info.get("forwardPE")  # P/E จากกำไรคาดการณ์
    result["price"] = info.get("currentPrice") or info.get("regularMarketPrice")

    return result


def _pct_from_info(info: dict, key: str) -> Optional[float]:
    """Yahoo เก็บ ratio เป็น decimal (0.25) → แปลงเป็น % (25.0)"""
    val = info.get(key)
    if val is not None:
        return round(val * 100, 2)
    return None
