
#coding=gbk

import logging
from logging.handlers import RotatingFileHandler
from logging.handlers import TimedRotatingFileHandler
import time


class LogWrapper:
    format_str = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
    date_fmt_str = '%a, %d %b %Y %H:%M:%S'
    filename_str = 'log.txt'
    console = ()
    rt_handler = ()
    inited = False
    #####################################################
    # when 是一个字符串的定义如下：
    # “S”: Seconds
    # “M”: Minutes
    # “H”: Hours
    # “D”: Days
    # “W”: Week day (0=Monday)
    # “midnight”: Roll over at midnight
    #####################################################
    @staticmethod
    def init(log_name, when_r="D", interval_r=1, backup_count_r=5):
        if LogWrapper.inited is False:
            LogWrapper.filename_str = log_name
            logging.basicConfig(level=logging.DEBUG,
                                format=LogWrapper.format_str,
                                datefmt=LogWrapper.date_fmt_str,
                                filename=LogWrapper.filename_str,
                                filemode='a')

            LogWrapper.console = logging.StreamHandler()
            LogWrapper.console.setLevel(logging.DEBUG)
            formatter = logging.Formatter(LogWrapper.format_str, LogWrapper.date_fmt_str)
            LogWrapper.console.setFormatter(formatter)
            logging.getLogger('').addHandler(LogWrapper.console)

            LogWrapper.rt_handler = TimedRotatingFileHandler(LogWrapper.filename_str, when=when_r, interval=interval_r, backupCount=backup_count_r)
            LogWrapper.rt_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(LogWrapper.format_str, LogWrapper.date_fmt_str)
            LogWrapper.rt_handler.setFormatter(formatter)
            logging.getLogger('').addHandler(LogWrapper.rt_handler)
            logging.info('Log Wrapper inited , log path: %s status :%d',LogWrapper.filename_str,LogWrapper.inited)
            LogWrapper.inited = True
        else:
            logging.info('Log Wrapper already inited , log path: %s status :%d', LogWrapper.filename_str,LogWrapper.inited)

    @staticmethod
    def set_level(level):
        LogWrapper.console.setLevel(level)
        LogWrapper.rt_handler.setLevel(level)