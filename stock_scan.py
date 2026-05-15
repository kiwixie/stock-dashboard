import yfinance as yf
import pandas as pd

# 股票池（可自行添加）
stock_list = [
    "AAPL", "MSFT", "TSLA", "GOOGL", "AMZN",
    "0700.HK", "9988.HK",
    "600519.SS", "000858.SZ", "300750.SZ"
]

def get_data(ticker):
    try:
        df = yf.download(ticker, period="10d", interval="1d")
        df["pct"] = df["Close"].pct_change() * 100
        df["is_up"] = df["pct"] > 0

        # 连涨天数统计
        up_days = 0
        for v in df["is_up"].iloc[::-1]:
            if v:
                up_days += 1
            else:
                break

        return {
            "code": ticker,
            "close": round(df["Close"].iloc[-1], 2),
            "pct": round(df["pct"].iloc[-1], 2),
            "up_days": up_days
        }
    except Exception as e:
        print(f"获取 {ticker} 失败: {e}")
        return None

def run():
    data = []
    for t in stock_list:
        res = get_data(t)
        if res:
            data.append(res)
    df = pd.DataFrame(data)
    # 关键：文件直接保存在当前目录
    df.to_csv("stock_result.csv", index=False, encoding="utf-8-sig")
    print("✅ 完成：涨幅榜 + 连涨筛选")

if __name__ == "__main__":
    run()
