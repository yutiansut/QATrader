# QATrader
QATRADER websocket 接入的期货交易/ 并给予HTTP接口方便快速调用业务(可自行封装)

需要先行配置好Rabbitmq/ quantaxis_pubsub

```
rabbitmq ubuntu一键部署 https://github.com/yutiansut/QUANTAXIS_RUN/blob/master/ubuntu_install.bash

windows 可以参考, erlang/rabbit的安装文件在群文件中有
```


策略无需考虑交易的部分, 及策略只负责从数据库读取实时的账户数据/ 并发送业务请求到EVENT MQ即可实现交易

这种设置主要是为了单账户多策略/ 以及单策略多市场等考虑

> 获取账户数据:

```python
acc = pymongo.MongoClient().QAREALTIME.account.find_one({'account_cookie':'xxxx'})

# 基础信息
print(acc['accounts'])

# 持仓
print(acc['positions'])

# 订单
print(acc['orders'])

# 交易
print(acc['trades'])

# 银期转账
print(acc['transfer'])

# 查询银行(多银行)
print(acc['banks'])

```

当然 除了从数据库获取, 你也可以从业务平台上订阅该账户的增量信息

```python
from QAPUBSUB import consumer
import json
from QAREALTIME.setting import real_account_mongo_ip
z = consumer.subscriber_routing(host='127.0.0.1', user='admin', password='admin',exchange='QAACCOUNT',routing_key='812572')
import pandas as pd
import QUANTAXIS as QA


def parse(a, b, c, body):
    z = json.loads(str(body, encoding='utf-8'))
    # QA.QA_util_log_info(z)
    if z['aid'] == 'rtn_data':
        data = z['data'][0]['trade']
        account_cookie = str(list(data.keys())[0])
        QA.QA_util_log_info(data)
        user_id = data[account_cookie]['user_id']
        accounts = data[account_cookie]['accounts']['CNY']
        positions = data[account_cookie]['positions']
        orders = data[account_cookie]['orders']
        trades = data[account_cookie]['trades']
        banks = data[account_cookie]['banks']
        transfers = data[account_cookie]['transfers']

        QA.QA_util_log_info("======================= QUANTAXIS ::{}=======================".format(
            account_cookie))
        QA.QA_util_log_info("== pre_balance " + str(accounts['pre_balance']) +
                            "== balance " + str(accounts['balance']))
        QA.QA_util_log_info("== 可用资金 " + str(accounts['available']) +
                            "== 冻结保证金 " + str(accounts['margin']) +
                            "== risk_ratio " + str(accounts['risk_ratio']))
        QA.QA_util_log_info('== position_profit ' +
                            str(accounts['position_profit']))
        QA.QA_util_log_info("==============POSITIONS===============")
        QA.QA_util_log_info(pd.DataFrame(positions))
        QA.QA_util_log_info("==============ORDERS==================")
        QA.QA_util_log_info(pd.DataFrame(orders))
        QA.QA_util_log_info("==============TRADERS==================")
        QA.QA_util_log_info(pd.DataFrame(trades))
z.callback = parse
z.start()
```


> 下单:

```python
from QAPUBSUB import producer

p = producer.publisher_routing(
    user='admin', password='admin', host=host, exchange='QAORDER_ROUTER')

p.pub(json.dumps({
    'topic': 'sendorder',
    'account_cookie': '111111',
    'strategy_id': 'test',
    'code': 'rb1910',
    'price': 4750,
    'order_direction': 'BUY',
    'order_offset': 'OPEN',
    'volume': 1,
    'order_time': str(datetime.datetime.now()),
    'exchange_id': 'SHFE'
}), routing_key='111111')

```

> 撤单:

```python
from QAPUBSUB import producer

p = producer.publisher_routing(
    user='admin', password='admin', host=host, exchange='QAORDER_ROUTER')
    
p.pub(json.dumps({
    'topic':'cancel_order',
    'order_id':'xxxx'}), routing_key=acc)
```
