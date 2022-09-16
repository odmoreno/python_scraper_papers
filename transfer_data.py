import psycopg2
import json
import config
from common_functions import *

class dbData:
    def __init__(self):
        self.institution_cols = ['id', '_id', 'name', 'ad1', 'ad2', 'ad3', 'url']
        self.authors_cols = ['id', '_id', 'name', 'sid', 'acmid', 'url']
        self.author_insti_cols = ['id', 'author_id', 'institution_id']
        # conexion con papers_info
        self.conn1 = self.connect_to_first_db()
        self.cursor = self.conn1.cursor()
        # conexion con subset db
        self.conn2 = self.connect_to_second_db()
        self.cursor2 = self.conn2.cursor()
        # rutas de docs
        self.institution_path = 'jsons/insti.json'
        self.authors_path = 'jsons/authors.json'
        # sets de informacion
        self.institution_set = {}
        self.authors_set = {}
        # ids de tablas

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

    def load_institutions(self):
        with open(self.institution_path, encoding='utf-8') as fh:
            insti = json.load(fh)
        self.institution_set = insti
    def load_authors(self):
        with open(self.authors_path, encoding='utf-8') as fh:
            authors = json.load(fh)
        self.authors_set = authors

    def find_institutions(self, insti):
        try:
            name = insti['name']
            name = insti['name'].replace("'", "''")
            querystring = "SELECT * FROM institution as p"
            querystring += " WHERE p.name LIKE '%" + name + "%'"
            self.cursor2.execute(querystring)
            mobile_records = self.cursor2.fetchall()
            if len(mobile_records) > 0:
                print("Ya existe:", name)
            else:
                print("NO existe insertar")
                self.insert_row_in_institution(insti)
                pass
        except Exception as e:
            print(name)
            print(querystring)
            fail_message(e)

    def find_authors(self, author):
        try:
            name = author['name']
            name = author['name'].replace("'", "''")
            querystring = "SELECT * FROM authors as p"
            querystring += " WHERE p.name LIKE '%" + name + "%'"
            self.cursor.execute(querystring)
            mobile_records = self.cursor.fetchall()
            if len(mobile_records) > 0:
                print("Existe en papers_info db:", name)
                self.cursor2.execute(querystring)
                mobile_records2 = self.cursor2.fetchall()
                if len(mobile_records2) == 0:
                    self.insert_row_in_authors(author, mobile_records[0], True)
            else:
                print("NO existe insertar")
                self.cursor2.execute(querystring)
                mobile_records = self.cursor2.fetchall()
                if len(mobile_records) == 0:
                    self.insert_row_in_authors(author, {})
                pass
        except Exception as e:
            print(name)
            print(querystring)
            fail_message(e)

    def find_data_ai(self, author):
        try:
            name = author['name']
            name = author['name'].replace("'", "''")
            querystring = "SELECT * FROM authors as p"
            querystring += " WHERE p.name LIKE '%" + name + "%'"
            self.cursor2.execute(querystring)
            mobile_records = self.cursor2.fetchall()
            author_in_db = mobile_records[0]
            for insti in author['institutions']:
                insti_id = insti['id']
                query = "SELECT * FROM institution as i"
                query += " WHERE i._id LIKE '%" + insti_id + "%'"
                self.cursor2.execute(querystring)
                mobile_records2 = self.cursor2.fetchall()
                insti_in_db = mobile_records2[0]
                self.make_relation_au_insti(author_in_db, insti_in_db)
        except Exception as e:
            print(name)
            print(querystring)
            fail_message(e)

    def make_relation_au_insti(self, author, insti):
        print(author)
        print(insti)
        headers = "("
        headers += ", ".join(self.author_insti_cols)
        headers += ")"
        id_count = self.count_table_inst('author_institution')
        insert_query = "INSERT INTO author_institution" + headers + " VALUES (%s,%s,%s)"
        record_to_insert = (id_count,
                            author[0],
                            insti[0])

        self.cursor2.execute(insert_query, record_to_insert)
        count = self.cursor2.rowcount
        self.conn2.commit()


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

    def insert_row_in_authors(self, au, prev, prev_data=False):
        headers = "("
        headers += ", ".join(self.authors_cols)
        headers += ")"
        id_count = self.count_table_inst('authors')
        iddb = ''
        sid = ''
        if prev_data == True:
            iddb = '' if prev[1] is None else prev[1]
            sid = '' if prev[3] is None else prev[3]

        insert_query = "INSERT INTO authors" + headers + " VALUES (%s,%s,%s,%s,%s,%s)"
        record_to_insert = (id_count,
                            iddb,
                            au['name'],
                            sid,
                            au['id'],
                            au['url'])

        self.cursor2.execute(insert_query, record_to_insert)
        count = self.cursor2.rowcount
        self.conn2.commit()


    def insert_row_in_institution(self, insti):
        headers = "("
        headers += ", ".join(self.institution_cols)
        headers += ")"
        id_count = self.count_table_inst('institution')
        insert_query = "INSERT INTO institution" + headers + " VALUES (%s,%s,%s,%s,%s,%s,%s)"
        newname = insti['name'].replace("'", "''")
        record_to_insert = ( id_count,
            insti['id'],
            insti['name'],
            insti['ad0'],
            '' if 'ad1' not in insti else insti['ad1'],
            '' if 'ad2' not in insti else insti['ad2'],
            insti['url'])
        self.cursor2.execute(insert_query, record_to_insert)
        count = self.cursor2.rowcount
        self.conn2.commit()
        pass

    def loop_authors_insti(self):
        self.load_authors()
        for au in self.authors_set.values():

            pass

    def pass_data_to_db_i(self):
        self.load_institutions()
        for insti in self.institution_set.values():
            self.find_institutions(insti)
            pass
    def pass_data_to_db_au(self):
        self.load_authors()
        for au in self.authors_set.values():
            self.find_authors(au)
            pass

    def main(self):
        #self.pass_data_to_db_i()
        self.pass_data_to_db_au()


if __name__ == "__main__":
    client = dbData()
    client.main()
