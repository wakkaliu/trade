import time
import ccxt

# 初始化 Bybit 期貨客戶端
bybit = ccxt.bybit({
    'apiKey': '',
    'secret': '',
})

# Set for testnet
bybit.set_sandbox_mode(True)

# 設定交易對和數量
# symbol_agix = 'AGIX/USDT:USDT'  # AGIXUSDU21 是 AGIX 的期貨合約
# symbol_fet = 'FET/USDT:USDT'    # FETUSDU21 是 FET 的期貨合約
# symbol_usdc = 'USDC/USDT:USDT'    # FETUSDU21 是 FET 的期貨合約
symbol_btc = 'BTC/USDT:USDT' 
symbol_sol = 'SOL/USDT:USDT' 
symbol_bnb = 'BNB/USDT:USDT' 
symbol_eth = 'ETH/USDT:USDT' 

# sell symbol lists
# short_symbol = [symbol_btc, symbol_eth, symbol_sol]
# long_symbol = [symbol_bnb]
# short_symbol = symbol_btc
# long_symbol = symbol_bnb

# 設定風報比(R)
# risk_ratio = 1.5
# stop_ratio = 0.02
# profit_ratio = risk_ratio * stop_ratio

# 假設你想要在 AGIX 價格高於 10 USDT 時下多單，低於 9 USDT 時下空單
# init_buy_ratio = 1.0260
# adjust_buy_ratio = init_buy_ratio
# init_sell_ratio = init_buy_ratio * (1.0 - stop_ratio)
# adjust_sell_ratio = init_buy_ratio * (1.0 + profit_ratio)
# adjust_stop_ratio = 3.5

def sell(symbol, amount):
    print(f"賣出\n\n\n")
    # order_short_futures = bybit.create_order(
    #     symbol,
    #     'Market',
    #     'sell',
    #     amount,
    # )
    # print(f"期貨開空單成功：{order_short_futures['info']}")

def buy(symbol, amount):
    print(f"買入\n\n\n")
    # order_long_futures = bybit.create_order(
    #     symbol,
    #     'Market',
    #     'buy',
    #     amount,
    # )
    # print(f"期貨開多單成功：{order_long_futures['info']}")

def build_long_short_contracts(long_symbol, short_symbol, long_amount, short_amount):
    buy(long_symbol, long_amount)
    print(f"做多{long_symbol} {long_amount} USDT")

    sell(short_symbol, short_amount)
    print(f"做空{long_symbol} {short_amount} USDT")

def get_size(coin_symbol):
     # 確認目前交易對情況
    size = 0.0
    position_info = bybit.fetch_positions()
    
    for position in position_info:
        if position['symbol'] == coin_symbol:
            size = position['contracts']

    return size

def get_price(coin_symbol):
    # 獲取 AGIX 和 FET 的目前價格
    ticker = bybit.fetch_ticker(coin_symbol)
    return ticker

def get_long_short_ratio(long_symbol, short_symbol):
    long_short_ratio = 0.0

    # 獲取做多交易對的目前價格
    long_ticker = bybit.fetch_ticker(long_symbol)
    # 提取價格
    long_price = long_ticker['last']

    # 獲取做空交易對的目前價格
    short_ticker = bybit.fetch_ticker(short_symbol)
    # 提取價格
    short_price = short_ticker['last']

    long_short_ratio = long_price / short_price

    print(f"long short ration的值為: {long_short_ratio}\n\n\n")

    return long_short_ratio

# 程式開始
# 一行中輸入多個幣對，以空格分隔
# long_symbol = [str(item) for item in input("做空幣對：").split()]
# short_symbol = [str(item) for item in input("做多幣對：").split()]
long_symbol = str(input("請輸入做空幣對："))
short_symbol = str(input("請設定做多幣對："))
print(long_symbol)
print(short_symbol)

# 設定風報比
risk_ratio = float(input("請輸入風報比："))
stop_ratio = float(input("請設定損失比例："))
print(risk_ratio)
print(stop_ratio)

# 設定做多做空金額
input_amount = float(input("請輸入投入金額："))

# 買入交易對
init_buy_ratio = 0.0
build_long_short_contracts(long_symbol, short_symbol, input_amount/2, input_amount/2)
init_buy_ratio = get_long_short_ratio(long_symbol, short_symbol)
print(init_buy_ratio)

# 計算初始停利停損ratio
adjust_buy_ratio = init_buy_ratio
adjust_stop_ratio = adjust_buy_ratio * (1.0 - stop_ratio)
adjust_profit_ratio = adjust_buy_ratio * (1.0 + risk_ratio * stop_ratio)
print(adjust_stop_ratio)
print(adjust_profit_ratio)

check_exit_loop = False

while True:
    try:
        # 確認目前最新ratio
        long_short_ratio = get_long_short_ratio(long_symbol, short_symbol)
        print(f"目前最新 ratio為：{long_short_ratio}")

        if long_short_ratio == 0:
            check_exit_loop = True

        # 設定移動停利停損
        if long_short_ratio > adjust_buy_ratio:
            print(f"更新buy ratio為：{long_short_ratio}, 原本 ratio為:{adjust_buy_ratio}, 原始買入ratio為:{init_buy_ratio}")
            adjust_stop_ratio = long_short_ratio * (1.0 - stop_ratio)
            adjust_profit_ratio = long_short_ratio * (1.0 + risk_ratio * stop_ratio)
            adjust_buy_ratio = long_short_ratio
            print(f"新的止損：{adjust_stop_ratio}, 新的止盈: {adjust_profit_ratio}")


        # 到達停損，清空艙位
        if long_short_ratio == adjust_stop_ratio:
            long_latest_price = get_price(long_symbol)
            short_latest_price = get_price(short_symbol)
            long_size = get_size(long_symbol)
            short_size = get_size(short_symbol)
            # 下多單
            sell(long_symbol, long_size)
            buy(short_symbol, short_size)

            print("到達停損，清空艙位\n\n")

            # 計算實際獲利或虧損
            long_stop_amount = long_latest_price * long_size
            short_stop_amount = short_latest_price * short_size

            stop_profit_ratio = ((long_stop_amount + short_stop_amount) / input_amount) - 1

            print(f"投入：{input_amount} USDT，營利百分比：{stop_profit_ratio * 100:.3f}%")
            
            check_exit_loop = True

        else:
            print("Ratio 價格在目標區間內，不執行任何操作\n\n")
    except Exception as e:
        print(f"Error fetching price: {e}")
        break

    if check_exit_loop == True:
        break

    # 每隔 2 秒下單一次
    time.sleep(2)
