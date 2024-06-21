import time
import ccxt

# 初始化 Bybit 期貨客戶端
bybit = ccxt.bybit({
    'apiKey': '',
    'secret': '',
})

# 設定交易對和數量
symbol_agix = 'AGIX/USDT:USDT'  # AGIXUSDU21 是 AGIX 的期貨合約
symbol_fet = 'FET/USDT:USDT'    # FETUSDU21 是 FET 的期貨合約
symbol_usdc = 'USDC/USDT:USDT'    # FETUSDU21 是 FET 的期貨合約
agix_amount = 30
fet_amount = 13                          # 下單數量

# 假設你想要在 AGIX 價格高於 10 USDT 時下多單，低於 9 USDT 時下空單
target_buy_ratio = 1.0260
target_sell_ratio = 1.02

while True:
    try:
        fet_size = 0
        agix_size = 0

        # 確認目前交易對情況
        position_info = bybit.fetch_positions()
        # count = position_info.count()
        # print(f"finish get position {count}")
        for position in position_info:
            print(f"in position loop, 交易對" + position['symbol'])
            if position['symbol'] == "FET/USDT:USDT":
                entry_price = position['entryPrice']
                fet_size = position['contracts']
                mode = position['marginMode']
                fet_side = position['side']
                percentage = position['contractSize']
                # print(f"交易對 {symbol_fet} 的開倉價格：{entry_price} USDT，數量：{agix_size} 初始保證金百分比：{percentage * 100:.3f}%")
                print(f"交易對 {symbol_fet} 的開倉價格：{entry_price} USDT，數量：{fet_size} mode: {mode} {percentage}, 買多賣空: {fet_side}")

            if position['symbol'] == "AGIX/USDT:USDT":
                entry_price = position['entryPrice']
                agix_size = position['contracts']
                mode = position['marginMode']
                agix_side = position['side']
                percentage = position['contractSize']
                # print(f"交易對 {symbol_agix} 的開倉價格：{entry_price} USDT，數量：{agix_size} mode: {mode} 初始保證金百分比：{percentage * 100:.3f}%")
                print(f"交易對 {symbol_agix} 的開倉價格：{entry_price} USDT，數量：{agix_size} mode: {mode} 初始保證金百分比：{percentage}, 買多賣空: {agix_side}")


        # 獲取 AGIX 和 FET 的目前價格
        fet_ticker = bybit.fetch_ticker(symbol_fet)
        agix_ticker = bybit.fetch_ticker(symbol_agix)

        # 提取價格
        agix_price = agix_ticker['last']
        fet_price = fet_ticker['last']

        stock_total_price = fet_size * fet_price
        risk_ratio = stock_total_price / 512

        print(f"AGIX 目前價格：{agix_price} USDT")
        print(f"FET 目前價格：{fet_price} USDT")
        print(f"目前FET 持倉總值：{ stock_total_price} USDT")
        print(f"目前 risk ratio：{ risk_ratio}")

        fet_agix_ratio = fet_price*433.226/agix_price/1000
        print(f"目前fet/agix交易對ratio：{fet_agix_ratio} USDT")

        if fet_agix_ratio > target_buy_ratio and risk_ratio < 1:
            # 下多單
            print(f"FET_AGIX 價格高於 {fet_agix_ratio} USDT，買入fet_agix交易對")
            # 在這裡執行下多單的操作
            # 開多單（做多）
            order_long_futures = bybit.create_order(
                symbol_agix,
                'Market',
                'buy',
                agix_amount,
            )
            print(f"期貨開多單成功：{order_long_futures['info']}")

            # 開空單（做空）
            order_short_futures = bybit.create_order(
                symbol_fet,
                'Market',
                'sell',
                fet_amount,
            )
            print(f"期貨開空單成功：{order_short_futures['info']}")

            # break

        elif fet_agix_ratio < target_sell_ratio and agix_size > 39:
            # 下空單
            print(f"FET_AGIX 價格低於 {target_sell_ratio} USDT，賣出fet_agix交易對")
            # 在這裡執行下空單的操作
            # 開多單（做空）
            order_long_futures = bybit.create_order(
                symbol_agix,
                'Market',
                'sell',
                agix_amount,
            )

            print(f"期貨開空單成功：{order_long_futures['info']}")

            # 開多單（做多）
            order_short_futures = bybit.create_order(
                symbol_fet,
                'Market',
                'buy',
                fet_amount,
            )
            print(f"期貨開多單成功：{order_short_futures['info']}")

        else:
            print("Ratio 價格在目標區間內，不執行任何操作\n\n")
    except Exception as e:
        print(f"Error fetching price: {e}")
    
    # 每隔 2 秒下單一次
    time.sleep(2)

# test
# leverage = 2  # 槓桿倍數
# # bybit.set_leverage(leverage, symbol_usdc)
# # order = bybit.create_market_buy_order(symbol_usdc, 5, params = {"leverage": 2})
# order = bybit.create_market_sell_order(symbol_usdc, 5, params = {"leverage": 2})

# print(f"下單成功，訂單 ID：{order['id']}")