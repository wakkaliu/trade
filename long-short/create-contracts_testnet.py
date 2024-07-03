import ccxt

# 初始化 Bybit 期貨客戶端
bybit = ccxt.bybit({
    'apiKey': '',
    'secret': '',
})

# Set for testnet
bybit.set_sandbox_mode(True)

def sell_by_contracts(symbol, contracts):
    print(f"賣出\n\n\n")
    order_short_futures = bybit.create_order(
        symbol,
        'Market',
        'sell',
        contracts,
    )
    print(f"期貨開空單成功：{order_short_futures['info']}")

def buy_by_contracts(symbol, contracts):
    print(f"買入\n\n\n")
    order_long_futures = bybit.create_order(
        symbol,
        'Market',
        'buy',
        contracts,
    )
    print(f"期貨開多單成功：{order_long_futures['info']}")

def build_long_short_contracts(long_symbol, short_symbol, long_amount_usdt, short_amount_usdt):
    long_size = len(long_symbol)
    short_size = len(short_symbol)
    each_long_amount = long_amount_usdt/long_size
    each_short_amount = short_amount_usdt/short_size

    for item in long_symbol:
        each_long_contracts = amount_to_contracts(item, each_long_amount)
        buy_by_contracts(item, each_long_contracts)
        total_long_usdt = get_price(item) * get_size(item)
        print(f"做多{item} {short_amount_usdt} USDT, totally {total_long_usdt} USDT")


    for item in short_symbol:
        each_short_contracts = amount_to_contracts(item, each_short_amount)
        sell_by_contracts(item, each_short_contracts)
        total_short_usdt = get_price(item) * get_size(item)
        print(f"做空{item} {each_short_contracts} contracts, totally {total_short_usdt} USDT")

def amount_to_contracts(symbol, amount):
    symbol_price = get_price(symbol)
    num_contracts = round(amount / symbol_price, 3)
    print(f"usdt轉換成{symbol}下單數量, {num_contracts}口\n\n\n")

    return num_contracts

def get_size(coin_symbol):
     # 確認目前交易對情況
    size = 0.0
    position_info = bybit.fetch_positions()

    for position in position_info:
        if position['symbol'] == coin_symbol:
            size = position['contracts']

    return size

def get_price(coin_symbol):
    # 獲取 交易對 的目前價格
    ticker = bybit.fetch_ticker(coin_symbol)
    symblo_price = ticker['last']
    return symblo_price

# 程式開始
# 一行中輸入多個幣對，以空格分隔
long_symbol = [str(item) for item in input("做多幣對：").split()]
short_symbol = [str(item) for item in input("做空幣對：").split()]
print(long_symbol)
print(short_symbol)

# 設定做多做空金額
input_amount = float(input("請輸入預期投入金額："))

build_long_short_contracts(long_symbol, short_symbol, input_amount/2, input_amount/2)