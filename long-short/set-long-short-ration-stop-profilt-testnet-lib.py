import time
from tradeOrderLibray import MyCCXTLibrary

api_key = ''
secret = ''

long_symbol = 'BTC/USDT:USDT'
short_symbol = 'DOGE/USDT:USDT'

my_lib = MyCCXTLibrary('bybit', api_key, secret)

my_lib.use_testnet()

long_symbol = str(input("請輸入單一做多幣對："))
short_symbol = str(input("請設定單一做空幣對："))
print(long_symbol)
print(short_symbol)

# 設定初始入場比例
# init_buy_ratio = float(input("請設定入場比例："))

# 計算入場ratio
# 更新目前倉位及價格
positions = my_lib.get_positions()
long_ticker = my_lib.get_ticker(long_symbol)
short_ticker = my_lib.get_ticker(short_symbol)

init_buy_ratio = my_lib.get_initial_ratio_single_pair(long_symbol, short_symbol, positions, 10000)

# 設定風報比
risk_ratio = float(input("請輸入風報比："))
stop_ratio = float(input("請設定損失比例："))
print(risk_ratio)
print(stop_ratio)

# 計算初始停利停損ratio
adjust_buy_ratio = init_buy_ratio
adjust_stop_ratio = adjust_buy_ratio * (1.0 - stop_ratio)
adjust_profit_ratio = adjust_buy_ratio * (1.0 + risk_ratio * stop_ratio)
print(f"初始停損ratio為：{adjust_stop_ratio}")
print(f"初始停利ratio為：{adjust_profit_ratio}")

check_exit_loop = False

while True:
    try:
        # 更新目前倉位及價格
        long_ticker = my_lib.get_ticker(long_symbol)
        short_ticker = my_lib.get_ticker(short_symbol)

        positions = my_lib.get_positions()

        # 確認目前size
        long_size = my_lib.get_size(positions, long_symbol)
        long_price = my_lib.get_price(long_ticker)
        short_size = my_lib.get_size(positions, short_symbol)
        short_price = my_lib.get_price(short_ticker)
        long_amount = long_price * long_size
        short_amount = short_price * short_size
        print(f"目前最新long {long_symbol}為：{long_size}口, 總共 {long_amount} USDT")
        print(f"目前最新short {short_symbol}為：{short_size}口, 總共 {short_amount} USDT")
        
        current_ratio = my_lib.get_long_short_ratio(long_ticker, short_ticker, 10000)

        # 到達停損，清空艙位
        if current_ratio < adjust_stop_ratio:
            long_latest_price = my_lib.get_price(long_ticker)
            short_latest_price = my_lib.get_price(short_ticker)
            long_size = my_lib.get_size(positions, long_symbol)
            short_size = my_lib.get_size(positions, short_symbol)
            # 下多單
            my_lib.sell_by_contracts(long_symbol, long_size)
            my_lib.buy_by_contracts(short_symbol, short_size)

            print("到達停損，清空艙位\n\n")

            check_exit_loop = True

        # 到達停利，清空艙位
        elif current_ratio > adjust_profit_ratio:
            long_size = my_lib.get_size(positions, long_symbol)
            short_size = my_lib.get_size(positions, short_symbol)
            # 清空艙位
            my_lib.sell_by_contracts(long_symbol, long_size)
            my_lib.buy_by_contracts(short_symbol, short_size)

            print("到達停利，清空艙位\n\n")

            check_exit_loop = True

        else:
            print("Ratio 價格在目標區間內，不執行任何操作\n\n")

    
    except Exception as e:
        print(f"Error fetching price: {e}")
        break

    if check_exit_loop == True:

        # 計算實際獲利或虧損
        curret_loss = my_lib.cal_current_profit(positions, long_ticker, short_ticker)

        # print(f"投入：{actual_input_amount} USDT，營利百分比：{stop_profit_ratio * 100:.3f}%")
        print(f"虧損或營利: {curret_loss} USDT")
        break

    # 每隔 2 秒下單一次
    time.sleep(2)
