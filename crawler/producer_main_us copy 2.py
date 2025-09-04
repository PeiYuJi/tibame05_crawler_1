import logging
from crawler.tasks_etf_list_us import etf_list_us
from crawler.tasks_crawler_etf_us import crawler_etf_us
from crawler.tasks_backtest_utils_us import backtest_utils_us
from crawler.tasks_crawler_etf_dps_us import crawler_etf_dps_us


# 設定 logging（可依需要改為寫入檔案）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),  # 輸出到終端
        # logging.FileHandler("etf_pipeline.log"),  # 若要寫入檔案
    ]
)


if __name__ == "__main__":
    us_etf_url = "https://tw.tradingview.com/markets/etfs/funds-usa/"

    # Step 1: 抓取 ETF 清單
    try:
        logging.info("開始抓取 ETF 清單...")
        etf_list_dict = etf_list_us(crawler_url=us_etf_url)
        logging.info(f"ETF 清單抓取完成，共取得 {len(etf_list_dict)} 檔 ETF。")
    except Exception as e:
        logging.error("ETF 清單抓取失敗！", exc_info=True)
        etf_list_dict = None

    # Step 2: 抓取配息資料
    if etf_list_dict is not None:
        try:
            logging.info("開始抓取配息資料...")
            crawler_etf_dps_us(etf_list_df=etf_list_dict)
            logging.info("配息資料抓取完成。")
        except Exception as e:
            logging.error("配息資料抓取失敗！", exc_info=True)

    # Step 3: 抓取歷史價格
    if etf_list_dict is not None:
        try:
            logging.info("開始抓取歷史價格資料...")
            crawler_etf_us(etf_list_df=etf_list_dict)
            logging.info("歷史價格資料抓取完成。")
        except Exception as e:
            logging.error("歷史價格資料抓取失敗！", exc_info=True)

    # Step 4: 技術指標與績效分析
    if etf_list_dict is not None:
        try:
            logging.info("開始進行歷史價格、技術指標與績效分析...")
            backtest_utils_us(etf_list_df=etf_list_dict)
            logging.info("分析完成。")
        except Exception as e:
            logging.error("歷史價格與績效分析失敗！", exc_info=True)

    logging.info("ETF 整體流程執行完畢。")
