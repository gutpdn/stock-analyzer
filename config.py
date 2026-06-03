# config.py — ปรับเกณฑ์การให้คะแนนได้ที่นี่

# รายชื่อหุ้นใน watchlist เริ่มต้น — 80 บริษัทใหญ่สุดของ S&P 500 (เรียงตาม market cap)
# หมายเหตุ: ticker ที่มีจุด เช่น BRK.B ใช้ขีดกลาง (BRK-B) ตามรูปแบบของ yfinance
WATCHLIST = [
    "NVDA", "MSFT", "AAPL", "AMZN", "GOOGL", "META", "AVGO", "TSLA",
    "BRK-B", "JPM", "WMT", "LLY", "V", "ORCL", "MA", "NFLX",
    "XOM", "COST", "JNJ", "HD", "PG", "ABBV", "BAC", "PLTR",
    "KO", "UNH", "PM", "CSCO", "CRM", "WFC", "IBM", "GE",
    "CVX", "ABT", "MCD", "LIN", "NOW", "AXP", "MRK", "T",
    "ISRG", "ACN", "PEP", "GS", "MS", "TMO", "INTU", "DIS",
    "AMD", "TXN", "QCOM", "BKNG", "ADBE", "CAT", "RTX", "VZ",
    "SPGI", "BSX", "AMGN", "PGR", "BA", "UNP", "NEE", "DHR",
    "HON", "C", "GILD", "SCHW", "LOW", "PFE", "SYK", "COF",
    "ETN", "TJX", "BLK", "CMCSA", "ADP", "DE", "AMAT", "MMC",
]

# ---- เกณฑ์ Growth Score (0-10) ----
# Revenue growth YoY (%)
REVENUE_GROWTH_EXCELLENT = 25   # >= นี้ได้คะแนนเต็ม
REVENUE_GROWTH_GOOD = 10        # >= นี้ได้คะแนนกลาง

# EPS growth YoY (%)
EPS_GROWTH_EXCELLENT = 20
EPS_GROWTH_GOOD = 5

# ---- เกณฑ์ Technical Score (0-10) ----
# ราคาเทียบ MA: คะแนนแบ่งจากตำแหน่งราคา
# MACD: signal crossover ให้ bonus

# ---- เกณฑ์ Valuation Score (0-10) ----
# PEG ratio (ต่ำกว่าดีกว่า)
PEG_EXCELLENT = 1.0   # <= นี้ได้คะแนนเต็ม
PEG_GOOD = 1.5        # <= นี้ได้คะแนนกลาง
PEG_FAIR = 2.5        # <= นี้ได้คะแนนต่ำ (เกิน = 0)

# ---- น้ำหนักคะแนนรวม ----
# ผลรวมต้องเท่ากับ 1.0
WEIGHT_GROWTH = 0.4
WEIGHT_TECHNICAL = 0.3
WEIGHT_VALUATION = 0.3

# ---- Cache settings ----
# ดึงข้อมูลใหม่ทุกกี่วินาที (3600 = 1 ชั่วโมง)
CACHE_TTL = 3600
