from requests import get
from os import path, getcwd, makedirs
from bs4 import BeautifulSoup as soup
from pybtex.database.input import bibtex

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
        self.editors = {}
        self.conference_papers = {}
        self.currentYear = ''
        self.currentEditor = ''

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
        links = bs.find(id='main').findAll('a', {"class": "toc-link"})
        return links

    def otherf(self, html):
        bs = soup(html, 'html.parser')  # MISSING 'html.parser'
        uls = bs.find(id='main').findAll('ul', {"class": "publ-list"})

        for ul in uls:
            # child = ul.findChildren("span", recursive=False)
            # print(child)
            span = ul.findAll('span')
            authors = ul.findAll(attrs={"itemprop": "author"})
            for author in authors:
                value = author.text

        logging.info('Uls: ' + str(uls))
        return uls

    def get_links_to_nav(self):
        html = self.get_page(self.baseUrl)
        links = self.get_all_links(html)
        return links

    def bibtextparser(self, url):
        parser = bibtex.Parser()
        bib_data = parser.parse_file(url)
        bib_data.entries.keys()
        print(bib_data)

    def findbibtext(self, entry):
        publ = entry.find('nav', {'class': 'publ'})
        publ_lis = publ.next_element
        second_li = publ_lis.contents[1]
        bibtext = second_li.contents[0]
        bibtextlink = bibtext.find('a').attrs['href']
        self.findbibtextlink(bibtextlink)

    def findbibtextlink(self, link):
        html = self.get_page(link)
        bs = soup(html, 'html.parser')
        bibtetx_element = bs.find(id='bibtex-section')
        ptag = bibtetx_element.previousSibling
        aref = ptag.contents[0].attrs['href']
        response = get(aref)
        #open("instagram.ico", "wb").write(response.content)
        pass

    def get_info_conference_year(self, link):
        html = self.get_page(link)
        bs = soup(html, 'html.parser')
        uls = bs.find(id='main').findAll('ul', {"class": "publ-list"})
        tam = len(uls)
        for ul in uls:
            lis = ul.findAll('li', {"class": "entry editor"})
            lispubs = ul.findAll('li', {"class": "entry inproceedings"})

            self.extractInfoLis(lis, mode = 1)
            self.extractInfoLis(lispubs, mode = 2)

    def extractInfoLis(self, entryeditors, mode):
        for entry in entryeditors:
            id = entry.attrs['id']
            box = entry.find('div', {'class': 'box'})
            box_title = box.find('img').attrs['title']
            cite = entry.find('cite', {'class': 'data tts-content'})

            authors = cite.findAll(attrs={"itemprop": "author"})
            title = cite.find('span', {'class': 'title'}).text
            publisher = cite.find(attrs={"itemprop": "publisher"})
            datepublished = cite.find(attrs={"itemprop": "datePublished"})
            isbn = cite.find(attrs={"itemprop": "isbn"})
            pagination = cite.find(attrs={"itemprop": "pagination"})
            autores = []
            for author in authors:
                autores.append(author.text)

            isbn = '' if isbn is None else isbn.text
            publisher = '' if publisher is None else publisher.text
            pagination = '' if pagination is None else pagination.text

            if mode == 1:

                if datepublished.text == '':
                    idsplit = id.split('/')
                    datepublished = idsplit[len(idsplit)-1]
                else:
                    datepublished = datepublished.text

                idsplit = id.split('/')
                newid = 'vinci_'+ idsplit[len(idsplit)-1]
                data = {
                    'id': 'vinci_'+ idsplit[len(idsplit)-1],
                    'type': box_title,
                    'authors': autores,
                    'editors': autores,
                    'title': title,
                    'publisher': publisher,
                    'year': datepublished,
                    'isbn': isbn
                }
                self.currentYear = data['year']
                self.currentEditor = data['id']
                self.editors[newid] = data
            else:
                idsplit = id.split('/')
                newid = idsplit[len(idsplit)-1]
                stripped_string = title.strip('"')

                data2 = {
                    'id': idsplit[len(idsplit)-1],
                    'type': box_title,
                    'authors': autores,
                    'title': stripped_string,
                    'year': datepublished.attrs['content'],
                    'pagination': pagination,
                    'conference': self.currentEditor
                }
                self.conference_papers[newid] = data2
            pass



    def save_as_json(self):
        json_string = json.dumps(self.conference_papers, indent=2)
        # Using a JSON string
        with open('data/vinci_papers.json', 'w') as outfile:
            outfile.write(json_string)
        pass

    def save_as_csv(self):
        csv_file = "data/vinci_papers.csv"
        csv_columns = ['id', 'type', 'title', 'year', 'pagination', 'conference']
        list = self.conference_papers.values()
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in list:
                del data['authors']
                data['title'] = data['title'].replace('"', '')
                writer.writerow(data)

        csv_file = "data/vinci_conferences.csv"
        csv_columns = ['id', 'type', 'title', 'publisher', 'year', 'isbn']
        list = self.editors.values()
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in list:
                del data['authors']
                del data['editors']
                del data['papers']
                writer.writerow(data)



    def main_fun(self):
        links = self.get_links_to_nav()
        for link in links:
            href = link.attrs['href']
            self.get_info_conference_year(href)
            listOfKeys = [key for (key, value) in self.conference_papers.items() if value['year'] == self.currentYear]
            self.editors[self.currentEditor]['papers'] = listOfKeys
            pass

        print(self.editors)
        print(self.conference_papers)
        #self.save_as_csv()
        self.save_as_json()




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
