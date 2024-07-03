import ccxt

class MyCCXTLibrary:
    def __init__(self, exchange_name, api_key, secret):
        self.exchange = getattr(ccxt, exchange_name)({
            'apiKey': api_key,
            'secret': secret,
        })

    def use_testnet(self):
        self.exchange.set_sandbox_mode(True)

    def get_ticker(self, symbol):
        return self.exchange.fetch_ticker(symbol)

    def get_balance(self):
        return self.exchange.fetch_balance()
    
    def get_positions(self):
        return self.exchange.fetch_positions()
    
    def get_price(self, ticker):
        # 獲取 交易對 的目前價格
        symblo_price = ticker['last']
        return symblo_price
    
    def get_initial_ratio_single_pair(self, long_symbol, short_symbol, positions, scale):
        long_entry_price = 0.0
        short_entry_price = 0.0

        for position in positions:
            # 判断是做多还是做空
            if position['side'] == 'long' and position['symbol'] == long_symbol:
                long_entry_price = float(position['entryPrice'])
            elif position['side'] == 'short' and position['symbol'] == short_symbol:
                short_entry_price = float(position['entryPrice'])
            else:
                continue
            
        init_ratio = long_entry_price / short_entry_price * scale

        print(f"long entry price為: {long_entry_price}\n")
        print(f"short entry price為: {short_entry_price}\n")
        print(f"entry ratio為: {init_ratio}\n")

        return init_ratio
    
    def get_size(self, position_info, coin_symbol):
         # 確認目前交易對情況
        size = 0.0
        # position_info = bybit.fetch_positions()

        for position in position_info:
            if position['symbol'] == coin_symbol:
                size = position['contracts']

        return size
    
    def get_long_short_ratio(self, long_ticker, short_ticker, scale):
        long_short_ratio = 0.0

        # 獲取做多交易對的目前價格
        long_price = long_ticker['last']

        # 獲取做空交易對的目前價格
        short_price = short_ticker['last']

        long_short_ratio = scale * long_price / short_price

        print(f"long short ration的值為: {long_short_ratio}\n\n\n")

        return long_short_ratio
    
    def cal_current_profit(self, positions, long_ticker, short_ticker):
        # 计算盈亏
        for position in positions:
            # 判断是做多还是做空
            if position['side'] == 'long':
                entry_price = float(position['entryPrice'])
                current_price = float(long_ticker['last'])
                amount = float(position['contracts'])
            
                long_pnl = (current_price - entry_price) * amount  # 做多的盈亏计算
            else:
                entry_price = float(position['entryPrice'])
                current_price = float(short_ticker['last'])
                amount = float(position['contracts'])
            
                short_pnl = (current_price - entry_price) * amount  # 做多的盈亏计算

        # 淨營利
        net_profit = long_pnl + short_pnl
            
        print(f"淨營利: {net_profit}")

        return net_profit

    def build_long_short_contracts_single(self, long_symbol, short_symbol, long_amount_usdt, short_amount_usdt):
        long_contracts = self.amount_to_contracts(long_symbol, long_amount_usdt)
        self.buy_by_contracts(long_symbol, long_contracts)
        print(f"做多{long_symbol} {long_amount_usdt} USDT")

        short_contracts = self.amount_to_contracts(short_symbol, short_amount_usdt)
        self.sell_by_contracts(short_symbol, short_contracts)
        print(f"做空{long_symbol} {short_amount_usdt} USDT")

    def amount_to_contracts(self, symbol, amount):
        symbol_price = self.get_price(symbol)
        num_contracts = round(amount / symbol_price, 3)
        print(f"usdt轉換成{symbol}下單數量, {num_contracts}口\n\n\n")

        return num_contracts

    def sell_by_contracts(self, symbol, contracts):
        print(f"賣出\n\n\n")
        order_short_futures = self.exchange.create_order(
            symbol,
            'Market',
            'sell',
            contracts,
        )
        print(f"期貨開空單成功：{order_short_futures['info']}")

    def buy_by_contracts(self, symbol, contracts):
        print(f"買入\n\n\n")
        order_long_futures = self.exchange.create_order(
            symbol,
            'Market',
            'buy',
            contracts,
        )
        print(f"期貨開多單成功：{order_long_futures['info']}")

    def build_long_short_contracts_list(self, long_symbol, short_symbol, long_amount_usdt, short_amount_usdt):
        long_size = len(long_symbol)
        short_size = len(short_symbol)
        each_long_amount = long_amount_usdt/long_size
        each_short_amount = short_amount_usdt/short_size

        for item in long_symbol:
            each_long_contracts = self.amount_to_contracts(item, each_long_amount)
            self.buy_by_contracts(item, each_long_contracts)
            total_long_usdt = self.get_price(item) * self.get_size(item)
            print(f"做多{item} {short_amount_usdt} USDT, totally {total_long_usdt} USDT")


        for item in short_symbol:
            each_short_contracts = self.amount_to_contracts(item, each_short_amount)
            self.sell_by_contracts(item, each_short_contracts)
            total_short_usdt = self.get_price(item) * self.get_size(item)
            print(f"做空{item} {each_short_contracts} contracts, totally {total_short_usdt} USDT")


