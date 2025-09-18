"""系统主入口，提供回测与定时交易功能。"""
from __future__ import annotations

import logging
import sys
from datetime import datetime, timedelta

import pandas as pd

from apscheduler.schedulers.blocking import BlockingScheduler

from backtester import run_backtest
from data_fetcher import fetch_data
from database import init_db, save_price_data
from trader import Trader

# 全局日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("trading.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# 默认配置，可根据需要调整
SYMBOL = "AAPL"
LOOKBACK_DAYS = 60
SHORT_WINDOW = 20
LONG_WINDOW = 50


def _calculate_signal(data: pd.DataFrame) -> int:
    """根据双均线产生交易信号。

    返回 1 表示买入，-1 表示卖出，0 表示无动作。
    """
    close_prices = data["Close"]
    if len(close_prices) < LONG_WINDOW:
        logger.warning("数据长度不足，无法计算均线")
        return 0

    ma_short = close_prices.rolling(window=SHORT_WINDOW).mean()
    ma_long = close_prices.rolling(window=LONG_WINDOW).mean()

    prev_short = ma_short.iloc[-2]
    prev_long = ma_long.iloc[-2]
    latest_short = ma_short.iloc[-1]
    latest_long = ma_long.iloc[-1]

    if any(value != value for value in (prev_short, prev_long, latest_short, latest_long)):
        # 包含缺失值时不产生信号
        return 0

    if prev_short <= prev_long and latest_short > latest_long:
        return 1
    if prev_short >= prev_long and latest_short < latest_long:
        return -1
    return 0


def run_daily_job(trader: Trader) -> None:
    """每日调度任务：获取数据、计算信号并执行交易。"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=LOOKBACK_DAYS)
        data = fetch_data(SYMBOL, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        if data is None or data.empty:
            logger.error("run_daily_job: 未能获取到行情数据")
            return
        save_price_data(data, SYMBOL)

        signal = _calculate_signal(data)
        price = float(data["Close"].iloc[-1])
        current_pos = trader.current_position()

        if signal == 1 and current_pos == 0:
            trader.buy(SYMBOL, price, quantity=100)
        elif signal == -1 and current_pos > 0:
            trader.sell(SYMBOL, price, quantity=current_pos)
        else:
            logger.info("当日无交易执行，信号=%s，持仓=%s", signal, current_pos)
    except Exception as exc:  # pragma: no cover - 调度任务中捕获所有异常
        logger.error("执行日常任务失败: %s", exc, exc_info=True)


def _run_scheduler() -> None:
    """启动APScheduler调度。"""
    trader = Trader()
    scheduler = BlockingScheduler()
    scheduler.add_job(run_daily_job, "cron", day_of_week="mon-fri", hour=9, minute=30, args=[trader])
    logger.info("启动交易调度器，目标标的 %s", SYMBOL)
    scheduler.start()


if __name__ == "__main__":
    init_db()
    if len(sys.argv) > 1 and sys.argv[1].lower() == "backtest":
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        run_backtest(SYMBOL, start_date, end_date, short_window=SHORT_WINDOW, long_window=LONG_WINDOW)
        sys.exit(0)

    _run_scheduler()
