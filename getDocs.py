import sqlite3
import requests
from retry import retry
import hashlib
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

        # skipping already filled rows
        cursor.execute("SELECT * FROM tenders_2023 WHERE title is NULL;")
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
    logging.debug(f'Inserting data for tender id... {keyword}')
    title = data.get('title', None)
    print(title)
    logging.debug(title)

    date_mod = data.get('dateModified', None)
    print(date_mod)
    logging.debug(date_mod)

    procuring_entity = data.get('procuringEntity', {})

    name_buyer = procuring_entity.get('name', None)
    print(name_buyer)
    logging.debug(name_buyer)

    identifier = procuring_entity.get('identifier', {})

    code_buyer = identifier.get('id', None)
    print(code_buyer)
    logging.debug(code_buyer)

    address = procuring_entity.get('address', {})

    region = address.get('region', None)
    print(region)
    logging.debug(region)

    locality = address.get('locality', None)
    print(locality)
    logging.debug(locality)

    streetAddress = address.get('streetAddress', None)
    print(streetAddress)
    logging.debug(streetAddress)

    awards = data.get('awards', [])

    suppliers = awards[0]['suppliers'] if awards and 'suppliers' in awards[0] else []

    name_company = suppliers[0].get('name', None) if suppliers else None
    print(name_company)
    logging.debug(name_company)

    identifier_company = suppliers[0].get('identifier', {}) if suppliers else {}

    code_company = identifier_company.get('id', None)
    print(code_company)
    logging.debug(code_company)

    # Convert the set to a comma-separated string
    if match_keyword != 'none':
        keywords_str = ', '.join(match_keyword)
    else:
        keywords_str = match_keyword
    print(f'Keyword added: {keywords_str}')
    logging.debug(f'Keyword added: {keywords_str}')

    # Convert the set to a comma-separated string
    if match_files != 'none':
        filenames_str = ', '.join(match_files)
    else:
        filenames_str = match_files
    print(f'Filename added: {filenames_str}')
    logging.debug(f'Filename added: {filenames_str}')

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
              name_company, code_company, price, keywords_str, filenames_str, row))

        # Commit the changes to the database
        conn.commit()

        print("Data inserted successfully.")
        logging.debug("Data inserted successfully.")

    except sqlite3.Error as e:
        print(f"Error writing to db: {e}")
        logging.debug(f"Error writing to db: {e}")

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


def sanitize_file_name(file_name):
    # Replace invalid characters with underscores
    invalid_chars = r'\/:*?"<>|'
    sanitized_name = ''.join(c if c not in invalid_chars else '_' for c in file_name)
    return sanitized_name

def download_docs(documents_urls, id):
    folder_name = os.path.join(folder_path, id)
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    for doc_urls in documents_urls:
        for i in range(len(doc_urls['urls'])):
            title = doc_urls['title'][i]
            # Example: Truncate the file name to a maximum length of 100 characters
            truncated_name = title[:100]
            sanitized_title = sanitize_file_name(truncated_name)
            print(f"Title: {truncated_name}, URLs: {doc_urls['urls'][i]}")
            print("Download begin")

            try:
                # Check if the URL is not None
                if doc_urls['urls'][i] is not None:
                    response = requests.get(doc_urls['urls'][i])

                    if response.status_code == 200:
                        file_path = os.path.join(folder_name, sanitized_title)
                        with open(file_path, "wb") as file:
                            file.write(response.content)
                        print(f"File saved... {sanitized_title} saved to... {file_path}")

                        if file_path.endswith(".zip"):
                            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                                zip_ref.extractall(folder_name)
                            print(f"Extracted contents of {sanitized_title} to {folder_name}")
                    else:
                        print(f"Failed to download document {title}. Status code: {response.status_code}")
                else:
                    print(f"Skipping document {title} because the URL is None.")
            except Exception as e:
                print(f"Error downloading document {title}: {e}")

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
