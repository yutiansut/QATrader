# QATrader
QATRADER websocket 接入的期货交易

需要先行配置好Rabbitmq/ quantaxis_pubsub

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

> 下单:

```python
from QAPUBSUB import producer

p = producer.publisher_routing(
    user='admin', password='admin', host=host, exchange='QAORDER_ROUTER')

p.pub(json.dumps({
    'topic': 'sendorder',
    'account_cookie': acc,
    'strategy_id': 'test',
    'code': code,
    'price': price[code],
    'order_direction': 'SELL',
    'order_offset': 'CLOSE',
    'volume': 1,
    'order_time': str(datetime.datetime.now()),
    'exchange_id': 'SHFE'
}), routing_key=acc)

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
