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


    def connect_to_subset_db(self):
        conn = psycopg2.connect(
            host="200.10.150.106",
            database="subset",
            user="postgres",
            password="postgres")
        print("Opened Subset DB successfully")
        return conn

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

        dict_from_csv = {}
        with open('data/papers_refences_table.csv', mode='r') as inp:
            reader = csv.reader(inp)
            dict_from_csv = {rows[0]: {'paper_id': rows[1], 'parent_id': rows[2]} for rows in reader}

        print(dict_from_csv)
        self.dict_papers_ref = dict_from_csv

    def loop_ref(self):
        querystring = "SELECT * FROM papers_reference"
        self.cursor.execute(querystring)
        refs = self.cursor.fetchall()
        list = []
        for reference in refs:
            paper_id = reference[1]
            parent_id = reference[2]
            paper1 = self.find_paper(paper_id)[0]
            parent = self.find_paper(parent_id)[0]
            data = {
                'paper_id': paper1[0],
                'paper_title': paper1[2],
                'paper_doi': paper1[5],
                'parent_id': parent[0],
                'parent_title': parent[2],
                'parent_doi': parent[5]
            }
            list.append(data)
        return list

    def find_paper(self, p_id):
        querystring = "SELECT * FROM papers"
        querystring += " WHERE id=" + str(p_id)
        self.cursor.execute(querystring)
        paper = self.cursor.fetchall()
        return paper

    def make_rows(self):
        self.load_data()
        list = []
        for author in self.authors_set.values():
            author_id = author['id']
            for institute in author['venue']:
                name_inst = institute['name']
                if institute['id'] == 'javascript:void(0)':
                    print('no')
                else:
                    data = {
                        'author_id': author_id,
                        'author_name': author['name'],
                        'institute_id': institute['id'],
                        'institute_name': name_inst
                    }
                    list.append(data)
        return list


    def make_rows_papers(self):
        self.load_data()
        list = []
        for paper in self.papers_dict.values():
            for author in paper['authors']:
                data = {
                    'paper_id': paper['doi'],
                    'paper_name': paper['title'],
                    'author_id': author['id'],
                    'author_name': author['name'].strip()
                }
                list.append(data)
        return list

    def make_rows_coautors(self):
        self.load_data()
        for paper in self.papers_dict.values():
            autores = paper['authors']
            tam = len(autores)
            j = 1
            for author in autores:
                for i in range(j,tam):
                    coauthor = autores[i]
                    id = author['id'] + ':' + coauthor['id']
                    id_2 = coauthor['id'] + ':' + author['id']
                    if (id or id_2) not in self.dictcoautores:
                        data = {
                            'author_id': author['id'],
                            'author_name': author['name'].strip(),
                            'coauthor_id': coauthor['id'],
                            'coauthor_name': coauthor['name'].strip(),
                            'value': 1,
                            'is_vinci': True if paper['publisher'] == 'ACM' else False
                        }
                        self.dictcoautores[id] = data
                        pass
                    else:
                        data = self.dictcoautores[id]
                        newval = data['value'] +1
                        self.dictcoautores[id]['value'] = newval
                j +=1
        pass

    def make_csv_coaut(self, name, conjunto):
        csv_file = "data/" + name + '.csv'
        csv_columns = ['author_id', 'author_name', 'coauthor_id', 'coauthor_name', 'value', 'is_vinci']
        with open(csv_file, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in conjunto.values():
                writer.writerow(data)

    def make_csv_rel2(self, list):
        csv_file = "jsons/papers_authors.csv"
        csv_columns = ['paper_id', 'paper_name', 'author_id', 'author_name']
        with open(csv_file, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in list:
                writer.writerow(data)

    def make_csv_rel1(self, list):
        csv_file = "jsons/authors_institutes.csv"
        csv_columns = ['author_id', 'author_name', 'institute_id', 'institute_name']
        with open(csv_file, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in list:
                writer.writerow(data)

    def make_csv_refs(self, list):
        csv_file = "jsons/papers_references.csv"
        csv_columns = ['paper_id', 'paper_title', 'paper_doi', 'parent_id', 'parent_title', 'parent_doi']
        with open(csv_file, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in list:
                writer.writerow(data)

    def get_paper_db(self, id):
        try:
            querystring = "SELECT * FROM papers"
            querystring += " WHERE id=" + str(id)
            self.cursor.execute(querystring)
            paper_records = self.cursor.fetchall()
            if len(paper_records) > 0:
                print("search", paper_records[0])
                return paper_records[0]

        except Exception as e:
            print(id)
            print(querystring)
            fail_message(e)
        pass
    def get_authors_papers_db(self, id):
        set_authors = {}
        try:
            querystring = "SELECT * FROM papers_authors as o"
            querystring += " where o.papers_id =" + str(id)
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
            print("search", paper_records[0])
            return paper_records[0]

    def loop_ref(self):
        self.load_data()
        for references in self.dict_papers_ref.values():
            paper_id = references['paper_id']
            parent_id = references['parent_id']
            #paper_row = self.get_paper_db(paper_id)
            #parent_row = self.get_paper_db(parent_id)
            list1 = self.get_authors_papers_db(paper_id)
            list2 = self.get_authors_papers_db(parent_id)
            if len(list1) != 0 and len(list2) !=0:
                print("matches")
                for author in list1:
                    for author2 in list2:
                        if author[0] != author2[0]:
                            id = str(author[0]) + ':' + str(author2[0])
                            id_2 = str(author2[0]) + ':' + str(author[0])
                            if (id or id_2) not in self.cocitations:
                                data = {
                                    'author_id': author[0],
                                    'author_name': author[2].strip(),
                                    'coauthor_id': author2[0],
                                    'coauthor_name': author2[2].strip(),
                                    'value': 1,
                                    'is_vinci': True
                                }
                                self.cocitations[id] = data

if __name__ == '__main__':
    client = Client()
    #list = client.make_rows()
    #client.make_csv_rel1(list)
    list1 = client.make_rows_papers()
    client.make_csv_rel2(list1)
    #ist = client.loop_ref()
    #client.make_csv_refs(list)

    #client.make_rows_coautors()
    #client.make_csv_coaut()

    client.loop_ref()
    client.make_csv_coaut('cocitations', client.cocitations)