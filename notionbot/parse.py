import json
import time

import requests
from config import NOTION_TOKEN, DATABASE_ID, headers, filename2, filename1, filename3
from utils.correction_dates import check_deadline, correct_dates, time_from_last_response
from datetime import datetime


def get_pages_parsing(filename, num_pages=None, ):
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()
    with open(f'{filename}.json', 'w') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    results = data.get("results")
    # while data["has_more"] and get_all:
    #     payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
    #     url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    #     response = requests.post(url, json=payload, headers=headers)
    #     data = response.json()
    #     results.extend(data["results"])

    return results


def get_data_from_json(filename):
    with open(f'{filename}.json') as file:
        respones = json.load(file).get("results")
    dict_all_events = dict()

    for event in respones:
        properties = event.get('properties')
        date = properties.get('Date').get('date').get('start')
        content = properties.get('Name').get('title')[0].get('text').get('content')
        deadline = check_deadline(date)
        if deadline:
            deadline['fulldatestr'] = correct_dates(date)
            dict_all_events[content] = deadline
    with open('data/processed_parse2.json', 'w') as file:
        json.dump(dict_all_events, file, ensure_ascii=False, indent=4)
    return dict_all_events


def connectin_check_time(userID, filename=filename3, waiting_time_seconds=20):
    userID = str(userID)
    with open(f'{filename}.json') as file:
        respones = json.load(file)
    if str(userID) in respones.keys():
        user_time_resp = time_from_last_response(respones[userID])
    respones[userID] = str(datetime.now())
    with open(f'{filename}.json', 'w') as file:
        json.dump(respones, file)
    if str(userID) in respones.keys():
        print('user_time_resp = ', user_time_resp)
        if user_time_resp < waiting_time_seconds:
            time.sleep(waiting_time_seconds - user_time_resp + 1)

    get_pages_parsing(filename1)
    get_data_from_json(filename1)


if __name__ == '__main__':
    # get_pages_parsing()
    get_data_from_json(filename1)
    pass
