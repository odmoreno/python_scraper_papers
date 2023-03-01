from selenium import webdriver
from typing import List
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

from selenium.common.exceptions import NoSuchElementException


#from Levenshtein import ratio
from urllib.parse import quote
from bs4 import BeautifulSoup
from os import path, makedirs
from math import ceil
from operator import itemgetter
from string import ascii_letters
from sys import platform
import re
import subprocess
import csv
import config
import psycopg2
import json

# rutas de docs
institution_path = 'data/jsons/insti.json'
authors_path = 'data/jsons/authors.json'
papers_path = 'data/jsons/papers.json'
# rutas de keys
insti_keys_path = 'data/keys/insti_ids.json'
authors_keys_path = 'data/keys/authors_ids.json'
papers_keys_path = 'data/keys/papers_ids.json'
auth_insti_keys_path = 'data/keys/insti_authors_ids.json'


def make_chrome_headless(o=True):
    """
    Return a headless driver of Chrome
    """
    options = Options()
    if o:
        options.add_argument("--headless")
        options.add_argument("--disable-extensions")
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
    headless_driver = webdriver.Chrome(
        ChromeDriverManager().install(),
        options=options,
    )
    return headless_driver


def create_file(path_to_search_results, file_name) -> str:
    """
    Return file path
    """
    if not path.exists(path_to_search_results):
        makedirs(path_to_search_results)
    file_path = path.join(path_to_search_results, str(file_name + ".csv"))
    return file_path


def check_if_exist_file(path_to_search_results, file_name) -> bool:
    """
    Check if file exist
    """
    file_path = path.join(path_to_search_results, str(file_name + ".csv"))
    if not path.exists(file_path):
        return False
    return True

def check_if_exist_file_json(path_to_search_results, file_name, make=False) -> bool:
    """
    Check if json file exist
    """
    file_path = path.join(path_to_search_results, str(file_name + ".json"))
    if not path.exists(file_path):
        if make == True:
            # Creating a file at specified location
            with open(file_path, 'w') as fp:
                pass
        return False
    return True

def get_data_conferences():
    data = []
    with open('data/conferences.csv', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)
    return data

def fail_message(e):
    """
    Print failure message
    """
    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
    message = template.format(type(e).__name__, e.args)
    print(message)

def print_checking_all_results(sp):
    """
    IO: print status to show results are getting checked
    """
    print(
        "Checking all results where journal/conference name matches selected ones by "
        + str(sp)
        + chr(37)
    )

def connect_to_first_db():
    """
    Connect to papers_info db
    """
    conn = psycopg2.connect(
            host="200.10.150.106",
            database="papers_info",
            user="postgres",
            password="postgres")
    print("Opened database successfully")
    return conn

def connect_to_second_db():
    """
        Connect to subset db
    """
    conn = psycopg2.connect(
            host="200.10.150.106",
            database="subset",
            user="postgres",
            password="postgres")
    print("Opened database subset successfully")
    return conn

def load_institutions():
    with open(institution_path, encoding='utf-8') as fh:
        insti = json.load(fh)
    return insti

def load_authors():
    with open(authors_path, encoding='utf-8') as fh:
        authors = json.load(fh)
    return authors

def load_papers():
    with open(papers_path, encoding='utf-8') as fh:
        data = json.load(fh)
    return data

def count_table_inst(table, cursor):
    # query to count total number of rows
    sql = 'SELECT count(*) from ' + table
    data = []
    # execute the query
    cursor.execute(sql, data)
    results = cursor.fetchone()
    # loop to print all the fetched details
    for r in results:
        print(r)
    #print("Total number of rows in the table:", r)
    return r

def create_files_for_keys():
    check_if_exist_file_json('data/keys', 'insti_ids', True)
    check_if_exist_file_json('data/keys', 'authors_ids', True)
    check_if_exist_file_json('data/keys', 'insti_authors_ids', True)
    check_if_exist_file_json('data/keys', 'papers_ids', True)
    check_if_exist_file_json('data/keys', 'papers_authors_ids', True)
    check_if_exist_file_json('data/keys', 'papers_references_ids', True)

def load_inti_keys():
    with open(insti_keys_path, encoding='utf-8') as fh:
        data = json.load(fh)
    return data

def load_authors_keys():
    with open(authors_keys_path, encoding='utf-8') as fh:
        data = json.load(fh)
    return data

def load_papers_keys():
    with open(papers_keys_path, encoding='utf-8') as fh:
        data = json.load(fh)
    return data
def load_rel1_keys():
    with open(auth_insti_keys_path, encoding='utf-8') as fh:
        data = json.load(fh)
    return data

def save_ids(dict, path):
    json_string2 = json.dumps(dict, ensure_ascii=False, indent=2)
    with open(path, 'w', encoding="utf-8") as outfile:
        outfile.write(json_string2)

def create_headers(cols):
    headers = "("
    headers += ", ".join(cols)
    headers += ")"
    return headers

def create_s_values(tam):
    strings = ' VALUES ('
    for i in range(tam):
        if i == tam - 1:
            strings += '%s'
        else:
            strings += '%s,'
    strings += ')'
    return strings

def save_generic(path, collection):
    json_string = json.dumps(collection, ensure_ascii=False, indent=2)
    with open(path, 'w', encoding="utf-8") as outfile:
        outfile.write(json_string)

def load_generic( path):
    with open(path, encoding='utf-8') as fh:
        elements = json.load(fh)
    return elements

def csv_generics(path, list, cols):
        csv_file = path
        csv_columns = cols
        with open(csv_file, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in list:
                #print(data)
                writer.writerow(data)

def load_csv_generic(path):
    with open(path, 'r') as file:
        csvreader = csv.reader(file)
        return csvreader

# result CSV file's header
header = [
    "URL",
    "Title",
    "Author(s)",
    "Year",
    "Journal",
    "Matched with Selected Journal/Conference",
    "Similarity %",
    "Database",
    "Query",
]
