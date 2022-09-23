import psycopg2
import json
import time
import re
from common_functions import *


class Client:

    def __init__(self):
        self.base_url = "/dl.acm.org"
        self.papers_dict = {}
        self.authors_set = {}
        self.dir = "jsons/"
        self.papers_path = "jsons/papers.json"
        self.real_authors_path = "jsons/authors.json"
        self.institution_path = "jsons/insti.json"
        self.intitution_set = {}
        # conexion con subset db
        self.conn = self.connect_to_subset_db()
        self.cursor = self.conn.cursor()

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


    def make_csv_rel2(self, list):
        csv_file = "jsons/papers_authors.csv"
        csv_columns = ['paper_id', 'paper_name', 'author_id', 'author_name']
        with open(csv_file, 'w', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in list:
                writer.writerow(data)

    def make_csv_rel1(self, list):
        csv_file = "jsons/authors_institutes.csv"
        csv_columns = ['author_id', 'author_name', 'institute_id', 'institute_name']
        with open(csv_file, 'w', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in list:
                writer.writerow(data)

    def make_csv_refs(self, list):
        csv_file = "jsons/papers_references.csv"
        csv_columns = ['paper_id', 'paper_title', 'paper_doi', 'parent_id', 'parent_title', 'parent_doi']
        with open(csv_file, 'w', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in list:
                writer.writerow(data)

if __name__ == '__main__':
    client = Client()
    #list = client.make_rows()
    #client.make_csv_rel1(list)
    #list1 = client.make_rows_papers()
    #client.make_csv_rel2(list1)
    list = client.loop_ref()
    client.make_csv_refs(list)