from QATRADER.trader import QA_TRADER
import click


@click.command()
@click.option('--acc', default='133496', help='account name')
@click.option('--pwd', default='QCHL1234')
@click.option('--wsuri', default='ws://www.yutiansut.com:7988')
@click.option('--broker', default='simnow')
@click.option('--trade_host', default='127.0.0.1')
@click.option('--pub_host', default='127.0.0.1')
@click.option('--ping_gap', default=5)
@click.option('--taskid', default=None)
@click.option('--portfolio', default='default')
@click.option('--bank_password', default=None)
@click.option('--capital_password', default=None)
@click.option('--appid', default=None)
def single_trade(acc, pwd, wsuri, broker, trade_host, pub_host, ping_gap, taskid, portfolio, bank_password, capital_password, appid):
    QA_TRADER(str(acc), str(pwd), wsuri=wsuri, trade_host=trade_host, pub_host=pub_host, portfolio=portfolio, bank_password=bank_password, capital_password=capital_password,
                  appid=appid, broker_name=broker, ping_gap=ping_gap, taskid=taskid).start()

