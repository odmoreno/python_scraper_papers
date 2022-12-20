import psycopg2
import json
import config
from common_functions import *

'''
Crea relaciones de papers_authors 
> recorre la tabla de papers de la base subset
> encuentra los autores registrados de los papers
> luego los insertamos en la tabla papers_reference
'''
class dbData:
    def __init__(self):
        #columnas de tablas
        self.papers_authors_col = ['id', 'papers_id', 'authors_id']
        # conexion con papers_info
        self.conn1 = self.connect_to_first_db()
        self.cursor = self.conn1.cursor()
        # conexion con subset db
        self.conn2 = self.connect_to_second_db()
        self.cursor2 = self.conn2.cursor()
        # rutas de docs
        self.institution_path = 'jsons/insti.json'
        self.authors_path = 'jsons/authors.json'
        self.papers_path = 'jsons/papers.json'
        # sets de informacion
        self.institution_set = {}
        self.authors_set = {}
        self.papers_set = {}
        self.papers_id = {}

    def connect_to_first_db(self):
        conn = psycopg2.connect(
            host="200.10.150.106",
            database="papers_info",
            user="postgres",
            password="postgres")
        print("Opened database successfully")
        return conn

    def connect_to_second_db(self):
        conn = psycopg2.connect(
            host="200.10.150.106",
            database="subset",
            user="postgres",
            password="postgres")
        print("Opened database subset successfully")
        return conn

    def load_papers(self):
        with open(self.papers_path, encoding='utf-8') as fh:
            data = json.load(fh)
        self.papers_set = data

    def count_table_inst(self, table):
        # query to count total number of rows
        sql = 'SELECT count(*) from ' + table
        data = []
        # execute the query
        self.cursor2.execute(sql, data)
        results = self.cursor2.fetchone()
        # loop to print all the fetched details
        for r in results:
            print(r)
        #print("Total number of rows in the table:", r)
        return r

    #buscar los autores en los papers en la base subset, para luego insertarlos en la tabla de relaciones "papers_authors"
    def find_paper(self, paper):
        try:
            doi = paper['doi']
            querystring = "SELECT * FROM papers as p"
            querystring += " WHERE p.doi LIKE '%" + doi + "%'"
            self.cursor2.execute(querystring)
            mobile_records = self.cursor2.fetchall()
            if len(mobile_records) > 0:
                print("Existe en papers_info db:", doi)
                paper_id = mobile_records[0][0]
                for author in paper['authors']:
                    acmid = author['id']
                    querystring = "SELECT * FROM authors as p"
                    querystring += " WHERE p.acmid LIKE '%" + acmid + "%'"
                    self.cursor2.execute(querystring)
                    author_records = self.cursor2.fetchall()
                    if len(author_records) > 0:
                        author_id = author_records[0][0]
                        self.insert_into_papers_authors(paper_id, author_id)

        except Exception as e:
            print(doi)
            print(querystring)
            fail_message(e)


    def insert_into_papers_authors(self, paper_id, author_id):
        print(paper_id, author_id)
        headers = "("
        headers += ", ".join(self.papers_authors_col)
        headers += ")"
        id_count = self.count_table_inst('papers_authors')
        insert_query = "INSERT INTO papers_authors" + headers + " VALUES (%s,%s,%s)"
        record_to_insert = (id_count, paper_id, author_id)
        self.cursor2.execute(insert_query, record_to_insert)
        count = self.cursor2.rowcount
        self.conn2.commit()

    def loop_papers(self):
        self.load_papers()
        for paper in self.papers_set.values():
            self.find_paper(paper)

    def main(self):
        # self.pass_data_to_db_i()
        self.loop_papers()
        pass

if __name__ == "__main__":
    client = dbData()
    client.main()