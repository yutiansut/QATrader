import codecs
import io
import os
import re
import sys
import webbrowser
import platform

try:
    from setuptools import setup
except:
    from distutils.core import setup


NAME = "QATRADER"
"""
名字，一般放你包的名字即可
"""
PACKAGES = ["QATRADER"]
"""
包含的包，可以多个，这是一个列表
"""

DESCRIPTION = "QUANTAXIS TRADER"
KEYWORDS = ["quantaxis", "quant", "finance", "Backtest", 'Framework']
AUTHOR_EMAIL = "yutiansut@qq.com"
AUTHOR = 'yutiansut'
URL = "https://github.com/yutiansut/QATRADER"


LICENSE = "MIT"

setup(
    name=NAME,
    version='1.4',
    description=DESCRIPTION,
    long_description='trader',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    install_requires=['pika', 'quantaxis>=1.5.29', 'quantaxis_webserver',
                      'quantaxis_pubsub', 'quantaxis_otgbroker>=1.9.2', 'qaenv'],
    entry_points={
        'console_scripts': [
            'qatrader=QATRADER.__init__:single_trade',
            'qatraderserver=QATRADER.webhandler:webserver'
        ]
    },
    keywords=KEYWORDS,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license=LICENSE,
    packages=PACKAGES,
    include_package_data=True,
    zip_safe=True
)
