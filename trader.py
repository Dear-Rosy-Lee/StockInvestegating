"""交易执行模块，提供模拟交易账户。"""
from __future__ import annotations

import logging

from database import record_trade

logger = logging.getLogger(__name__)


class Trader:
    """简单的单标的模拟交易账户。"""

    def __init__(self) -> None:
        self.position = 0

    def buy(self, symbol: str, price: float, quantity: int = 100) -> bool:
        """模拟买入指定数量。"""
        if self.position > 0:
            logger.warning("buy: 已有持仓，忽略重复买入")
            return False
        self.position += quantity
        logger.info("买入 %s 数量 %d，价格 %.2f", symbol, quantity, price)
        record_trade(symbol, "BUY", price, quantity)
        return True

    def sell(self, symbol: str, price: float, quantity: int = 100) -> bool:
        """模拟卖出指定数量，默认全部卖出。"""
        if self.position <= 0:
            logger.warning("sell: 当前为空仓，无法卖出")
            return False
        sell_qty = min(quantity, self.position)
        self.position -= sell_qty
        logger.info("卖出 %s 数量 %d，价格 %.2f", symbol, sell_qty, price)
        record_trade(symbol, "SELL", price, sell_qty)
        return True

    def current_position(self) -> int:
        """返回当前持仓数量。"""
        return self.position


__all__ = ["Trader"]
