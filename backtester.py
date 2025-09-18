"""回测模块，封装Backtrader回测流程。"""
from __future__ import annotations

import logging
from typing import Optional

import backtrader as bt
import pandas as pd

from data_fetcher import fetch_data
from strategy import MAStrategy

logger = logging.getLogger(__name__)


def _build_data_feed(data_df: pd.DataFrame) -> bt.feeds.PandasData:
    """将DataFrame转换为Backtrader数据源。"""
    data_feed = bt.feeds.PandasData(dataname=data_df)
    return data_feed


def run_backtest(
    symbol: str,
    start_date: str,
    end_date: str,
    cash: float = 100_000.0,
    commission: float = 0.001,
    short_window: int = 20,
    long_window: int = 50,
) -> Optional[float]:
    """运行双均线策略回测。

    返回最终资产价值，若失败返回None。
    """
    data_df = fetch_data(symbol, start_date, end_date)
    if data_df is None or data_df.empty:
        logger.error("run_backtest: 无法获取历史数据，终止回测")
        return None

    cerebro = bt.Cerebro()
    cerebro.adddata(_build_data_feed(data_df))
    cerebro.addstrategy(MAStrategy, short_window=short_window, long_window=long_window)
    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission=commission)

    logger.info(
        "开始回测 %s，资金 %.2f，短均线 %d，长均线 %d",
        symbol,
        cash,
        short_window,
        long_window,
    )
    cerebro.run()
    final_value = cerebro.broker.getvalue()
    logger.info("回测完成，最终资金 %.2f", final_value)
    print(f"Backtest Results - Final Portfolio Value: {final_value:.2f}")
    return final_value


__all__ = ["run_backtest"]
