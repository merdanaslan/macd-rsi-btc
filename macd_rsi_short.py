import backtrader as bt
import pandas as pd


class MACDCrossoverStrategy(bt.Strategy):
    params = (
        ("fast_period", 12),
        ("slow_period", 26),
        ("signal_period", 9),
    )

    def __init__(self):
        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.p.fast_period,
            period_me2=self.p.slow_period,
            period_signal=self.p.signal_period
        )

        self.rsi = bt.indicators.RSI_SMA(self.data.close, period=14)  # Using RSI with a 14-period lookback

        self.last_signal = None  # To keep track of the last signal (buy/sell)
        self.buy_allowed = True  # To allow buy signals after a sell

    def next(self):
        if self.macd.macd[0] > self.macd.signal[0] and self.macd.macd[-1] <= self.macd.signal[-1] and self.rsi[0] <= 30:
            if self.last_signal != 'buy' and self.buy_allowed:
                self.buy()
                self.last_signal = 'buy'
                self.buy_allowed = False

        elif self.macd.macd[0] < self.macd.signal[0] and self.macd.macd[-1] >= self.macd.signal[-1] and self.rsi[0] >= 70:
            if self.last_signal == 'buy':
                self.sell()
                self.last_signal = 'sell'
                self.buy_allowed = True


data = pd.read_csv('btc_4h_data_jan_to_aug.csv', parse_dates=True, index_col='timestamp')
data_feed = bt.feeds.PandasData(dataname=data)

cerebro = bt.Cerebro()
cerebro.adddata(data_feed)
cerebro.addstrategy(MACDCrossoverStrategy)

cerebro.broker.set_cash(10000)
cerebro.broker.setcommission(commission=0.001)

print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

cerebro.run()

print('Ending Portfolio Value: %.2f' % cerebro.broker.getvalue())
cerebro.plot()
