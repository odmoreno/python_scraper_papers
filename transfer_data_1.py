import psycopg2
import json
import config
from common_functions import *

class dbData:
    def __init__(self):
        self.institution_cols = ['id', '_id', 'name', 'ad1', 'ad2', 'ad3', 'url']
        # conexion con papers_info
        self.conn1 = connect_to_first_db()
        self.cursor = self.conn1.cursor()
        # conexion con subset db
        self.conn2 = connect_to_second_db()
        self.cursor2 = self.conn2.cursor()
        # sets de informacion
        self.institution_set = load_institutions()
        self.authors_set = load_authors()
        self.papers_set = load_papers()
        # creando archivos de llaves
        create_files_for_keys()
        # ids
        self.insti_ids = {}
        self.papers_ids = {}
        self.authors_ids = {}

    def load_keys(self):
        # ids
        self.insti_ids = load_inti_keys()
        self.papers_ids = load_papers_keys()
        self.authors_ids = load_authors_keys()

    def record_insti(self, id, insti):
        record_to_insert = (id,
                            insti['id'],
                            insti['name'],
                            insti['ad0'],
                            '' if 'ad1' not in insti else insti['ad1'],
                            '' if 'ad2' not in insti else insti['ad2'],
                            insti['url'])
        return record_to_insert

    def insert_row(self, dict, cols, table_name, tam, option):
        headers = create_headers(cols)
        id_count = count_table_inst(table_name, self.cursor2)
        values_string = create_s_values(tam)
        insert_query = "INSERT INTO " + table_name + headers + values_string
        record_to_insert = ()
        if option == 1:
            record_to_insert = self.record_insti(id_count, dict)
            #dict['id_table'] = id_count
        self.cursor2.execute(insert_query, record_to_insert)
        count = self.cursor2.rowcount
        self.conn2.commit()
        if option == 1 :
            self.insti_ids[dict['id']] = id_count
            save_ids(self.insti_ids, insti_keys_path)


    def find_institutions(self, insti):
        try:
            name = insti['name'].replace("'", "''")
            querystring = "SELECT * FROM institution as p"
            querystring += " WHERE p._id LIKE '%" + insti['id'] + "%'"
            self.cursor2.execute(querystring)
            mobile_records = self.cursor2.fetchall()
            if len(mobile_records) > 0:
                print("Ya existe:", name)
            else:
                print("NO existe insertar")
                self.insert_row(insti, self.institution_cols, 'institution', 7, 1)
        except Exception as e:
            print(name)
            print(querystring)
            fail_message(e)

    def pass_data_to_db_i(self):
        for insti in self.institution_set.values():
            if insti['id'] not in self.insti_ids:
                self.find_institutions(insti)
            pass

    def main(self):
        self.pass_data_to_db_i()

if __name__ == "__main__":
    client = dbData()
    client.load_keys()
    client.main()