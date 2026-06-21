from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import akshare as ak
from datetime import date, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

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

def fetch_one(code: str, start: str, end: str, days: int):
    try:
        df = ak.stock_zh_a_hist(
            symbol=code,
            period="daily",
            start_date=start,
            end_date=end,
            adjust=""
        )
        rows = df.tail(days)[["日期", "成交量", "涨跌幅"]].to_dict("records")
        return code, [
            {
                "date": str(r["日期"])[:10],
                "volume": int(r["成交量"]),
                "pct": float(r["涨跌幅"])
            }
            for r in rows
        ], None
    except Exception as e:
        return code, None, str(e)

@app.get("/hist")
def hist(codes: str, days: int = 7):
    end = date.today().strftime("%Y%m%d")
    start = (date.today() - timedelta(days=days + 5)).strftime("%Y%m%d")

    code_list = [c.strip() for c in codes.split(",") if c.strip()]
    data = {}
    errors = {}

    # 并发查询，最多8线程
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch_one, code, start, end, days): code for code in code_list}
        for future in as_completed(futures):
            code, result, error = future.result()
            if error:
                errors[code] = error
            else:
                data[code] = result

    return {"ok": True, "data": data, "errors": errors}
