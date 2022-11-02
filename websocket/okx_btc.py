import websocket
import datetime
import pandas as pd
import json

def on_error(wsapp, error):
    print(error)

def on_message(wsapp, message):
    try:
        json_result = json.loads(message)
        result = json_result['data'][0]
        for i in range(len(result)):
            result[i] = float(result[i])
        result[0] = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        result.pop(-1)
        df = pd.Series(result, index=['time', 'open', 'high', 'low', 'close', 'volume'])
        df.to_csv('/Users/araschang/Desktop/coding/binance_trading_bot/websocket/okx_btc.csv')
        print(df)
    except Exception as e:
        print(e)

def on_close(close_msg):
    print("### closed ###" + close_msg)

def on_open(wsapp):
    wsapp.send(json.dumps({
        "op": "subscribe",
        "args": [{
            "channel": "candle1M",
            "instId": "BTC-USDT-SWAP",
        }]
    }))

def on_pong(wsapp, message):
    print("Got a pong! No need to respond")

def get_price():
    socket = 'wss://ws.okx.com:8443/ws/v5/public'
    wsapp = websocket.WebSocketApp(socket,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                on_open=on_open,
                                on_pong=on_pong)
    wsapp.run_forever(ping_interval=25, ping_timeout=10)

get_price()
