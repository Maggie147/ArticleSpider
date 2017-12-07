# -*- coding: utf-8 -*-
import time
from datetime import datetime

def format_date(value):
    if not value:
        return None
    try:
        timesp = time.strptime(value, "%m/%d/%y")
        print timesp
        timesf = time.strftime("%Y-%m-%d", timesp)
        print timesf
        return timesf
    except:
        timesf = time.strftime("%Y-%m-%d", time.localtime())
        return timesf


def test():
    time_tmp = "10/02/17"
    time_f = format_date(time_tmp)
    print time_f

if __name__ == '__main__':
    test()