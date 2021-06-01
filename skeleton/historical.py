from binance.client import Client
from config import *
import pandas as pd

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
    hist_df = hist_df[['Open', 'High', 'Low', 'Close']]
    hist_df = hist_df.apply(pd.to_numeric)

    return hist_df



def main():
    global client 
    # Initalise our client and pass through the API key and secret
    client = Client(API_KEY, API_SECRET)

    df = get_historical_kline_df("BTCUSDT", Client.KLINE_INTERVAL_4HOUR, "01/01/2020", "25/12/2020")


if __name__ == '__main__':
    main()