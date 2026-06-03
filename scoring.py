# scoring.py — ให้คะแนน 3 ด้าน (0-10) และคะแนนรวม

from config import (
    REVENUE_GROWTH_EXCELLENT, REVENUE_GROWTH_GOOD,
    EPS_GROWTH_EXCELLENT, EPS_GROWTH_GOOD,
    PEG_EXCELLENT, PEG_GOOD, PEG_FAIR,
    WEIGHT_GROWTH, WEIGHT_TECHNICAL, WEIGHT_VALUATION,
)


def score_growth(fund: dict) -> float:
    """
    Growth score 0-10
    คะแนนมาจาก revenue growth (60%) และ EPS growth (40%)
    """
    rev = fund.get("revenue_growth")
    eps = fund.get("eps_growth")

    rev_score = _score_growth_metric(rev, REVENUE_GROWTH_EXCELLENT, REVENUE_GROWTH_GOOD)
    eps_score = _score_growth_metric(eps, EPS_GROWTH_EXCELLENT, EPS_GROWTH_GOOD)

    # ถ้าขาดข้อมูลตัวใดตัวหนึ่ง ใช้ตัวที่มีเต็ม ๆ
    if rev is None and eps is None:
        return 0.0
    if rev is None:
        return eps_score
    if eps is None:
        return rev_score

    return round(rev_score * 0.6 + eps_score * 0.4, 2)


def score_technical(tech: dict) -> float:
    """
    Technical score 0-10
    - ราคา > MA50 และ MA200: +4 และ +3
    - MACD bullish: +3
    """
    score = 0.0

    vs_ma50 = tech.get("price_vs_ma50")
    vs_ma200 = tech.get("price_vs_ma200")
    macd_bullish = tech.get("macd_bullish")

    # ราคาเทียบ MA50 (max 4 คะแนน)
    if vs_ma50 is not None:
        if vs_ma50 > 5:
            score += 4
        elif vs_ma50 > 0:
            score += 2
        # ถ้า < 0 ไม่ได้คะแนน

    # ราคาเทียบ MA200 (max 3 คะแนน)
    if vs_ma200 is not None:
        if vs_ma200 > 5:
            score += 3
        elif vs_ma200 > 0:
            score += 1.5

    # MACD bullish crossover (3 คะแนน)
    if macd_bullish:
        score += 3

    return round(min(score, 10.0), 2)


def score_valuation(fund: dict) -> float:
    """
    Valuation score 0-10 จาก PEG ratio
    PEG ต่ำ = undervalued = คะแนนสูง
    """
    peg = fund.get("peg")

    if peg is None or peg <= 0:
        return 5.0  # ข้อมูลไม่พอ → ให้กลาง ๆ ไว้ก่อน

    if peg <= PEG_EXCELLENT:
        return 10.0
    elif peg <= PEG_GOOD:
        # interpolate ระหว่าง 7-10
        ratio = (peg - PEG_EXCELLENT) / (PEG_GOOD - PEG_EXCELLENT)
        return round(10 - ratio * 3, 2)
    elif peg <= PEG_FAIR:
        # interpolate ระหว่าง 3-7
        ratio = (peg - PEG_GOOD) / (PEG_FAIR - PEG_GOOD)
        return round(7 - ratio * 4, 2)
    else:
        return 0.0


def score_total(fund: dict, tech: dict) -> dict:
    """
    คืนค่า dict คะแนนทั้งหมด:
      growth, technical, valuation, total (weighted average)
    """
    g = score_growth(fund)
    t = score_technical(tech)
    v = score_valuation(fund)
    total = round(g * WEIGHT_GROWTH + t * WEIGHT_TECHNICAL + v * WEIGHT_VALUATION, 2)

    return {
        "growth": g,
        "technical": t,
        "valuation": v,
        "total": total,
    }


def _score_growth_metric(value, excellent, good) -> float:
    """Helper: แปลง % growth เป็นคะแนน 0-10"""
    if value is None:
        return 0.0
    if value >= excellent:
        return 10.0
    elif value >= good:
        # interpolate ระหว่าง 5-10
        ratio = (value - good) / (excellent - good)
        return round(5 + ratio * 5, 2)
    elif value > 0:
        return round(value / good * 5, 2)
    else:
        return 0.0
