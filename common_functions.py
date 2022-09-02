from selenium import webdriver
from typing import List
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from Levenshtein import ratio
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

def check_if_exist_file_json(path_to_search_results, file_name) -> bool:
    """
    Check if file exist
    """
    file_path = path.join(path_to_search_results, str(file_name + ".json"))
    if not path.exists(file_path):
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
