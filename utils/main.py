from datetime import datetime

from dateutil.relativedelta import relativedelta


def change_date_by_day(date_str, days_to_add):
    date = datetime.strptime(str(date_str).split(' ')[0], '%Y-%m-%d')
    new_date = date + relativedelta(days=days_to_add)
    return new_date


def answer_deadline_filter(query, respones):
    num, timedwm = query
    num = int(num)
    days_utill_dd = num if timedwm == 'd' else num * 7 if timedwm == 'w' else num * 30
    new_events = {}
    now = datetime.now()
    current_date = datetime(now.year, now.month, now.day)

    for item in respones:
        eventtime = datetime(*map(int, respones[item].get('date').split('-')))
        if current_date <= eventtime < change_date_by_day(now, days_utill_dd):
            new_events[item] = respones[item].get("fulldatestr")
    return new_events

def test_function(new_events):
    lst = []
    for i in new_events:
        lst.append(i + '\n' + new_events[i])
    return lst


if __name__ == '__main__':
    pass
