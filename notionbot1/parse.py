import functools
import json
import sqlite3
import time
from datetime import datetime

import requests
from utils.correction_dates import check_deadline, correct_dates

Mistake = 'Что-то пошло не так! Попробуйте ввести токен заново!'


def cache_with_timeout(func):
    cache = {}
    last_called = {}

    @functools.wraps(func)
    def wrapper(userID, *args, **kwargs):
        current_time = time.time()
        if userID in last_called and current_time - last_called[userID] < 1:
            return cache[userID]
        else:
            result = func(userID, *args, **kwargs)
            cache[userID] = result
            last_called[userID] = current_time
            return result

    return wrapper


@cache_with_timeout
def get_pages_parsing(userID, filename):
    # with open('data/all_tokens.json') as file:
    #     alltokens = json.load(file).get(userID)
    #     DATABASE_ID = alltokens.get('DBToken')
    #     NOTION_TOKEN = alltokens.get('NotionToken')
    conn = sqlite3.connect("data/tokens.sql")
    cursor = conn.cursor()

    userid = userID
    cursor.execute('SELECT DBToken, NotionToken FROM tokens_tbl WHERE userid=?', (userid,))
    result = cursor.fetchone()
    if result:
        DATABASE_ID = result[0]
        NOTION_TOKEN = result[1]

    cursor.close()
    conn.close()
    print(result)
    headers = {
        "Authorization": "Bearer " + NOTION_TOKEN,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {"page_size": 100}
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    with open(f'{filename}.json', 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    results = data.get("results")
    if data.get('object') == "error":
        return Mistake
    return results



def get_data_from_json(UserID, filename):
    respones = get_pages_parsing(UserID, filename)
    if respones == Mistake:
        return Mistake
    # with open(f'{filename}.json') as file:
    #     respones = json.load(file).get("results")
    dict_all_events = dict()
    print(respones)
    for event in respones:
        try:
            properties = event.get('properties')
            date = properties.get('Date').get('date').get('start')
            content = properties.get('Name').get('title')[0].get('text').get('content')
            deadline = check_deadline(date)
            if deadline:
                deadline['fulldatestr'] = correct_dates(date)
                deadline['date'] = date[:10]
                dict_all_events[content] = deadline
        except (AttributeError, IndexError):
            pass
    with open(f'data/events/{UserID}processed_parse2.json', 'w') as file:
        json.dump(dict_all_events, file, ensure_ascii=False, indent=4)
    return dict_all_events


def get_data_from_json_for_calendar(UserID, responsedate):
    with open(f'data/events/{UserID}processed_parse2.json') as file:
        respones = json.load(file)
    dict_all_events = dict()
    for name in respones:
        if respones[name].get('date') in responsedate:
            dict_all_events[name] = respones[name].get('fulldatestr')
    return dict_all_events


def connectin_check_time(userID):
    # get_pages_parsing(str(userID), 'data/parse1')
    if get_data_from_json(str(userID), 'data/parse1') == Mistake:
        return False
    return True


if __name__ == '__main__':
    pass
