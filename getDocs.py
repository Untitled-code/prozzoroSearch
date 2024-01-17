#!/home/investigator/PycharmProjects/parsing_mistoDlaLudey_project/venv/bin/python
# prozorro parser with API

import requests
from retry import retry
import time
import sys
import logging, json
from pathlib import Path
import csv
import os
import json
import zipfile


logging.basicConfig(filename='getDocs.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug('Start of program')
QUERY_LIST_FILE = ('keyword_list_tendersID.csv')
BASE_LINK = 'https://public.api.openprocurement.org/api/2.5/tenders/'
# get data from csv files


def get_keywords(list_file):
    with open(list_file, 'r') as i_file:
        rows = csv.reader(i_file, delimiter=',')
        keywords = [row[0] for row in rows]
        return keywords


@retry(Exception, delay=15, backoff=1.2, max_delay=600)
def request(id):
    print('______________')
    print(f"Checking tender # {id}")
    response = requests.get(f'{BASE_LINK}{id}')
    response.raise_for_status()
    # Load JSON data info
    resultDict = json.loads(response.text)
    data = resultDict['data']
    if data:  # check if resultDict has values
        tender_title = data['title']
        tender_url = 'https://www.prozorro.gov.ua/tender/' + data['tenderID']  # url of tender
        print(data['title'])
        print(data['dateModified'])
        print(data['id'])
        print(data['value'])
        print(data['procuringEntity'])
    # saving json file to test it
    # with open("test_tender2.json", 'w') as file:
    #     json.dump(data, file, indent=2)
    return data


def extract_document_urls(data, current_path="", document_urls=[]):
    if isinstance(data, dict):
        for key, value in data.items():
            new_path = f"{current_path}.{key}" if current_path else key
            # print(f"if...{new_path}")
            if key == "documents":
                title_doc = [doc.get("title") for doc in value]
                print(title_doc)
                document_urls.append({"title": [doc.get("title") for doc in value],
                                      "urls": [doc.get("url") for doc in value]})
            extract_document_urls(value, new_path, document_urls)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            new_path = f"{current_path}[{i}]"
            extract_document_urls(item, new_path, document_urls)


def download_docs(documents_urls, id):
    folder_name = os.path.join(folder_path, id)
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    for doc_urls in documents_urls:
        for i in range(len(doc_urls['urls'])):
            print(f"Title: {doc_urls['title'][i]}, URLs: {doc_urls['urls'][i]}")
            print("Download begin")
            response = requests.get(doc_urls['urls'][i])

            if response.status_code == 200:
                file_path = os.path.join(folder_name, doc_urls['title'][i])
                with open(file_path, "wb") as file:
                    file.write(response.content)
                print(f"File saved... {doc_urls['title'][i]} saved to... {file_path}")

                if file_path.endswith(".zip"):
                    extract_folder = os.path.join(folder_name, "extracted")
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_folder)

                    print(f"Extracted contents of {doc_urls['title'][i]} to {extract_folder}")
            else:
                print(f"Failed to download document {doc_urls['title'][i]}. Status code: {response.status_code}")


#####################################

keywords = get_keywords(QUERY_LIST_FILE)

for keyword in keywords:
    json_data = request(keyword)
    print(f'Data of tender with title {json_data["title"]} is retrieved')
    folder_path = "./tenders/"  # Replace with your desired folder path
    # download_and_extract_documents(json_data, folder_path, keyword)
    document_urls = []
    # Call the function without passing 'urls' as a keyword argument
    extract_document_urls(json_data, document_urls=document_urls)
    download_docs(document_urls, keyword)

print("_______________Done!_______________")
logging.debug("________________Done!________________")
