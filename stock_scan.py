import yfinance as yf
import pandas as pd
import time

# ----------------------
# 股票池：A股 + 港股 + 美股（稳定可获取）
# ----------------------
stock_list = [
    # A股
    "600000.SS", "600036.SS", "601318.SS",
    "000858.SZ", "000001.SZ", "002594.SZ",
    "300750.SZ", "300059.SZ",

    # 港股
    "00700.HK", "09988.HK", "09618.HK",
    "03690.HK", "01810.HK",

    # 美股
    "AAPL", "MSFT", "TSLA", "GOOGL", "AMZN",
    "NVDA", "META", "NFLX"
]

# ----------------------
# 获取单只股票数据
# ----------------------
def get_stock_data(ticker):
    try:
        time.sleep(0.1)
        df = yf.download(ticker, period="10d", interval="1d", progress=False)
        df = df.dropna()

        if len(df) < 3:
            return None

        close = df["Close"].astype(float)
        pct_change = close.pct_change() * 100
        is_up = pct_change > 0

        # 连涨天数
        up_days = 0
        for val in is_up.iloc[::-1].dropna():
            if val:
                up_days += 1
            else:
                break

        return {
            "code": ticker,
            "close": round(close.iloc[-1], 2),
            "pct": round(pct_change.iloc[-1], 2),
            "up_days": up_days
        }
    except:
        return None

# ----------------------
# 批量扫描
# ----------------------
def run_scan():
    result = []
    for code in stock_list:
        data = get_stock_data(code)
        if data:
            result.append(data)

    if not result:
        print("❌ 未获取到任何数据")
        return

    df = pd.DataFrame(result)
    df = df.sort_values("pct", ascending=False)
    df.to_csv("stock_result.csv", index=False, encoding="utf-8-sig")
    print("✅ 扫描完成！数据已保存到 stock_result.csv")

if __name__ == "__main__":
    run_scan()
