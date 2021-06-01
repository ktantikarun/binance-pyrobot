from __future__ import (absolute_import, division, print_function, unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
from binance.client import Client
import pandas as pd
from config import *


def get_historical_kline_df(symbol, interval, start_date, end_date):
    '''
    Get raw candlesticks data returned from client and decorate into dataframe format
    # Response is in below format
    # [
    #     1499040000000,        // Open time
    #     "0.01634790",         // Open
    #     "0.80000000",         // High
    #     "0.01575800",         // Low
    #     "0.01577100",         // Close
    #     "148796.11427815"     // Volume
    #     1499644799999,        // Close time
    #     "2434.19055334"       // Quote asset volume
    #     308,                  // Number of trades
    #     "1756.87402397"       // Taker buy base asset volume
    #     "28.46694368"         // Taker buy quote asset volume
    #     "17928899.62484339"   // Ignore
    # ]
    '''
    candlesticks = client.get_historical_klines(symbol, interval, start_date, end_date)
    hist_df = pd.DataFrame(candlesticks)
    hist_df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'QuoteAssetVol', 'TradeNo', 'TakerBuyBaseAssetVol', 'TakerBuyQuoteAssetVol', 'Ignore']
    hist_df['Date'] = pd.to_datetime(hist_df['Date'], unit='ms')
    hist_df.set_index('Date', inplace=True)
    hist_df = hist_df[['Open', 'High', 'Low', 'Close', 'Volume']]
    hist_df = hist_df.apply(pd.to_numeric)

    return hist_df


# Create a Stratey
class TestStrategy(bt.Strategy):

    def log(self, message, dt=None):
        '''
        Log messages
        '''
        timestamp = dt or self.datas[0].datetime.datetime(0)
        print(f'{timestamp}: {message}')


    def __init__(self):
        '''
        Invoked at instatiation. indicators is typically created here
        '''
        #self.data = self.datas[0]
        # To keep track of pending orders
        self.order = None
        self.sma20 = bt.indicators.SMA(self.data.close, period=20)
        self.sma50 = bt.indicators.SMA(self.data.close, period=50)
        self.rsi = bt.indicators.RSI(self.data.close)
        


    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, {order.executed.price:.2f}')
            
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        
        # Write down: no pending order
        self.order = None


    def next(self):
        '''
        Iteration through each data point in the data feed
        '''
        self.log(f'Close, {self.data.close[0]:.2f}')

        if self.order:
            return
        
        self.log('')

        if not self.position:
            if self.sma20[0] > self.sma50[0] and self.sma20[-1] <= self.sma50[-1]:
                self.log(f'BUY CREATED, {self.data.close[0]:.2f}')
                self.order = self.buy()
        
        else:
            if self.sma20[0] < self.sma50[0] and self.sma20[-1] >= self.sma50[-1]:
                self.log(f'SELL CREATED, {self.data.close[0]:.2f}')
                self.order = self.sell()


if __name__ == '__main__':

    client = Client(API_KEY, API_SECRET)

    df = get_historical_kline_df("XRPUSDT", Client.KLINE_INTERVAL_1MINUTE, "23/12/2020", "25/12/2020")
    print('ok')

    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    # Create a Data Feed
    data = bt.feeds.PandasData(dataname=df)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(0.0025)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())