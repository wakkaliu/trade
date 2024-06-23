import time
# import ccxt

# # 初始化 Bybit 期貨客戶端
# bybit = ccxt.bybit({
#     'apiKey': '',
#     'secret': '',
# })

# 設定交易對和數量
# symbol_agix = 'AGIX/USDT:USDT'  # AGIXUSDU21 是 AGIX 的期貨合約
# symbol_fet = 'FET/USDT:USDT'    # FETUSDU21 是 FET 的期貨合約
# symbol_usdc = 'USDC/USDT:USDT'    # FETUSDU21 是 FET 的期貨合約
symbol_btc = 'BTC/USDT:USDT' 
symbol_sol = 'SOL/USDT:USDT' 
symbol_bnb = 'BNB/USDT:USDT' 
symbol_eth = 'ETH/USDT:USDT' 

# sell symbol lists
short_symbol = [symbol_btc, symbol_eth, symbol_sol]
long_symbol = [symbol_bnb]

# 設定風報比(R)
risk_ratio = 1.5
stop_ratio = 0.02
profit_ratio = risk_ratio * stop_ratio

# 假設你想要在 AGIX 價格高於 10 USDT 時下多單，低於 9 USDT 時下空單
init_buy_ratio = 1.0260
adjust_buy_ratio = init_buy_ratio
init_sell_ratio = init_buy_ratio * (1.0 - stop_ratio)
adjust_sell_ratio = init_buy_ratio * (1.0 + profit_ratio)

def sell(symbol, amount):
    order_short_futures = bybit.create_order(
        symbol,
        'Market',
        'sell',
        amount,
    )
    print(f"期貨開空單成功：{order_short_futures['info']}")

def buy(symbol, amount):
    order_long_futures = bybit.create_order(
        symbol,
        'Market',
        'buy',
        amount,
    )
    print(f"期貨開多單成功：{order_long_futures['info']}")

def build_long_short_contracts(long_symbol, short_symbol, long_amount, short_amount):
    long_size = len(long_symbol)
    short_size = len(short_symbol)
    each_long_amount = long_amount/long_size
    each_short_amount = short_amount/short_size

    for item in long_symbol:
        buy(item, each_long_amount)
        print(item)
        

    for item in short_symbol:
        sell(item, each_short_amount)
        print(item)

def get_long_short_ratio(long_symbol, short_symbol):
    # 確認目前交易對情況
    position_info = bybit.fetch_positions()
    long_amount = 0.0
    short_amount = 0.0

    for position in position_info:
        for item in long_symbol:
            if position['symbol'] == item:
                symbol_size = position['contracts']

                # 獲取交易對的目前價格
                long_ticker = bybit.fetch_ticker(item)
                # 提取價格
                long_price = long_ticker['last']
                long_symbol_amount = long_price * symbol_size
                long_amount += long_symbol_amount

                print(f"交易對 {item} 的數量：{symbol_size}, 有{long_symbol_amount} USDT")

        for item in short_symbol:
            if position['symbol'] == item:
                symbol_size = position['contracts']
                
                # 獲取交易對的目前價格
                short_ticker = bybit.fetch_ticker(item)
                # 提取價格
                short_price = short_ticker['last']
                short_symbol_amount = short_price * symbol_size
                short_amount += short_symbol_amount

                print(f"交易對 {item} 的數量：{symbol_size}, 有{short_symbol_amount} USDT")

    long_short_ratio = long_amount / short_amount

    print(f"long short ration的值為: {long_short_ratio}\n\n\n")

    return long_short_ratio

# def get_amount(symbol):
#     # 確認目前交易對情況
#     position_info = bybit.fetch_positions()
#     for position in position_info:
#         if position['symbol'] == symbol:

# 程式開始
# 一行中輸入多個幣對，以空格分隔
long_symbol = [str(item) for item in input("做空幣對：").split()]
short_symbol = [str(item) for item in input("做多幣對：").split()]
print(long_symbol)
print(short_symbol)

# 設定風報比
risk_ratio = float(input("請輸入風報比："))
stop_ratio = float(input("請設定損失比例："))
print(risk_ratio)
print(stop_ratio)

# 計算停利停損ratio
# init_buy_ratio = get_long_short_ratio(long_symbol, short_symbol)
adjust_buy_ratio = init_buy_ratio
adjust_profit_ratio = adjust_buy_ratio * (1.0 - stop_ratio)
adjust_sell_ratio = adjust_buy_ratio * (1.0 + profit_ratio)
print(adjust_profit_ratio)
print(adjust_sell_ratio)

while True:
    try:
        # 確認目前最新ratio
        long_short_ratio = get_long_short_ratio(long_symbol, short_symbol)

        # 設定移動停利停損
        if long_short_ratio > adjust_buy_ratio:
            print(f"更新buy ratio為：{long_short_ratio}, 原本 ratio為:{adjust_buy_ratio}, 原始買入ratio為:{init_buy_ratio}")
            adjust_sell_ratio = long_short_ratio * (1.0 - stop_ratio)
            adjust_stop_ratio = long_short_ratio * (1.0 + profit_ratio)
            adjust_buy_ratio = long_short_ratio

        # 到達停損，清空艙位
        if long_short_ratio == adjust_stop_ratio:
            # 下多單
            sell(long_symbol)
            buy(short_symbol)
        else:
            print("Ratio 價格在目標區間內，不執行任何操作\n\n")
    except Exception as e:
        print(f"Error fetching price: {e}")
    
    # 每隔 4 秒下單一次
    time.sleep(4)