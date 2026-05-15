import yfinance as yf
import pandas as pd
import akshare as ak
import time

# ---------------------- 1. 获取全市场代码 ----------------------
def get_all_stocks():
    codes = []

    # -------- A股（沪深主板+创业板+科创板）----------
    try:
        a_df = ak.stock_zh_a_spot_em()
        a_codes = a_df["代码"].astype(str).tolist()
        # 补后缀
        for c in a_codes:
            if c.startswith(("60","688")):
                codes.append(c + ".SS")
            elif c.startswith(("00","30")):
                codes.append(c + ".SZ")
        print(f"✅ A股: {len(a_codes)}")
    except Exception as e:
        print("❌ A股获取失败", e)

    # -------- 港股（0开头5位）----------
    hk_codes = [f"{i:05d}.HK" for i in range(1, 10000) if i % 1000 == 0]
    codes.extend(hk_codes)
    print(f"✅ 港股（抽样）: {len(hk_codes)}")

    # -------- 美股（用yfinance lookup）----------
    try:
        us_stocks = yf.Search("NASDAQ", count=2000).quotes
        us_stocks2 = yf.Search("NYSE", count=2000).quotes
        us_codes = [s["symbol"] for s in us_stocks + us_stocks2]
        codes.extend(us_codes)
        print(f"✅ 美股: {len(us_codes)}")
    except Exception as e:
        print("❌ 美股获取失败", e)

    # 去重
    codes = list(set(codes))
    print(f"📊 全市场总数: {len(codes)}")
    return codes

# ---------------------- 2. 单只股票数据 ----------------------
def get_stock_data(ticker):
    try:
        df = yf.download(ticker, period="10d", interval="1d", progress=False)
        df = df.dropna()
        if len(df) < 3:
            return None

        close = df["Close"].astype(float)
        pct = close.pct_change() * 100
        is_up = pct > 0

        # 连涨天数
        up_days = 0
        for v in is_up.iloc[::-1]:
            if v:
                up_days += 1
            else:
                break

        return {
            "code": ticker,
            "close": round(close.iloc[-1], 2),
            "pct": round(pct.iloc[-1], 2),
            "up_days": up_days
        }
    except:
        return None

# ---------------------- 3. 全盘扫描 ----------------------
def run():
    all_codes = get_all_stocks()
    result = []

    for idx, code in enumerate(all_codes):
        data = get_stock_data(code)
        if data:
            result.append(data)
        # 防风控
        if idx % 500 == 0:
            print(f"进度: {idx}/{len(all_codes)}")
            time.sleep(5)

    df = pd.DataFrame(result)
    # 排序：涨幅从高到低
    df = df.sort_values("pct", ascending=False).reset_index(drop=True)
    df.to_csv("stock_result.csv", index=False, encoding="utf-8-sig")
    print(f"🎉 完成！共有效股票: {len(df)}")
    print("🔥 当日涨幅前10：")
    print(df.head(10))

if __name__ == "__main__":
    run()
