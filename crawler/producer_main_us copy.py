from crawler.tasks_etf_list_us import etf_list_us  

if __name__ == "__main__":
    print("🚀 開始執行美股 ETF 抓取")
    etf_list_us(crawler_url="https://tw.tradingview.com/markets/etfs/funds-usa/")
    print("✅ 抓取完成")
