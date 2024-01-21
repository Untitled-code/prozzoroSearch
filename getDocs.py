import sqlite3
import requests
from retry import retry
import time
import sys
import logging, json
import csv
import os
import json
import zipfile
from find_matches import check_files

logging.basicConfig(filename='getDocs.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug('Start of program')


def read_from_table(db):
    tenders_id = []
    conn = sqlite3.connect(db)  # Replace with your database name
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT prozorro_id FROM tenders_2023")
        rows = cursor.fetchall()

        for row in rows:
            print(row)
            tenders_id.append(row[0])

    except sqlite3.Error as e:
        print(f"Error: {e}")

    finally:
        cursor.close()
        conn.close()

    print(f"Tenders: {tenders_id}")
    return tenders_id


@retry(Exception, delay=15, backoff=1.2, max_delay=600)
def request(id):
    print('______________')
    print(f"Checking tender # {id}")
    response = requests.get(f'{BASE_LINK}{id}')
    response.raise_for_status()
    # Load JSON data info
    resultDict = json.loads(response.text)
    if resultDict:
        data = resultDict['data']
        return data


def write_to_table(data, match_keyword, match_files, row):
    title = data.get('title', None)
    print(title)

    date_mod = data.get('dateModified', None)
    print(date_mod)

    procuring_entity = data.get('procuringEntity', {})

    name_buyer = procuring_entity.get('name', None)
    print(name_buyer)

    identifier = procuring_entity.get('identifier', {})

    code_buyer = identifier.get('id', None)
    print(code_buyer)

    address = procuring_entity.get('address', {})

    region = address.get('region', None)
    print(region)

    locality = address.get('locality', None)
    print(locality)

    streetAddress = address.get('streetAddress', None)
    print(streetAddress)

    awards = data.get('awards', [])

    suppliers = awards[0]['suppliers'] if awards and 'suppliers' in awards[0] else []

    name_company = suppliers[0].get('name', None) if suppliers else None
    print(name_company)

    identifier_company = suppliers[0].get('identifier', {}) if suppliers else {}

    code_company = identifier_company.get('id', None)
    print(code_company)

    print(match_keyword)
    print(match_files)

    contracts = data.get('contracts', [])

    value = contracts[0]['value'] if contracts else {}

    price = value.get('amount', None)
    print(price)

    # Connect to the SQLite database (creates a new database if it doesn't exist)
    conn = sqlite3.connect(db)

    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE tenders_2023
            SET date_mod=?, title=?, name_buyer=?, code_buyer=?, region=?, locality=?, 
                streetAddress=?, name_company=?, code_company=?, price=?, keyword=?, docs=?
            WHERE prozorro_id=?
        ''', (date_mod, title, name_buyer, code_buyer, region, locality, streetAddress,
              name_company, code_company, price, match_keyword, match_files, row))

        # Commit the changes to the database
        conn.commit()

        print("Data inserted successfully.")

    except sqlite3.Error as e:
        print(f"Error: {e}")

    finally:
        # Close the cursor and connection
        cursor.close()
        conn.close()


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
                    # extract_folder = os.path.join(folder_name, "extracted")
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(folder_name)

                    print(f"Extracted contents of {doc_urls['title'][i]} to {folder_name}")
            else:
                print(f"Failed to download document {doc_urls['title'][i]}. Status code: {response.status_code}")

    return folder_name


#####################################

if __name__ == "__main__":
    db = 'database.db'
    BASE_LINK = 'https://public.api.openprocurement.org/api/2.5/tenders/'
    keywords = read_from_table(db)

    for keyword in keywords:
        json_data = request(keyword)
        print(f'Data of tender with title {json_data["title"]} is retrieved')
        folder_path = "./tenders/"
        document_urls = []

        # Call the function without passing 'urls' as a keyword argument
        extract_document_urls(json_data, document_urls=document_urls)
        folder = download_docs(document_urls, keyword)
        match_keyword, match_files = check_files(folder)
        write_to_table(json_data, match_keyword, match_files, keyword)

    print("_______________Done!_______________")
    logging.debug("________________Done!________________")
