from QATRADER.trader import QA_TRADER
from qaenv import eventmq_ip, mongo_ip
import click


@click.command()
@click.option('--acc', default='133496', help='account name')
@click.option('--pwd', default='QCHL1234')
@click.option('--wsuri', default='ws://www.yutiansut.com:7988')
@click.option('--broker', default='simnow')
@click.option('--eventmq_ip', default=eventmq_ip)
@click.option('--database_ip', default=mongo_ip)
@click.option('--ping_gap', default=5)
@click.option('--taskid', default=None)
@click.option('--portfolio', default='default')
@click.option('--bank_password', default=None)
@click.option('--capital_password', default=None)
@click.option('--appid', default=None)
def single_trade(acc, pwd, wsuri, broker, eventmq_ip, database_ip, ping_gap, taskid, portfolio, bank_password, capital_password, appid):
    #print(database_ip)
    QA_TRADER(str(acc), str(pwd), wsuri=wsuri, eventmq_ip=eventmq_ip, database_ip=database_ip, portfolio=portfolio, bank_password=bank_password, capital_password=capital_password,
                  appid=appid, broker_name=broker, ping_gap=ping_gap, taskid=taskid).start()

