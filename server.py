from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import akshare as ak
from datetime import date, timedelta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "message": "AKShare hist service is running"}

@app.get("/hist")
def hist(codes: str, days: int = 7):
    end = date.today().strftime("%Y%m%d")
    start = (date.today() - timedelta(days=days + 5)).strftime("%Y%m%d")

    data = {}
    errors = {}

    for code in codes.split(","):
        code = code.strip()
        if not code:
            continue
        try:
            df = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start,
                end_date=end,
                adjust=""
            )
            rows = df.tail(days)[["日期", "成交量", "涨跌幅"]].to_dict("records")
            data[code] = [
                {
                    "date": str(r["日期"])[:10],
                    "volume": int(r["成交量"]),
                    "pct": float(r["涨跌幅"])
                }
                for r in rows
            ]
        except Exception as e:
            errors[code] = str(e)

    return {"ok": True, "data": data, "errors": errors}
