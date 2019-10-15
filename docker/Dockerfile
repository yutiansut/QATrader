FROM daocloud.io/quantaxis/qawebserver:latest

RUN cd /root \
&& git clone https://github.com/yutiansut/QATrader \
&& pip install quantaxis -U \
&& pip install qaenv \
&& cd QATrader && pip install -e .

EXPOSE 8020
