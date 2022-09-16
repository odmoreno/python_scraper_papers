import psycopg2
import json
import config
from common_functions import *

class dbData:
    def __init__(self):
        self.institution_cols = ['id', '_id', 'name', 'ad1', 'ad2', 'ad3', 'url']
        self.authors_cols = ['id', '_id', 'name', 'sid', 'acmid', 'url']
        self.author_insti_cols = ['id', 'author_id', 'institution_id']
        self.papers_cols = ['id', '_id', 'title', 'year', 'abstract', 'doi', 'n_citation', 'page_start',
                           'page_end', 'lang', 'volume', 'issue', 'ibsn', 'type', 'downloads',
                            'url', 'venue']
        self.papers_ref_col = ['id', 'papers_id', 'parent_papers_id']

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
        #path
        self.path_papers_id = "jsons/papers_ids.json"

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
    def load_papers(self):
        with open(self.papers_path, encoding='utf-8') as fh:
            data = json.load(fh)
        self.papers_set = data
        with open(self.path_papers_id, encoding='utf-8') as fh:
            data = json.load(fh)
        self.papers_id = data

    def save_ids(self):
        json_string2 = json.dumps(self.papers_id, ensure_ascii=False, indent=2)
        with open(self.path_papers_id, 'w', encoding="utf-8") as outfile:
            outfile.write(json_string2)

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

    def find_institutions(self, insti):
        try:
            name = insti['name']
            name = insti['name'].replace("'", "''")
            if name == 'University of London':
                print(name)
            querystring = "SELECT * FROM institution as p"
            querystring += " WHERE p._id LIKE '%" + insti['id'] + "%'"
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

    def find_paper(self, paper):
        try:
            name = paper['title']
            name = paper['title'].replace("'", "''")
            querystring = "SELECT * FROM papers as p"
            querystring += " WHERE p.title LIKE '%" + name + "%'"
            self.cursor.execute(querystring)
            mobile_records = self.cursor.fetchall()
            if len(mobile_records) > 0:
                print("Existe en papers_info db:", name)
                self.cursor2.execute(querystring)
                mobile_records2 = self.cursor2.fetchall()
                if len(mobile_records2) == 0:
                    id_paper = self.insert_paper(paper, mobile_records[0], True)
                    paper_ori_id = mobile_records[0][0]
                    querystring = "SELECT * FROM papers_reference"
                    querystring += " where papers_id = " + str(paper_ori_id)
                    self.cursor.execute(querystring)
                    references = self.cursor.fetchall()
                    for ref in references:
                        parent_paper_id = ref[2]
                        querystring = "SELECT * FROM papers as p"
                        querystring += " WHERE p._id LIKE '%" + parent_paper_id + "%'"
                        self.cursor.execute(querystring)
                        parent_paper = self.cursor.fetchall()
                        #check if exist in second db
                        self.cursor2.execute(querystring)
                        mobile_records3 = self.cursor2.fetchall()
                        if len(mobile_records3) == 0:
                            id_parent = self.insert_parent_paper(parent_paper)
                            self.insert_into_paper_ref(id_paper, id_parent)
                        pass
                else:
                    print('check references')
                    data = mobile_records2[0]
                    paper_ori_id = mobile_records[0][0]
                    querystring = "SELECT * FROM papers_reference"
                    querystring += " where papers_id = " + str(paper_ori_id)
                    self.cursor.execute(querystring)
                    references = self.cursor.fetchall()
                    for ref in references:
                        parent_paper_id = ref[2]
                        querystring = "SELECT * FROM papers as p"
                        querystring += " WHERE p._id LIKE '%" + parent_paper_id + "%'"
                        self.cursor.execute(querystring)
                        parent_paper = self.cursor.fetchall()
                        # check if exist in second db
                        self.cursor2.execute(querystring)
                        mobile_records3 = self.cursor2.fetchall()
                        if len(mobile_records3) == 0:
                            id_parent = self.insert_parent_paper(parent_paper)
                            self.insert_into_paper_ref(data[0], id_parent)

            else:
                print("NO existe insertar")
                if paper['doi'] not in self.papers_id:
                    self.insert_paper(paper, {})
                """
                querystring = "SELECT * FROM papers as p"
                querystring += " WHERE p.doi LIKE '%" + paper['doi'] + "%'"
                self.cursor2.execute(querystring)
                mobile_records = self.cursor2.fetchall()
                if len(mobile_records) == 0:
                    self.insert_paper(paper, {})"""
                pass
        except Exception as e:
            print(name)
            print(querystring)
            fail_message(e)
        pass

    def insert_parent_paper(self, list):
        paper = list[0]
        headers = "("
        headers += ", ".join(self.papers_cols)
        headers += ")"
        id_count = self.count_table_inst('papers')
        insert_query = "INSERT INTO papers" + headers + " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        record_to_insert = ()
        # split_string = paper['extra'][2].split("")
        record_to_insert = (id_count, paper[1], paper[2], paper[3], paper[4], paper[5], paper[7],
                            paper[8], paper[9], paper[10], paper[11], paper[12], paper[13], '', '','', '')

        self.cursor2.execute(insert_query, record_to_insert)
        count = self.cursor2.rowcount
        self.conn2.commit()

        return id_count

    def insert_into_paper_ref(self, id_paper, id_parent):
        print(id_paper, id_parent)
        headers = "("
        headers += ", ".join(self.papers_ref_col)
        headers += ")"
        id_count = self.count_table_inst('papers_reference')
        insert_query = "INSERT INTO papers_reference" + headers + " VALUES (%s,%s,%s)"
        record_to_insert = (id_count, id_paper, id_parent)
        self.cursor2.execute(insert_query, record_to_insert)
        count = self.cursor2.rowcount
        self.conn2.commit()

    def insert_paper(self, paper, row, prev_data=False):
        headers = "("
        headers += ", ".join(self.papers_cols)
        headers += ")"
        id_count = self.count_table_inst('papers')
        insert_query = "INSERT INTO papers" + headers + " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        record_to_insert = ()
        #split_string = paper['extra'][2].split("")
        if prev_data == True:
            record_to_insert = (id_count, row[1], paper['title'], row[3], row[4], paper['doi'], paper['citations'],
                                row[8], row[9], row[10], row[11], row[12], row[13], paper['type'], paper['downloads'],
                                paper['url'], paper['publisher'])
        else:
            record_to_insert = (id_count, '', paper['title'], paper['year'], paper['abstract'], paper['doi'], paper['citations'], '', '', '', '',
                                '', '', paper['type'], paper['downloads'], paper['url'], paper['publisher'])

        self.cursor2.execute(insert_query, record_to_insert)
        count = self.cursor2.rowcount
        self.conn2.commit()
        self.papers_id[paper['doi']] = id_count
        self.save_ids()
        return id_count

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
                if insti_id != 'javascript:void(0)':
                    query = "SELECT * FROM institution as i"
                    query += " WHERE i._id LIKE '%" + insti_id + "%'"
                    self.cursor2.execute(query)
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
        value = self.find_if_exist_au_insti(author[0], insti[0])
        if not value:
            id_count = self.count_table_inst('author_institution')
            insert_query = "INSERT INTO author_institution" + headers + " VALUES (%s,%s,%s)"
            record_to_insert = (id_count,
                            author[0],
                            insti[0])
            self.cursor2.execute(insert_query, record_to_insert)
            count = self.cursor2.rowcount
            self.conn2.commit()

    def find_if_exist_au_insti(self, id_auth, id_inst):
        querystring = "SELECT * FROM author_institution"
        querystring += " WHERE author_id = "+  str(id_auth) + " and institution_id=" + str(id_inst)
        self.cursor2.execute(querystring)
        mobile_records = self.cursor2.fetchall()
        if len(mobile_records) == 0:
            return False
        else:
            return True



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
            self.find_data_ai(au)
            pass
    def loop_papers(self):
        self.load_papers()
        for paper in self.papers_set.values():
            self.find_paper(paper)

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
        #self.pass_data_to_db_au()
        #self.loop_authors_insti()
        self.loop_papers()


if __name__ == "__main__":
    client = dbData()
    client.main()
