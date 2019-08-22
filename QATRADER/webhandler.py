import datetime
import json
import os
import time

import pymongo
from QUANTAXIS import qa_path
from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado_http2.server import Server

from QAPUBSUB import producer
from QATRADER.setting import (real_account_mongo_ip, real_account_mongo_port,
                              sim_account_mongo_ip, sim_account_mongo_port,
                              simtrade_server_ip, trade_server_ip,
                              trade_server_password, trade_server_user)
from QAWebServer import QABaseHandler, QAWebSocketHandler
from QAWebServer.jobhandler import JOBHandler

"""
1. 一个完整的交易 部署/控制/查看过程
"""


class TradeAccountHandler(QABaseHandler):

    def get(self):
        client = pymongo.MongoClient()
        action = self.get_argument('action')
        if action == 'list_sim':
            """
            http://localhost:8020/tradeaccounts?action=list_sim&portfolio=default
            """
            portfolio = self.get_argument('portfolio', 'default')
            res = []
            portfoliox = {'pre_balance': 0, 'balance': 0,
                          'close_profit': 0, 'float_profit': 0, 'available': 0}
            for item in pymongo.MongoClient(host=sim_account_mongo_ip, port=sim_account_mongo_port).QAREALTIME.account.find(
                    {'portfolio': portfolio}, {'_id': 0, 'accounts': 1, 'broker_name': 1, 'status': 1, 'trading_day': 1}):
                _t = item['accounts']
                res.append(_t)
                try:
                    _t.update(
                        {'status': item['status'], 'broker_name': item['broker_name'], 'trading_day': item['trading_day']})
                    portfoliox['pre_balance'] += item['accounts']['pre_balance']
                    portfoliox['balance'] += item['accounts']['balance']
                    portfoliox['close_profit'] += item['accounts']['close_profit']
                    portfoliox['float_profit'] += item['accounts']['float_profit']
                    portfoliox['available'] += item['accounts']['available']

                except:
                    pass

            for key in portfoliox.keys():
                portfoliox[key] = round(portfoliox[key], 2)
            portfoliox['portfolio'] = portfolio
            self.write({
                'status': 200,
                'result': res,
                'portfolio': portfoliox
            })
        if action == 'list_sim_portfolio':
            res = list(set([item['portfolio'] for item in pymongo.MongoClient(host=sim_account_mongo_ip, port=sim_account_mongo_port).QAREALTIME.account.find(
                {}, {'_id': 0, 'portfolio': 1})]))
            self.write({
                'status': 200,
                'result': res
            })
        elif action == 'list_real':
            res = []
            for item in pymongo.MongoClient(host=real_account_mongo_ip, port=real_account_mongo_port).QAREALTIME.account.find(
                    {}, {'_id': 0, 'accounts': 1, 'broker_name': 1, 'status': 1, 'trading_day': 1}):
                _t = item['accounts']
                _t.update(
                    {'status': item['status'], 'broker_name': item['broker_name'], 'trading_day': item['trading_day']})
                res.append(_t)
            # print(res)
            self.write({
                'status': 200,
                'result': res
            })
        elif action == 'query_account':
            account_cookie = self.get_argument('account_cookie')
            # print(account_cookie)
            # print(client.QAREALTIME.account.find_one(
            #     {'account_cookie': account_cookie}, {'_id': 0}))
            self.write({
                'status': 200,
                'result': client.QAREALTIME.account.find_one({'account_cookie': account_cookie}, {'_id': 0})
            })
        elif action == 'query_accounthistory':
            account_cookie = self.get_argument('account_cookie')
            # print(account_cookie)
            # print([item for item in client.QAREALTIME.history.find({'account_cookie': account_cookie}, {'_id': 0})])
            self.write({
                'status': 200,
                'result': [{'trading_day': item['trading_day'], 'balance': item['accounts']['balance']} for item in client.QAREALTIME.history.find({'account_cookie': account_cookie}, {'_id': 0})]
            })
        elif action == 'query_accounthistorytick':
            account_cookie = self.get_argument('account_cookie')
            self.write({
                'status': 200,
                'result': [{'trading_day': str(item['updatetime']), 'balance': item['accounts']['balance']} for item in client.QAREALTIME.hisaccount.find({'account_cookie': account_cookie}, {'_id': 0})]
            })

    def post(self):
        client = pymongo.MongoClient().QAREALTIME
        action = self.get_argument('action')
        if action == 'restart_all':

            for acc in client.account.find({'status': 500}):
                client.account.update_one({'_id': acc['_id']}, {
                    '$set': {'status': 100}})
        elif action == 'kill':
            tradetype = self.get_argument('type', 'sim')
            if tradetype == 'sim':
                p = producer.publisher_routing(user=trade_server_user, password=trade_server_password,
                                               host=simtrade_server_ip, exchange='QAORDER_ROUTER')
            else:
                p = producer.publisher_routing(user=trade_server_user, password=trade_server_password,
                                               host=trade_server_ip, exchange='QAORDER_ROUTER')
            p.pub(json.dumps({
                'topic': 'kill'
            }), routing_key=self.get_argument('account_cookie'))
        elif action == 'killall':
            for acc in client.account.find({'status': 200}):
                p = producer.publisher_routing(user=trade_server_user, password=trade_server_password,
                                               host=simtrade_server_ip, exchange='QAORDER_ROUTER')
                print(acc['account_cookie'])
                p.pub(json.dumps({
                    'topic': 'kill'
                }), routing_key=acc['account_cookie'])


