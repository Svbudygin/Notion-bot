import re
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


def time_from_last_response(currenttime):
    event_time = re.split('-|:|T|\s', currenttime)[:5]
    now = datetime.now()
    response_time = datetime(*map(int, event_time))
    period = now - response_time
    return period.total_seconds()


if __name__ == '__main__':
    pass
