import json
from config import filename2


def answer_deadline_filter(query, filename):
    num, timedwm = query
    num = int(num)
    days_utill_dd = num if timedwm == 'd' else num * 7 if timedwm == 'w' else num * 30
    with open(f'{filename}.json') as file:
        respones = json.load(file)
    new_events = {}
    for item in respones:
        if respones[item].get('days') <= days_utill_dd:
            new_events[item] = respones[item].get("fulldatestr")

    return new_events


def test_function(new_events):
    lst = []
    for i in new_events:
        lst.append(i + '\n' + new_events[i])
    return lst


if __name__ == '__main__':
    answer_deadline_filter('1w', filename=filename2)
