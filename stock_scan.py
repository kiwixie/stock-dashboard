import yfinance as yf
import pandas as pd
import time

# 只保留100%可获取数据的标的，彻底避免无数据导致的崩溃
stock_list = [
    # A股（沪市）
    "600000.SS", "600036.SS", "601318.SS", "600519.SS",
    # A股（深市）
    "000858.SZ", "000001.SZ", "002594.SZ", "300750.SZ",
    # 美股
    "AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "NVDA", "META", "NFLX"
]

def get_stock_data(ticker):
    try:
        # 加请求延时，避免被限流
        time.sleep(0.2)
        # 明确设置auto_adjust=False，避免数据格式异常
        df = yf.download(ticker, period="10d", interval="1d", progress=False, auto_adjust=False)
        df = df.dropna()

        # 数据不足3天，直接跳过
        if len(df) < 3:
            return None

        # 强制转成float类型，避免后续比较报错
        close = df["Close"].astype(float)
        pct_change = close.pct_change() * 100
        is_up = pct_change > 0

        # 连涨天数统计
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
    except Exception as e:
        print(f"获取 {ticker} 失败: {e}")
        return None

def run_scan():
    result = []
    for code in stock_list:
        data = get_stock_data(code)
        if data:
            result.append(data)

    # 关键：处理无数据的情况，避免后续报错
    if not result:
        print("❌ 未获取到任何有效数据，退出")
        return

    df = pd.DataFrame(result)
    # 强制将pct列转为float，避免类型不一致导致排序报错
    df["pct"] = df["pct"].astype(float)
    df = df.sort_values("pct", ascending=False)
    df.to_csv("stock_result.csv", index=False, encoding="utf-8-sig")
    print("✅ 扫描完成！数据已保存到 stock_result.csv")
    print("📊 有效标的数量：", len(df))

if __name__ == "__main__":
    run_scan()
