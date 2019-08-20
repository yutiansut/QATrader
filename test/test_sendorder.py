from QAPUBSUB import producer
import json
import datetime

import click



def test_send_order(host='127.0.0.1'):
    p = producer.publisher_routing(
        user='admin', password='admin', host=host, exchange='QAORDER_ROUTER')

    price = {'rb1905': 4171}
    for acc in ['1010101']:
        for code in price.keys():
            p.pub(json.dumps({
                'topic': 'sendorder',
                'account_cookie': acc,
                'strategy_id': 'test',
                'code': code,
                'price': price[code],
                'order_direction': 'SELL',
                'order_offset': 'OPEN',
                'volume': 1,
                'order_time': str(datetime.datetime.now()),
                'exchange_id': 'SHFE'
            }), routing_key=acc)

if __name__ == "__main__":
    test_send_order()