def adaptChange(x): return float(x) if '.' in str(x) else int(x)


class SendOrderHandler(QABaseHandler):
    event = {}
    starttime = str(datetime.datetime.now())
    client = pymongo.MongoClient().QAREALTIME
    event['startime'] = starttime

    def post(self):
        action = self.get_argument('action')

        acc = self.get_argument('acc')
        xtime = datetime.datetime.now()
        #self.event['startime'] = self.starttime
        if acc not in self.event.keys():
            self.event[acc] = {}
        if action not in self.event[acc].keys():
            self.event[acc][action] = []
        if action == 'sendorder':
            price = self.get_argument('price')
            code = self.get_argument('code')
            direction = self.get_argument('direction')
            offset = self.get_argument('offset')
            volume = self.get_argument('volume')
            exchange_id = self.get_argument('exchange')
            accounttrade = self.get_argument('type')
            price = adaptChange(price)
            volume = adaptChange(volume)
            if accounttrade == 'real':
                p = producer.publisher_routing(user=trade_server_user, password=trade_server_password,
                                               host=trade_server_ip, exchange='QAORDER_ROUTER')
            else:
                p = producer.publisher_routing(user=trade_server_user, password=trade_server_password,
                                               host=simtrade_server_ip, exchange='QAORDER_ROUTER')

            self.event[acc][action].append({
                'reqesttime': xtime,
                'account_cookie': acc,
                'topic': action,
                'strategy_id': 'test',
                'code': code,
                'price': price,
                'order_direction': direction,
                'order_offset': offset,
                'volume': volume,
                'order_time': time,
                'exchange_id': exchange_id
            })
            p.pub(json.dumps({
                'topic': action,
                'account_cookie': acc,
                'strategy_id': 'test',
                'code': code,
                'price': price,
                'order_direction': direction,
                'order_offset': offset,
                'volume': volume,
                'order_time': str(datetime.datetime.now()),
                'exchange_id': exchange_id
            }), routing_key=acc)
            self.client.event.update_one({'starttime': self.starttime, 'account_cookie': acc}, {
                                         '$set': self.event[acc]}, upsert=True)
            self.write({
                'status': 200,
                'result': {
                    'topic': action,
                    'account_cookie': acc,
                    'strategy_id': 'test',
                    'code': code,
                    'price': price,
                    'order_direction': direction,
                    'order_offset': offset,
                    'volume': volume,
                    'exchange_id': exchange_id}
            })
        elif action == 'cancel_order':
            orderid = self.get_argument('order_id')
            accounttrade = self.get_argument('type')
            if accounttrade == 'real':
                p = producer.publisher_routing(user=trade_server_user, password=trade_server_password,
                                               host=trade_server_ip, exchange='QAORDER_ROUTER')
            else:
                p = producer.publisher_routing(user=trade_server_user, password=trade_server_password,
                                               host=simtrade_server_ip, exchange='QAORDER_ROUTER')
            p.pub(json.dumps({
                'topic': action,
                'account_cookie': acc,
                'order_id':  orderid
            }), routing_key=acc)
            self.event[acc][action].append({
                'topic': action,
                'reqesttime': xtime,
                'account_cookie': acc,
                'order_id': orderid
            })
            self.client.event.update_one({'starttime': self.starttime, 'account_cookie': acc}, {
                                         '$set': self.event[acc]}, upsert=True)
        elif action == 'transfer':
            #bankid = self.get_argument('bankid')
            # bankpassword = self.get_argument('bankpassword')
            # capitalpassword = self.get_argument('capitalpassword')
            """
            此处需要控制请求:

            1分钟内单账户 不允许 相同金额的出入金

            """

            amount = self.get_argument('amount')
            accounttrade = self.get_argument('type')

            xflag = False
            lastrequest = list(self.event[acc][action])
            # print(lastrequest)
            if len(lastrequest) == 0:
                xflag = True
            else:
                if float(amount) == float(lastrequest[-1]['amount']):
                    if xtime - lastrequest[-1]['reqesttime'] > datetime.timedelta(seconds=60):
                        #print('true for >60')
                        xflag = True
                    else:
                        # print('wrong in 60s')
                        xflag = False
                else:
                    # print(amount)
                    # print(lastrequest[-1]['amount'])
                    # print('true for not equal amount')
                    xflag = True
            if xflag:
                client = pymongo.MongoClient(
                    trade_server_ip).QAREALTIME.account
                res = client.find_one({'account_cookie': acc})
                if res is not None:
                    bank = res['banks']
                    accounts1 = res['accounts']
                    if len(bank) == 0:
                        self.write({
                            'status': 400,
                            'result': '没有银行'
                        })
                    else:

                        bankid = self.get_argument('bankid', bank[0]['bankid'])
                        before = bank[bankid]['fetch_amount']
                        if before == -1:
                            self.write({
                                'status': 400,
                                'result': '查询银行未就绪'
                            })
                        else:

                            if accounttrade == 'real':
                                staticbalance1 = accounts1['pre_balance']
                                p = producer.publisher_routing(user=trade_server_user, password=trade_server_password,
                                                               host=trade_server_ip, exchange='QAORDER_ROUTER')
                                p.pub(json.dumps({
                                    'topic': action,
                                    'account_cookie': acc,
                                    'amount': float(amount)
                                }), routing_key=acc)
                                self.event[acc][action].append({
                                    'topic': action,
                                    'account_cookie': acc,
                                    'amount': float(amount),
                                    'reqesttime': xtime,
                                })
                                self.client.event.update_one({'starttime': self.starttime, 'account_cookie': acc}, {
                                    '$set': self.event[acc]}, upsert=True)
                                time.sleep(2)
                                p.pub(json.dumps({
                                    'topic': 'query_bank',
                                    'account_cookie': acc,
                                }), routing_key=acc)

                                time.sleep(2)
                                res2 = client.find_one(
                                    {'account_cookie': acc})
                                bank2 = res2['banks']
                                accounts2 = res2['accounts']
                                staticbalance2 = accounts2['pre_balance']
                                after = bank2[bankid]['fetch_amount']

                                # print(res2['banks'])

                                if before - after == float(amount) or staticbalance1 - staticbalance2 == float(amount):

                                    self.write({
                                        'status': 200,
                                        'result': float(amount),
                                        'before': before,
                                        'after': after,
                                        'amount': float(amount)
                                    })
                                else:
                                    p.pub(json.dumps({
                                        'topic': 'query_bank',
                                        'account_cookie': acc,
                                    }), routing_key=acc)
                                    time.sleep(4)
                                    res = client.find_one(
                                        {'account_cookie': acc})
                                    bank = res['banks']
                                    after = bank[bankid]['fetch_amount']
                                    accounts2 = res2['accounts']
                                    staticbalance2 = accounts2['pre_balance']
                                    # print(res['banks'])
                                    if before - after == float(amount) or staticbalance1 - staticbalance2 == float(amount):
                                        self.write({
                                            'status': 200,
                                            'result': float(amount),
                                            'before': before,
                                            'after': after,
                                            'amount': float(amount)
                                        })
                                    else:
                                        self.write({
                                            'status': 500,
                                            'result': '等待时间过长',
                                            'before': before,
                                            'after': after,
                                            'amount': float(amount)
                                        })

                            else:
                                self.write({
                                    'status': 400,
                                    'result': '请使用实盘账户字段 real'
                                })
            else:
                self.write({
                    'status': 400,
                    'result': '1min重复提交, 请于下次 {} 提交'.format(lastrequest[-1]['datetime']+datetime.timedelta(60))
                })

        elif action == 'query_bank':
            accounttrade = self.get_argument('type')
            bankid = self.get_argument('bankid', False)
            if accounttrade == 'real':
                p = producer.publisher_routing(user=trade_server_user, password=trade_server_password,
                                               host=trade_server_ip, exchange='QAORDER_ROUTER')
            else:
                p = producer.publisher_routing(user=trade_server_user, password=trade_server_password,
                                               host=simtrade_server_ip, exchange='QAORDER_ROUTER')
            self.event[acc][action].append({
                'topic': action,
                'account_cookie': acc,
                'lastrequesttime': xtime
            })
            print(self.event)
            self.client.event.update_one({'starttime': self.starttime, 'account_cookie': acc}, {
                                         '$set': self.event[acc]}, upsert=True)
            if bankid:
                p.pub(json.dumps({
                    'topic': action,
                    'account_cookie': acc,
                    'bankid': bankid
                }), routing_key=acc)
            else:
                p.pub(json.dumps({
                    'topic': action,
                    'account_cookie': acc,
                }), routing_key=acc)
        elif action == 'change_password':
            newpw = self.get_argument('newpassword')
            accounttrade = self.get_argument('type')
            if accounttrade == 'real':
                p = producer.publisher_routing(user=trade_server_user, password=trade_server_password,
                                               host=trade_server_ip, exchange='QAORDER_ROUTER')
            else:
                p = producer.publisher_routing(user=trade_server_user, password=trade_server_password,
                                               host=simtrade_server_ip, exchange='QAORDER_ROUTER')

            p.pub(json.dumps({
                'topic': action,
                'newPass': newpw
            }), routing_key=acc)
            self.event[acc][action].append({
                'topic': action,
                'account_cookie': acc,
                'lastrequesttime': xtime,
                'newPass': newpw
            })
            self.client.event.update_one({'starttime': self.starttime, 'account_cookie': acc}, {
                                         '$set': self.event[acc]}, upsert=True)

        elif action == 'query_settlement':
            dates = self.get_argument('day')
            res = self.client.account.find_one({'account_cookie': acc}, {
                'settlement': 1, '_id': 0})['settlement']
            if dates in res.keys():
                self.write({
                    'status': 200,
                    'result': res[dates]
                })
            else:
                p = producer.publisher_routing(user=trade_server_user, password=trade_server_password,
                                               host=trade_server_ip, exchange='QAORDER_ROUTER')

                p.pub(json.dumps({
                    'topic': action,
                    'day': dates
                }), routing_key=acc)
                self.event[acc][action].append({
                    'topic': action,
                    'day': dates
                })
                self.client.event.update_one({'starttime': self.starttime, 'account_cookie': acc}, {
                    '$set': self.event[acc]}, upsert=True)
                time.sleep(2)
                res = self.client.account.find_one({'account_cookie': acc}, {
                    'settlement': 1, '_id': 0})['settlement']
                if dates in res.keys():
                    self.write({
                        'status': 200,
                        'result': res[dates]
                    })
                else:
                    self.write({
                        'status': 400,
                        'result': '尚未就绪'
                    })


def webserver():
    handlers = [(r'/tradeaccounts', TradeAccountHandler),
                (r'/order', SendOrderHandler)]

    apps = Application(
        handlers=handlers,
        debug=True,
        autoreload=True,
        compress_response=True
    )
    http_server = Server(apps)
    http_server.bind('8020', address='0.0.0.0')
    http_server.start(1)
    IOLoop.current().start()


if __name__ == "__main__":
    webserver()
