import re
from time import time
from datetime import datetime


def correct_dates(date):
    try:
        execttime = re.split('T|\.', date)[1][:-3] + ' '
    except IndexError:
        execttime = ''
    deadline = datetime(*map(int, re.split('-|:|T', date)[:5]))
    return f"{execttime}{deadline.strftime('%d %B %Y (%A)')}"


def check_deadline(currenttime):
    event_time = re.split('-|:|T', currenttime)[:5]
    now = datetime.now()
    deadline = datetime(*map(int, event_time))
    if now > deadline:
        return None
    else:
        period = deadline - now
        return {'days': period.days, 'seconds': period.seconds}


if __name__ == '__main__':
    x = check_deadline("2023-12-27T21:00:00.000+03:00")
    print(x)
