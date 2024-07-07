import os
import json
import math
import pandas as pd
import csv
from urllib.parse import urlparse, parse_qsl, urlunparse

csv.field_size_limit(100000000)
INPUT_DIR = "captures/csv-captures/catwatch"
OUTPUT_FILE = 'collections/catwatch/collection.json'
COLLECTION_NAME = 'CONVERTED_catwatch_TEST'
PORT = 38888

def create_df(dir):
    dfs = []
    for filename in os.listdir(dir):
        if filename.endswith(".csv"): 
            file_path = os.path.join(dir, filename)
            df = pd.read_csv(file_path, sep='|', engine='python')
            dfs.append(df)

    combined_df = pd.concat(dfs, ignore_index=True)
    combined_df.columns = ['method', 'uri', 'user_agent', 'accept', 'authorization', 'payload']
    return combined_df

def init_postman_collection(name):
    collection = {
        "info": {
            "_postman_id": "9a707ca6-ee81-413c-a9d4-f81020284c84",
            "name": name,
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            "_exporter_id": "33435539"
        },
        "item": []
    }
    return collection

def parse_url(raw_url):
    parsed_url = urlparse(raw_url)
    query = parse_qsl(parsed_url.query)
    return {
        "raw": raw_url,
        "protocol": parsed_url.scheme,
        "host": [parsed_url.hostname],
        "port": parsed_url.port,
        "path": parsed_url.path.split('/')[1:] if parsed_url.path.split('/')[1:][-1] else parsed_url.path.split('/')[1:-1],
        "query": [{"key": k, "value": v} for k, v in query]
    }

def create_body(payload):
    body = {
        'mode': 'raw',
        'raw': payload,
        "options": {
            "raw": {
              "language": "json"
            }
        }
    }
    return body

def change_port(uri, new_port):
    parsed = urlparse(uri)
    new_netloc = f"{parsed.hostname}:{new_port}"
    new_uri = urlunparse(parsed._replace(netloc=new_netloc))
    return new_uri

def create_headers(row):
    headers = []
    if not pd.isna(row['user_agent']):
        headers.append({"key": "User-Agent", "value": row['user_agent']})
    if not pd.isna(row['accept']):
        headers.append({"key": "Accept", "value": row['accept']})
    if not pd.isna(row['authorization']):
        headers.append({"key": "Authorization", "value": row['authorization']})
    return headers

def create_item(method, header, url, response, payload):
    item = {
        'name': 'New Request',
        'request': {
            'method': method,
            'header': header,
            'url': url
        },
        'response': response 
    }
    if isinstance(payload, float) and math.isnan(payload):
        return item
    body = create_body(payload)
    item['request']['body'] = body
    return item

def create_items(df, items):
    for index, row in df.iterrows():
        method = row['method']
        raw_url = row['uri']
        payload = row['payload']
        url = change_port(raw_url, PORT)
        url = parse_url(url)
        header = create_headers(row)
        response = []
        payload = row['payload']

        item = create_item(method, header, url, response, payload)
        items.append(item)

def save(filename, collection):
    with open(filename, 'w') as f:
        json.dump(collection, f, indent=2)

df = create_df(INPUT_DIR)
collection = init_postman_collection(COLLECTION_NAME)
create_items(df, collection['item'])

save(OUTPUT_FILE, collection)
