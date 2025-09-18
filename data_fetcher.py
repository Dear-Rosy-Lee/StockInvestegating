"""行情数据获取模块。

该模块通过yfinance库从Yahoo Finance获取历史行情数据。
"""
from __future__ import annotations

import logging
from typing import Optional

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


def fetch_data(symbol: str, start_date: str, end_date: str, interval: str = "1d") -> Optional[pd.DataFrame]:
    """从Yahoo Finance获取历史行情数据。

    参数:
        symbol: 股票或其他金融标的代码，例如"AAPL"。
        start_date: 数据开始日期，格式"YYYY-MM-DD"。
        end_date: 数据结束日期，格式"YYYY-MM-DD"。
        interval: 数据频率，默认为"1d"日线。

    返回:
        如果成功，返回按日期索引排序的pandas.DataFrame；若失败则返回None。
    """
    try:
        logger.debug(
            "fetch_data: downloading data", extra={"symbol": symbol, "start": start_date, "end": end_date}
        )
        df = yf.download(symbol, start=start_date, end=end_date, interval=interval, progress=False)
    except Exception as exc:  # pragma: no cover - 网络错误难以预测
        logger.error("获取行情数据失败: %s", exc)
        return None

    if df.empty:
        logger.warning("fetch_data: 未获取到 %s 在%s至%s的数据", symbol, start_date, end_date)
        return df

    # 将索引转为DatetimeIndex并排序，去除缺失值，确保数据质量。
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    df.dropna(how="any", inplace=True)
    return df


__all__ = ["fetch_data"]
