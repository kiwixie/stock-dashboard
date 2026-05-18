import yfinance as yf
import pandas as pd
import akshare as ak
import time

# ==========================================
# 【全自动】获取 全部 A 股 股票代码（5000+）
# ==========================================
def get_all_a_share():
    print("正在获取全量A股列表...")
    df = ak.stock_zh_a_spot_em()
    codes = []

    for code in df["代码"].astype(str).str.zfill(6):
        if code.startswith(("60", "68")):
            codes.append(f"{code}.SS")
        elif code.startswith(("00", "30")):
            codes.append(f"{code}.SZ")

    print(f"✅ 全A股总量：{len(codes)} 只")
    return codes

# ==========================================
# 获取单只股票数据 + 连涨天数
# ==========================================
def get_one_stock(ticker):
    try:
        time.sleep(0.15)  # 防风控
        df = yf.download(ticker, period="20d", interval="1d", progress=False)

        if len(df) < 5:
            return None

        # 取出收盘价列表
        closes = df["Close"].dropna().tolist()
        if len(closes) < 2:
            return None

        # 今日涨幅
        today = closes[-1]
        yesterday = closes[-2]
        pct = ((today - yesterday) / yesterday) * 100

        # 连续上涨天数（从最新往历史数）
        up_days = 0
        for i in range(len(closes)-1, 0, -1):
            if closes[i] > closes[i-1]:
                up_days += 1
            else:
                break

        return {
            "code": ticker,
            "close": round(today, 2),
            "pct": round(pct, 2),
            "up_days": up_days
        }

    except:
        return None

# ==========================================
# 全市场扫描主程序
# ==========================================
def run():
    all_codes = get_all_a_share()
    result = []

    print("开始全市场扫描...")

    for idx, code in enumerate(all_codes):
        data = get_one_stock(code)
        if data:
            result.append(data)

        # 打印进度
        if idx % 200 == 0:
            print(f"进度：{idx}/{len(all_codes)}  有效数据：{len(result)}")

    # 没有数据直接退出
    if not result:
        print("❌ 未获取到数据")
        return

    # 生成表格
    df = pd.DataFrame(result)
    df = df.sort_values("pct", ascending=False)
    df.to_csv("stock_result.csv", index=False, encoding="utf-8-sig")

    print("✅ 全市场扫描完成！")
    print(f"📊 有效股票：{len(df)} 只")
    print("\n🔥 涨幅前10：")
    print(df.head(10)[["code", "pct", "up_days"]])

    print("\n📈 连涨 3 天以上股票：")
    up3 = df[df["up_days"] >= 3]
    print(up3[["code", "pct", "up_days"]])

if __name__ == "__main__":
    run()
