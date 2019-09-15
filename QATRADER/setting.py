# 以下是一些交易的时候的设定

# 交易服务器

import os
"""
交易的服务器地址
qatrademq_ip
qatrademq_host

qatrademongo_ip

"""

trade_server_ip = os.getenv('qatrademq_ip','127.0.0.1')
trade_server_port = os.getenv('qatrademq_port','5672')

trade_server_user = 'admin'
trade_server_password = 'admin'

trade_server_account_exchange = 'QAACCOUNT'
trade_server_order_exchange = 'QAORDER_ROUTER'

simtrade_server_ip = os.getenv('qatrademq_ip','127.0.0.1')
simtrade_server_port = os.getenv('qatrademq_port','5672')

simtrade_server_user = 'admin'
simtrade_server_password = 'admin'

simtrade_server_account_exchange = 'QAACCOUNT'
simtrade_server_order_exchange = 'QAORDER_ROUTER'

# 数据服务器 行情数据

market_data_ip = '127.0.0.1'
market_data_port = '5672'
market_data_user = 'admin'
market_data_password = 'admin'


# 历史数据服务器

history_data_mongo_ip =  os.getenv('qatrademongo_ip','127.0.0.1')
history_data_mongo_port = 27017

real_account_mongo_ip = os.getenv('qatrademongo_ip','127.0.0.1')
real_account_mongo_port = 27017
sim_account_mongo_ip = os.getenv('qatrademongo_ip','127.0.0.1')
sim_account_mongo_port = 27017


settings = {
    'trade_server_ip': trade_server_ip,
    'trade_server_port': trade_server_port,

}
