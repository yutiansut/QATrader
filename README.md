# QATrader


_QATrader兼容 [QIFI协议标准](https://github.com/QUANTAXIS/QIFI/blob/master/README.md)_

![version](https://img.shields.io/pypi/v/QATRADER.svg)

```
pip install QATRADER
```

QATRADER 会逐步开放多个语言的实现

==>  GO Client

[QATrader_GO](https://github.com/yutiansut/qatrader_go)

==> Rust Client

[QATrader_Rust](https://github.com/yutiansut/qatrader_rust)





QATRADER websocket 接入的期货交易/ 并给予HTTP接口方便快速调用业务(可自行封装)

需要先行配置好Rabbitmq/ quantaxis_pubsub

```
rabbitmq ubuntu一键部署 https://github.com/yutiansut/QUANTAXIS_RUN/blob/master/ubuntu_install.bash

windows 可以参考, erlang/rabbit的安装文件在群文件中有
```

安装部署可以参见: [安装参考](期货模拟盘从零配置.md)


策略无需考虑交易的部分, 及策略只负责从数据库读取实时的账户数据/ 并发送业务请求到EVENT MQ即可实现交易

这种设置主要是为了单账户多策略/ 以及单策略多市场等考虑


## QATRADER 提供的两种交易接入方案

### 1. eventmq 接入(AMQP协议)

eventmq的接入模式速度较快, 延迟也较低

AMQP协议天生也支持多个语言: c++/java/python/go/javascript/rust (具体可以在github搜索 rabbitmq的相关支持)

QUANTAIXS的python版本的api接入 采用quantaxis_pubsub

详细信息可以参考:[eventmq](## EVENTMQ 接入API)


### 2. http 接入


```
在pip install 之后, 在命令行输入

qatraderserver

即可开启http端口(8020)
```

> 账户相关

查询账户组合: [GET]  http://localhost:8020/tradeaccounts?action=list_sim

查询单个账户: [GET]  http://localhost:8020/tradeaccounts?action=query_account&account_cookie=1010101

查询账户历史(昨日 前日这些)  [GET] http://localhost:8020/tradeaccounts?action=query_accounthistory&account_cookie=1010101

查询账户的资金曲线 [GET] http://localhost:8020/tradeaccounts?action=query_accounthistorytick&account_cookie=1010101


> 订单相关  [POST] http://localhost:8020/order?action={}&acc={}

下单: [POST] 

attention:  
1. exchange 内的交易所大写
2. direction/offset 大写

http://localhost:8020/order?action=sendorder&acc=1010101&price=3800&code=rb1910&&direction=BUY&offset=OPEN&volume=1&exchange=SHFE&type=sim


撤单 [POST]

http://localhost:8020/order?action=cancel_order&acc=1010101&order_id=xxxxx

转账 [POST]


http://localhost:8020/order?action=transfer&acc=1010101&type=real&amount=100


查询银行 [POST]  (实盘独有API)

http://localhost:8020/order?action=query_bank&acc=1010101&type=real&bank_id=1

修改密码 [POST] 


http://localhost:8020/order?action=change_password&acc=1010101&new_password=xxxx&type=real

查询结算单  [POST]

http://localhost:8020/order?action=query_settlement&acc=1010101&day=20190818



## EVENTMQ 接入API

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
