import yfinance as yf
import pandas as pd
import time

# 只保留100%稳定可获取数据的标的
stock_list = [
    # A股
    "600000.SS", "600036.SS", "601318.SS", "600519.SS",
    "000858.SZ", "000001.SZ", "002594.SZ", "300750.SZ",
    # 美股
    "AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "NVDA", "META", "NFLX"
]

def get_stock_data(ticker):
    try:
        time.sleep(0.2)
        # 强制使用单线程、无调整下载，避免数据格式异常
        df = yf.download(
            ticker,
            period="10d",
            interval="1d",
            progress=False,
            auto_adjust=False,
            threads=False
        )
        df = df.dropna()

        if len(df) < 3:
            return None

        # 关键：用 .iloc[0,0] 强制取标量，避免Series嵌套
        close_price = float(df["Close"].iloc[-1, 0])
        prev_close_price = float(df["Close"].iloc[-2, 0])

        # 手动计算涨跌幅
        pct = ((close_price - prev_close_price) / prev_close_price) * 100

        # 手动计算连涨天数
        up_days = 0
        for i in range(len(df)-1, 0, -1):
            curr_close = float(df["Close"].iloc[i, 0])
            prev_close = float(df["Close"].iloc[i-1, 0])
            if curr_close > prev_close:
                up_days += 1
            else:
                break

        return {
            "code": ticker,
            "close": round(close_price, 2),
            "pct": round(pct, 2),
            "up_days": up_days
        }
    except Exception as e:
        print(f"获取 {ticker} 失败: {str(e)[:100]}")
        return None

def run_scan():
    result = []
    for code in stock_list:
        data = get_stock_data(code)
        if data:
            result.append(data)

    if not result:
        print("❌ 未获取到任何有效数据，退出")
        return

    df = pd.DataFrame(result)
    df = df.sort_values(by="pct", ascending=False)
    df.to_csv("stock_result.csv", index=False, encoding="utf-8-sig")
    print("✅ 扫描完成！数据已保存到 stock_result.csv")
    print("📊 有效标的数量：", len(df))

if __name__ == "__main__":
    run_scan()
