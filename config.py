# config.py — ปรับเกณฑ์การให้คะแนนได้ที่นี่

# รายชื่อหุ้นใน watchlist เริ่มต้น — 80 ตัวแรกของ S&P 500 (เรียงตามตัวอักษร)
# หมายเหตุ: ticker ที่มีจุด เช่น BRK.B / BF.B ใช้ขีดกลางตามรูปแบบของ yfinance
WATCHLIST = [
    "A", "AAPL", "ABBV", "ABNB", "ABT", "ACGL", "ACN", "ADBE",
    "ADI", "ADM", "ADP", "ADSK", "AEE", "AEP", "AES", "AFL",
    "AIG", "AIZ", "AJG", "AKAM", "ALB", "ALGN", "ALL", "ALLE",
    "AMAT", "AMCR", "AMD", "AME", "AMGN", "AMP", "AMT", "AMZN",
    "ANET", "ANSS", "AON", "AOS", "APA", "APD", "APH", "APTV",
    "ARE", "ATO", "AVB", "AVGO", "AVY", "AWK", "AXON", "AXP",
    "AZO", "BA", "BAC", "BALL", "BAX", "BBY", "BDX", "BEN",
    "BF-B", "BG", "BIIB", "BK", "BKNG", "BKR", "BLDR", "BLK",
    "BMY", "BR", "BRK-B", "BRO", "BSX", "BWA", "BX", "BXP",
    "C", "CAG", "CAH", "CARR", "CAT", "CB", "CBOE", "CBRE",
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
