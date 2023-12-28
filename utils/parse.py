import functools
import json
import sqlite3
import time
from datetime import datetime, timezone

import requests
from correction_dates import check_deadline, correct_dates

Mistake = 'Что-то пошло не так! Попробуйте ввести токен заново!'


def cache_with_timeout(func):
    cache = {}
    last_called = {}

    @functools.wraps(func)
    def wrapper(userID, *args, **kwargs):
        current_time = time.time()
        if userID in last_called and current_time - last_called[userID] < 1 and cache[userID] != Mistake:
            return cache[userID]
        else:
            result = func(userID, *args, **kwargs)
            cache[userID] = result
            last_called[userID] = current_time
            return result

    return wrapper


@cache_with_timeout
def get_pages_parsing(userID):
    conn = sqlite3.connect("../data/tokens.sql")
    cursor = conn.cursor()

    userid = userID
    cursor.execute('SELECT DBToken, NotionToken FROM tokens_tbl WHERE userid = ?', (userid,))

    result = cursor.fetchone()
    if result:
        DATABASE_ID = result[0]
        NOTION_TOKEN = result[1]

    cursor.close()
    conn.close()
    headers = {
        "Authorization": "Bearer " + NOTION_TOKEN,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    print(result, 'get_pages_parsing')
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {"page_size": 100}
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    results = data.get("results")
    if data.get('object') == "error":
        return Mistake

    return results


def get_data_from_json(UserID):
    respones = get_pages_parsing(UserID)
    if respones == Mistake:
        return Mistake
    dict_all_events = dict()
    for event in respones:
        try:
            properties = event.get('properties')
            date = properties.get('Date').get('date').get('start')
            content = properties.get('Name').get('title')[0].get('text').get('content')
            deadline = {}
            deadline['fulldatestr'] = correct_dates(date)
            deadline['date'] = date[:10]
            dict_all_events[content] = deadline
        except (AttributeError, IndexError):
            pass
    return dict_all_events


def get_data_from_json_for_calendar(UserID, responsedate):
    respones = get_data_from_json(UserID)
    dict_all_events = dict()
    for name in respones:
        if respones[name].get('date') in responsedate:
            dict_all_events[name] = respones[name].get('fulldatestr')
    return dict_all_events


def connectin_check_time(userID):
    return get_data_from_json(str(userID))


def create_page(title, userID, date_of_event):
    conn = sqlite3.connect("../data/tokens.sql")
    cursor = conn.cursor()

    userid = userID
    cursor.execute('SELECT DBToken, NotionToken FROM tokens_tbl WHERE userid = ?', (userid,))

    result = cursor.fetchone()
    if result:
        DATABASE_ID = result[0]
        NOTION_TOKEN = result[1]

    cursor.close()
    conn.close()
    published_date = datetime.now().astimezone(timezone.utc).isoformat()
    date_of_event += 'T18:00:00.905826+00:00'
    headers = {
        "Authorization": "Bearer " + NOTION_TOKEN,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    data = {
        "Name": {"title": [{"text": {"content": title}}]},
        "Date": {"date": {"start": date_of_event, "end": None}}
    }
    create_url = "https://api.notion.com/v1/pages"

    payload = {"parent": {"database_id": DATABASE_ID}, "properties": data}

    res = requests.post(create_url, headers=headers, json=payload)
    return res

def delete_page(page_id: str, userID):
    conn = sqlite3.connect("../data/tokens.sql")
    cursor = conn.cursor()

    userid = userID
    cursor.execute('SELECT DBToken, NotionToken FROM tokens_tbl WHERE userid = ?', (userid,))

    result = cursor.fetchone()
    if result:
        NOTION_TOKEN = result[1]

    cursor.close()
    conn.close()
    headers = {
        "Authorization": "Bearer " + NOTION_TOKEN,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    url = f"https://api.notion.com/v1/pages/{page_id}"

    payload = {"archived": True}

    res = requests.patch(url, json=payload, headers=headers)
    return res

if __name__ == '__main__':
    pass
