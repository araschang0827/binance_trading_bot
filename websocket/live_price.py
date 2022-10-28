import websocket
import datetime
import pandas as pd
import json

########## GETTING DATA FROM WEB SOCKET AND ADDING INDICATORS ##########

df = pd.DataFrame(columns=['date', 'symbol', 'high', 'low', 'close'])


def on_message(ws, message):
    global df
    print()
    print(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": "))
    json_result = json.loads(message)
    end = {'date': str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 'symbol': json_result['k']['s'],
           'high': float(json_result['k']['h']), 'low': float(json_result['k']['l']),
           'close': float(json_result['k']['c'])}
    end_df = pd.DataFrame(end, index=[0])
    df = pd.concat([df, end_df], ignore_index=True)
    if len(df.index) > 100:
        df.drop(index=0, inplace=True)
        df.reset_index(drop=True, inplace=True)
    df.to_csv('/Users/araschang/Desktop/coding/QUANT/BinanceBot/btc_live_price.csv')
    print(df)


def on_error(ws, error):
    print(error)


def on_close(close_msg):
    print("### closed ###" + close_msg)


def streamKline(currency, interval):
    websocket.enableTrace(False)
    socket = f'wss://stream.binancefuture.com/ws/{currency}@kline_{interval}'
    ws = websocket.WebSocketApp(socket,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()


streamKline('btcusdt', '1h')
