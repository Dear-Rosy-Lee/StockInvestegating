"""数据库模块，使用SQLite存储行情与交易记录。"""
from __future__ import annotations

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import pandas as pd

logger = logging.getLogger(__name__)

DB_FILE = Path("trading.db")

_conn = sqlite3.connect(DB_FILE, check_same_thread=False)
_cursor = _conn.cursor()


def init_db() -> None:
    """初始化数据库表结构。"""
    try:
        _cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS prices (
                symbol TEXT,
                date TEXT,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume REAL,
                PRIMARY KEY(symbol, date)
            )
            """
        )
        _cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                datetime TEXT,
                symbol TEXT,
                action TEXT,
                price REAL,
                quantity INTEGER
            )
            """
        )
        _conn.commit()
        logger.info("数据库初始化完成，文件位于 %s", DB_FILE.resolve())
    except Exception as exc:
        logger.error("数据库初始化失败: %s", exc)


def save_price_data(df: pd.DataFrame, symbol: str) -> None:
    """保存行情数据至prices表。"""
    try:
        records: List[Tuple[str, str, float, float, float, float, float]] = []
        for date, row in df.iterrows():
            date_str = date.strftime("%Y-%m-%d")
            records.append(
                (
                    symbol,
                    date_str,
                    float(row.get("Open", 0.0)),
                    float(row.get("High", 0.0)),
                    float(row.get("Low", 0.0)),
                    float(row.get("Close", 0.0)),
                    float(row.get("Volume", 0.0)),
                )
            )
        if records:
            _cursor.executemany(
                """
                INSERT OR REPLACE INTO prices(symbol, date, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                records,
            )
            _conn.commit()
    except Exception as exc:
        logger.error("保存行情数据出错: %s", exc)


def record_trade(symbol: str, action: str, price: float, quantity: int) -> None:
    """记录交易行为。"""
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        _cursor.execute(
            """
            INSERT INTO trades(datetime, symbol, action, price, quantity)
            VALUES (?, ?, ?, ?, ?)
            """,
            (now, symbol, action, float(price), int(quantity)),
        )
        _conn.commit()
    except Exception as exc:
        logger.error("记录交易失败: %s", exc)


__all__ = ["init_db", "save_price_data", "record_trade"]
