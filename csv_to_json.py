import psycopg2
import json
import time
import re
from common_functions import *

import pandas as pd


class Client:

    def __init__(self):
        self.base_url = "/dl.acm.org"
        self.papers_dict = {}
        self.authors_set = {}
        self.intitution_set = {}
        self.dir = "data/jsons/"
        self.papers_path = "data/jsons/papers.json"
        self.real_authors_path = "data/jsons/authors.json"
        self.institution_path = "data/jsons/insti.json"

        # conexion con subset db
        #self.conn = self.connect_to_subset_db()
        #self.cursor = self.conn.cursor()
        self.dictcoautores = {}
        self.dict_papers_ref = {}
        self.cocitations = {}

        #cols
        self.papers_col = ['type', 'title', 'year', 'authors','citations', 'downloads', 'doi', 'publisher', "n_reference"]
        self.autors_col = ['name', 'url', 'institutions', 'countries', 'country']

    def load_data(self):
        with open(self.institution_path, encoding='utf-8') as fh:
            insti = json.load(fh)
        self.intitution_set = insti
        with open(self.real_authors_path, encoding='utf-8') as fh:
            autores = json.load(fh)
        self.authors_set = autores
        with open(self.papers_path, encoding='utf-8') as fh:
            papers = json.load(fh)
        self.papers_dict = papers

    def create_list(self):
        newlist = []
        for paper in self.papers_dict.values():
            autores = paper['authors']
            getnames = []
            for autor in autores:
                getnames.append(autor['name'])

            data = {
                'type': paper['type'],
                'title': paper['title'],
                'year':  paper['year'],
                'authors': getnames,
                'citations': paper['citations'],
                'downloads' : paper['downloads'],
                'doi': paper['doi'],
                'publisher': paper['publisher'],
                'n_reference': paper['n_reference']
            }
            newlist.append(data)
        return newlist

    def create_list_autors(self):
        newlist = []
        for autor in self.authors_set.values():
            print(autor)
            institutos = autor['institutions']
            getnames = []
            getcountries = []
            for insti in institutos:
                id = insti['id']
                if id != 'javascript:void(0)':
                    getnames.append(insti['name'])
                    institution_ob = self.intitution_set[id]
                    ad2 = institution_ob['ad2'] if 'ad2' in institution_ob else ''
                    ad1 = institution_ob['ad1'] if 'ad1' in institution_ob else ''
                    ad0 = institution_ob['ad0'] if 'ad0' in institution_ob else ''
                    if ad2 != '':
                        pais = ad2
                    elif ad1 != '':
                        pais =ad1
                    else : pais = ad0
                    getcountries.append(pais)

            if len(institutos) > 0:
                firstinst = institutos[0]
                idfirst = firstinst['id']
                insti = self.intitution_set[idfirst]
                ad2 = '' if 'ad2' not in insti else insti['ad2']
                ad1 = '' if 'ad1' not in insti else insti['ad1']
                ad0 = '' if 'ad0' not in insti else insti['ad0']
                pais = ad2 if ad2 != '' else (ad1 if ad1 != '' else ad0)
            else:
                getnames = ''
                getcountries = ''
                pais = ''

            data = {
                'name': autor['name'],
                'url': autor['url'],
                'institutions': getnames,
                'countries': getcountries,
                'country':  pais
            }
            newlist.append(data)

        print("fin")
        return newlist

    def make_csv_refs(self, list):
        csv_file = "data/papers.csv"
        csv_columns = self.papers_col
        with open(csv_file, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in list:
                writer.writerow(data)

    def make_csv_autors(self, list):
        csv_file = "data/authors.csv"
        csv_columns = self.autors_col
        with open(csv_file, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in list:
                writer.writerow(data)

    def papers_to_csv(self):
        list = self.create_list()
        print(list[0])
        self.make_csv_refs(list)

    def autors_to_csv(self):
        list = self.create_list_autors()
        print(list[0])
        self.make_csv_autors(list)

if __name__ == '__main__':
    client = Client()
    client.load_data()
    #client.papers_to_csv()
    client.autors_to_csv()
