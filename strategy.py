"""策略模块，定义双均线策略类。"""
from __future__ import annotations

import backtrader as bt


class MAStrategy(bt.Strategy):
    """双均线交叉策略。

    当短期均线上穿长期均线时买入，当短期均线下穿长期均线时卖出。
    """

    params = ("short_window", 20), ("long_window", 50)

    def __init__(self) -> None:
        # 初始化短期与长期移动平均线指标
        self.ma_short = bt.indicators.SimpleMovingAverage(self.data.close, period=self.p.short_window)
        self.ma_long = bt.indicators.SimpleMovingAverage(self.data.close, period=self.p.long_window)

    def next(self) -> None:
        """每个新bar到来时执行交易逻辑。"""
        if len(self.ma_short) < 2 or len(self.ma_long) < 2:
            # 尚未形成足够长的历史均线
            return

        prev_short = self.ma_short[-1]
        prev_long = self.ma_long[-1]
        latest_short = self.ma_short[0]
        latest_long = self.ma_long[0]

        # 金叉触发买入
        if prev_short <= prev_long and latest_short > latest_long:
            if not self.position:
                self.buy()
        # 死叉触发卖出
        elif prev_short >= prev_long and latest_short < latest_long:
            if self.position:
                self.sell()


__all__ = ["MAStrategy"]
