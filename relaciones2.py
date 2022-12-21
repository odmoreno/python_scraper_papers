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
        self.dir = "data/jsons/"
        self.papers_path = "data/jsons/papers.json"
        self.real_authors_path = "data/jsons/authors.json"
        self.institution_path = "data/jsons/insti.json"
        self.intitution_set = {}
        # conexion con subset db
        self.conn = self.connect_to_subset_db()
        self.cursor = self.conn.cursor()
        self.dictcoautores = {}
        self.dict_papers_ref = {}
        self.cocitations = {}
        self.list_papers_ref = []

    def connect_to_subset_db(self):
        conn = psycopg2.connect(
            host="200.10.150.106",
            database="subset",
            user="postgres",
            password="postgres")
        print("Opened Subset DB successfully")
        return conn

    def load_data(self):
        dict_from_csv = {}
        with open('data/papers_refences_table.csv', mode='r') as inp:
            reader = csv.reader(inp)
            dict_from_csv = {rows[0]: {'paper_id': rows[1], 'parent_id': rows[2]} for rows in reader}

        print(dict_from_csv)
        self.dict_papers_ref = dict_from_csv

    def get_paper_db(self, id):
        querystring = "SELECT * FROM papers"
        querystring += " WHERE id=" + str(id)
        try:
            self.cursor.execute(querystring)
            paper_records = self.cursor.fetchall()
            if len(paper_records) > 0:
                #print("search", paper_records[0])
                return paper_records[0]

        except Exception as e:
            print(id)
            print(querystring)
            fail_message(e)


    def get_authors_papers_db(self, id):
        set_authors = {}
        querystring = "SELECT * FROM papers_authors as o"
        querystring += " where o.papers_id =" + str(id)
        try:
            self.cursor.execute(querystring)
            records = self.cursor.fetchall()
            if len(records) > 0:
                list  =[]
                for record in records:
                    author_id = record[2]
                    author = self.get_authors_db(author_id)
                    list.append(author)
                return list
            else:
                return []
        except Exception as e:
            print(id)
            print(querystring)
            fail_message(e)

    def get_authors_db(self, id):
        querystring = "SELECT * FROM authors"
        querystring += " WHERE id=" + str(id)
        self.cursor.execute(querystring)
        paper_records = self.cursor.fetchall()
        if len(paper_records) > 0:
            #print("search", paper_records[0])
            return paper_records[0]


    def loop_ref(self):
        self.load_data()
        for references in self.dict_papers_ref.values():
            paper_id = references['paper_id']
            parent_id = references['parent_id']
            list1 = self.get_authors_papers_db(paper_id)
            list2 = self.get_authors_papers_db(parent_id)
            paper_row = self.get_paper_db(paper_id)
            parent_row = self.get_paper_db(parent_id)
            selfcitationPapers = False
            if len(list1) != 0 and len(list2) !=0:
                print("matches")
                for author in list1:
                    for author2 in list2:
                        #if author[0] != author2[0]:
                            id = str(author[0]) + ':' + str(author2[0]) + ':' + (paper_id) + ':' + (parent_id)
                            id_2 = str(author2[0]) + ':' + str(author[0]) + ':' + (paper_id) + ':' + (parent_id)

                            selfcitation = False
                            if author[0] == author2[0]:
                                selfcitation = True
                                selfcitationPapers = True

                            #if author2[0] in list1: selfcitation = True
                            value = [item for item in list1 if author2[0] in item]
                            if len(value) > 0:
                                selfcitation = True
                                selfcitationPapers = True

                            if (id or id_2) not in self.cocitations:
                                data = {
                                    'author_id': author[0],
                                    'author_name': author[2].strip(),
                                    'coauthor_id': author2[0],
                                    'coauthor_name': author2[2].strip(),
                                    'self_citation': selfcitation,
                                    'paper_doi': paper_row[5],
                                    'paper_title': paper_row[2],
                                    'parent_doi': parent_row[5],
                                    'parent_title': parent_row[2]
                                    #'value': 1,
                                    #'is_vinci': True
                                }
                                self.cocitations[id] = data
                print("Finish", paper_id, parent_id)
            self.get_papers_reference(paper_row, parent_row, selfcitationPapers)
        print("fin loop")

    def get_papers_reference(self, paper1, parent, flag):
        data = {
            'paper_id': paper1[0],
            'paper_title': paper1[2],
            'paper_doi': paper1[5],
            'self_citation': flag,
            'parent_id': parent[0],
            'parent_title': parent[2],
            'parent_doi': parent[5]
        }
        self.list_papers_ref.append(data)
        pass

    def make_csv_coaut(self, name, conjunto):
        csv_file = "data/" + name + '.csv'
        csv_columns = ['author_id', 'author_name', 'coauthor_id', 'coauthor_name', 'self_citation', 'paper_doi', 'paper_title', 'parent_doi', 'parent_title']
        with open(csv_file, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in conjunto.values():
                writer.writerow(data)

    def make_csv_refs(self, list):
        csv_file = "data/papers_references2.csv"
        csv_columns = ['paper_id', 'paper_title', 'paper_doi', 'self_citation', 'parent_id', 'parent_title', 'parent_doi']
        with open(csv_file, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in list:
                writer.writerow(data)

    def make_aut_citations(self):
        self.loop_ref()
        self.make_csv_coaut('aut_citations', self.cocitations)
        self.make_csv_refs(self.list_papers_ref)


if __name__ == '__main__':
    client = Client()
    client.make_aut_citations()