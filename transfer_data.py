import psycopg2
import json
import config
from common_functions import *

class dbData:
    def __init__(self):
        self.institution_cols = ['id', '_id', 'name', 'ad1', 'ad2', 'ad3', 'url']
        # conexion con papers_info
        self.conn1 = self.connect_to_first_db()
        self.cursor = self.conn1.cursor()
        # conexion con subset db
        self.conn2 = self.connect_to_second_db()
        self.cursor2 = self.conn2.cursor()
        # rutas de docs
        self.institution_path = 'jsons/insti.json'
        # sets de informacion
        self.institution_set = {}
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

    def find_institutions(self, insti):
        try:
            name = insti['name']
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
        pass

    def count_table_inst(self):
        # query to count total number of rows
        sql = 'SELECT count(*) from institution'
        data = []
        # execute the query
        self.cursor2.execute(sql, data)
        results = self.cursor2.fetchone()
        # loop to print all the fetched details
        for r in results:
            print(r)
        print("Total number of rows in the table:", r)
        return r


    def insert_row_in_institution(self, insti):
        headers = "("
        headers += ", ".join(self.institution_cols)
        headers += ")"
        id_count = self.count_table_inst()
        insert_query = "INSERT INTO institution" + headers + " VALUES (%s,%s,%s,%s,%s,%s,%s)"
        record_to_insert = ( id_count,
            insti['id'],
            insti['name'],
            insti['ad0'],
            insti['ad1'],
            '' if 'ad2' not in insti else insti['ad2'],
            insti['url'])
        self.cursor2.execute(insert_query, record_to_insert)
        count = self.cursor2.rowcount
        self.conn2.commit()

        pass

    def pass_data_to_db(self):
        self.load_institutions()
        for insti in self.institution_set.values():
            self.find_institutions(insti)
            pass

    def main(self):
        self.pass_data_to_db()


if __name__ == "__main__":
    client = dbData()
    client.main()
