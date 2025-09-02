import pandas as pd
import yfinance as yf
import pandas_ta as ta

import requests
from bs4 import BeautifulSoup
import pandas as pd


us_etf_url = "https://tw.tradingview.com/markets/etfs/funds-usa/"
# 發送 HTTP 請求獲取網站內容
response = requests.get(us_etf_url)
response.encoding = 'utf-8'  # 確保中文編碼正確

    # 解析 HTML
soup = BeautifulSoup(response.text, 'html.parser')

etf_codes = []
    # 解析表格數據
rows = soup.select("table tbody tr")
for row in rows:
    code_tag = row.select_one('a[href^="/symbols/"]')
    name_tag = row.select_one("sup")
        
    if code_tag and name_tag:
        code = code_tag.get_text(strip=True)
        name = name_tag.get_text(strip=True)
        region = "US"  # 手動補上國別
        currency = "USD"  # 手動補上幣別
        etf_codes.append((code, name, region, currency))

    # 將資料放入 DataFrame
etf_list_df = pd.DataFrame(etf_codes, columns=["etf_id", "etf_name", "region", "currency"])
         
start_date = '2015-05-01'
end_date = pd.Timestamp.today().strftime('%Y-%m-%d')

failed_tickers = []

for r in etf_codes:
    print(f"正在下載：{r}")
    try:
        df = yf.download(r, start=start_date, end=end_date, auto_adjust=False)
        df = df[df["Volume"] > 0].ffill()
        if df.empty:
            raise ValueError("下載結果為空")
            
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.droplevel(1)
            df.columns.name = None

            df.reset_index(inplace=True)
            df.rename(columns={
                "Date": "date",
                "Adj Close": "adj_close",
                "Close": "close",
                "High": "high",
                "Low": "low",
                "Open": "open",
                "Volume": "volume"
            }, inplace=True)

        
            # RSI (14) (相對強弱指標)
            df["rsi"] = ta.rsi(df["close"], length=14)

            # MA5、MA20（移動平均線）（也可以使用 df['close'].rolling(5).mean())）
            df["ma5"] = ta.sma(df["close"], length=5)
            df["ma20"] = ta.sma(df["close"], length=20)

            # MACD（移動平均收斂背離指標）
            macd = ta.macd(df["close"], fast=12, slow=26, signal=9)
            df["macd_line"] = macd["MACD_12_26_9"]
            df["macd_signal"] = macd["MACDs_12_26_9"]
            df["macd_hist"] = macd["MACDh_12_26_9"]

            # KD 指標（STOCH: 隨機震盪指標）
            stoch = ta.stoch(df["high"], df["low"], df["close"], k=14, d=3, smooth_k=3)
            df["pct_k"] = stoch["STOCHk_14_3_3"]
            df["pct_d"] = stoch["STOCHd_14_3_3"]

            # 增加該日報酬率與累積報酬指數
            df['daily_return'] = df['adj_close'].pct_change()
            df['cumulative_return'] = (1 + df['daily_return']).cumprod()
            df.insert(0, "etf_id", r)  # 新增一欄「etf_id」
            print (df)
            #df.columns = ["etf_id","date", "dividend_per_unit"]    # 調整欄位名稱
            columns_order = ['etf_id', 'date', 'adj_close','close','high', 'low', 'open','volume',
                            'rsi', 'ma5', 'ma20', 'macd_line', 'macd_signal', 'macd_hist',
                            'pct_k', 'pct_d', 'daily_return', 'cumulative_return']
            etf_daily_price_df = df[columns_order]
    except Exception as e:
        failed_tickers.append(r)
