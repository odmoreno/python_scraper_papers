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
        self.auth_insti_ids = {}
        self.current_id_rel = 0

    def load_keys(self):
        # ids
        self.insti_ids = load_inti_keys()
        self.papers_ids = load_papers_keys()
        self.authors_ids = load_authors_keys()
        self.auth_insti_ids = load_rel1_keys()

    def record_insti(self, id, insti):
        record_to_insert = (id,
                            insti['id'],
                            insti['name'],
                            insti['ad0'],
                            '' if 'ad1' not in insti else insti['ad1'],
                            '' if 'ad2' not in insti else insti['ad2'],
                            insti['url'])
        return record_to_insert

    def record_author(self,id_count, au, iddb, sid):
        record_to_insert = (id_count,
                            iddb,
                            au['name'],
                            sid,
                            au['id'],
                            au['url'])
        return record_to_insert

    def record_relations(self,  id_count, id1, id2):
        record_to_insert = (id_count, id1, id2)
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

    def insert_row_with_prev_data(self, dict, prev, cols, table_name, tam, option, prev_data=False):
        headers = create_headers(cols)
        id_count = count_table_inst(table_name, self.cursor2)
        values_string = create_s_values(tam)
        iddb = ''
        sid = ''
        if prev_data == True:
            iddb = '' if prev[1] is None else prev[1]
            sid = '' if prev[3] is None else prev[3]
        insert_query = "INSERT INTO " + table_name + headers + values_string
        record_to_insert = self.record_author(id_count, dict, iddb, sid)
        self.cursor2.execute(insert_query, record_to_insert)
        self.conn2.commit()
        if option == 1 :
            self.authors_ids[dict['id']] = id_count
            save_ids(self.authors_ids, authors_keys_path)

    def insert_rows_for_relations(self, id1, id2, cols, table_name, tam):
        headers = create_headers(cols)
        id_count = count_table_inst(table_name, self.cursor2)
        values_string = create_s_values(tam)
        insert_query = "INSERT INTO " + table_name + headers + values_string
        record_to_insert = self.record_relations(id_count, id1, id2)
        self.cursor2.execute(insert_query, record_to_insert)
        count = self.cursor2.rowcount
        self.conn2.commit()
        self.current_id_rel = id_count


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

    def find_authors(self, author):
        try:
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
                    self.insert_row_with_prev_data(author, mobile_records[0], self.authors_cols, 'authors', 6, 1, True)
                    self.loop_insti_authors(author['institutions'], author)
            else:
                print("NO existe insertar")
                self.cursor2.execute(querystring)
                mobile_records = self.cursor2.fetchall()
                if len(mobile_records) == 0:
                    self.insert_row_with_prev_data(author, {}, self.authors_cols, 'authors', 6, 1)
                    self.loop_insti_authors(author['institutions'], author)
        except Exception as e:
            print(name)
            print(querystring)
            fail_message(e)

    def loop_insti_authors(self, list, auth):
        auth_db_id = self.authors_ids[auth['id']]
        for insti in list:
            if insti['id'] != 'javascript:void(0)':
                insti_id = insti['id']
                insti_id_db = self.insti_ids[insti_id]
                self.insert_rows_for_relations(auth_db_id, insti_id_db, self.author_insti_cols, 'author_institution', 3)
                data = {
                    'author_db_id': auth_db_id,
                    'author_id': auth['id'],
                    'insti_db_id': insti_id_db,
                    'insti_id': insti_id
                }
                self.auth_insti_ids[self.current_id_rel] = data
                save_ids(self.auth_insti_ids, auth_insti_keys_path)

    def pass_data_to_db_i(self):
        for insti in self.institution_set.values():
            if insti['id'] not in self.insti_ids:
                self.find_institutions(insti)
            pass

    def pass_data_to_db_au(self):
        for au in self.authors_set.values():
            if au['id'] not in self.authors_ids:
                self.find_authors(au)
            pass

    def main(self):
        #self.pass_data_to_db_i()
        self.pass_data_to_db_au()

if __name__ == "__main__":
    client = dbData()
    client.load_keys()
    client.main()