from requests import get
from os import path, getcwd, makedirs
from bs4 import BeautifulSoup as soup
import csv
import json
import re
import json
import os
import logging

info = "https://www.codegrepper.com/code-examples/python/beautifulsoup+loop+through+child+elements"
infotext ="python bs4 get element and iterate subelements"

class dblpClient:
    def __init__(self):
        self.baseUrl = "https://dblp.org/db/conf/vinci/index.html"
        self.currentlink = ''

    def clear_page(self):
        clear = lambda: os.system('cls')
        clear()

    def get_page(self, url):
        req = get(url, verify=False)
        if req.status_code == 200:
            return req.text
        else:
            return None
        # raise Exception('Error {0}'.format(req.status_code))

    def get_all_links(self, html):
        bs = soup(html, 'html.parser')  # MISSING 'html.parser'
        mainpage = bs.find(id='main')
        uls = bs.find(id='main').findAll('ul',  {"class": "publ-list"})
        print(uls)
        logging.info('Uls: ' + str(uls))

        return uls

    def get_links_to_nav(self):
        html = self.get_page(self.baseUrl)
        links = self.get_all_links(html)
        return links

    def main_fun(self):
        links = self.get_links_to_nav()


if __name__ == '__main__':
  client = dblpClient()

  logging.basicConfig(filename='logs/vinci_log.log', filemode='w', level=logging.INFO, format='%(asctime)s %(message)s')
  logger = logging.getLogger('__FileServer__')
  logging.info('------------------------------------------------------------------------------------------')
  logging.info('')
  logging.info('')
  logging.info('Starting')
  logging.info('base_url: ' + client.baseUrl)


  client.main_fun()
