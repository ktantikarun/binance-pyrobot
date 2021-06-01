#from config import *
from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.enums import *
from twisted.internet import reactor
from config import *
import pandas as pd
import numpy as np
import talib

closes = np.array([])
rsi = []
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30


def on_tick_message_received(msg):
    '''
    A callback function to handle incoming WebSocket update 
        'E' = timestamp
        's' = symbol
        'p' = price change
        'P' = price change pct
        'c' = Last
        'b' = Bid
        'a' = Ask
        'o' = Open
        'h' = High
        'l' = Low

    '''
    if msg['e'] != 'error':
        symbol = msg['s']
        last = msg['h']
        timestamp = pd.to_datetime(msg['E'])
        print(f'{symbol}: traded at {last} at time {timestamp}')
    else:
        print('something wrong')

def on_update(msg):
    global closes
    '''
    A callback function to handle incoming WebSocket update 
            "e": "kline",                                   # event type
            "E": 1499404907056,                             # event time
            "s": "ETHBTC",                                  # symbol
            "k": {
                "t": 1499404860000,                 # start time of this bar
                "T": 1499404919999,                 # end time of this bar
                "s": "ETHBTC",                              # symbol
                "i": "1m",                                  # interval
                "f": 77462,                                 # first trade id
                "L": 77465,                                 # last trade id
                "o": "0.10278577",                  # open
                "c": "0.10278645",                  # close
                "h": "0.10278712",                  # high
                "l": "0.10278518",                  # low
                "v": "17.47929838",                 # volume
                "n": 4,                                             # number of trades
                "x": false,                                 # whether this bar is final
                "q": "1.79662878",                  # quote volume
                "V": "2.34879839",                  # volume of active buy
                "Q": "0.24142166",                  # quote volume of active buy
                "B": "13279784.01349473"    # can be ignored
                }
        }

    '''
    if msg['e'] != 'error':

        symbol = msg['s']
        candle = msg['k']

        openn = candle['o']
        high = candle['h']
        low = candle['l']
        close = candle['c']
        start_time = pd.to_datetime(candle['t'], unit='ms')
        end_time = pd.to_datetime(candle['T'], unit='ms')
        timestamp = pd.to_datetime(msg['E'], unit='ms')
        is_final_tick = candle['x']

        if is_final_tick:
            closes = np.append(closes, float(close))
            rsi = talib.RSI(closes, RSI_PERIOD)
            print(rsi)
            last_rsi = rsi[-1]
            print(f'Current RSI is {last_rsi}')

            print(f'{symbol}: O: {openn}, H: {high}, L: {low}, C: {close} at time {timestamp} / start {start_time}, end {end_time}')
        # else:
            #print(f'{symbol}: O: {openn}, H: {high}, L: {low}, C: {close} at time {timestamp} / start {start_time}, end {end_time}')
    else:
        print('something wrong')

def main():
    # Initalise our client and pass through the API key and secret
    client = Client(API_KEY, API_SECRET)

    bsm = BinanceSocketManager(client)
   # conn_key = bsm.start_symbol_ticker_socket('XRPUSDT', on_message_received)
    conn_key = bsm.start_kline_socket('XRPUSDT', on_update, interval=KLINE_INTERVAL_1MINUTE)
    bsm.start()

    # bsm.stop()
    # reactor.stop()

if __name__ == '__main__':
    main()