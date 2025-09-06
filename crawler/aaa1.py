import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

crawler_url = "https://tw.tradingview.com/markets/etfs/funds-usa/"
    # 發送 HTTP 請求獲取網站內容
response = requests.get(crawler_url)
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
  
        try:
            etf = yf.Ticker(code)
            info = etf.info
            expense_ratio = info.get("netExpenseRatio", None)
            inception_ts = info.get("fundInceptionDate", None)
            inception_date = (
            datetime.fromtimestamp(inception_ts).strftime("%Y-%m-%d") if inception_ts else None
                    )
        except Exception as e:
                    print(f"查詢 {code} 時發生錯誤: {e}")
                    expense_ratio = None
                    inception_date = None

        etf_codes.append((code, name, region, currency, expense_ratio, inception_date))

# 將資料放入 DataFrame
etf_list_df = pd.DataFrame(etf_codes, columns=["etf_id", "etf_name", "region", "currency",
                                               "expense_ratio","inception_date"])
print(etf_list_df)
etf_list = etf_list_df.to_dict(orient="records") 
print(etf_list)
tickers = [etf["etf_id"] for etf in etf_list]

#print(tickers)
