import psycopg2
import json
import config
from common_functions import *

class PostData:
    def __init__(self):
        self.id =0 #self.load_id()
        self.row_values = [ 'id', '_id', 'title', 'year', 'abstract', 'doi', 'pdf', 'n_citation', 'page_start', 'page_end',
             'lang', 'volume', 'issue', 'ibsn', 'venue_id', 'type', 'downloads', 'publisher', 'conference_title']

        self.data = get_data_conferences()
        self.data = self.data[:12]

        self.conn = self.connect_to_first_db()
        self.cursor = self.conn.cursor()
        self.conn2 = self.connect_to_second_db()
        self.cursor2 = self.conn2.cursor()

    def load_id(self):
        filename = "data/id.json"
        f = open(filename)
        data = json.load(f)
        print(data)
        f.close()
        return data


    def save_id(self):
        filename = "data/id.json"
        json_string = json.dumps(self.id, indent=2)
        # Using a JSON string
        with open(filename, 'w') as outfile:
            outfile.write(json_string)


    def connect_to_first_db(self):
        conn = psycopg2.connect(
            host="200.10.150.106",
            database="papers_info",
            user="postgres",
            password="postgres")
        print("Opened database successfully")
        return  conn

    def connect_to_second_db(self):
        conn = psycopg2.connect(
            host="200.10.150.106",
            database="subset",
            user="postgres",
            password="postgres")
        print("Opened database subset successfully")
        return  conn

    def find_paper(self, paper):

        try:
            title = paper['title']
            querystring = "SELECT * FROM papers as p"
            querystring += " WHERE p.title LIKE '%" + title + "%'"
            self.cursor.execute(querystring)
            mobile_records = self.cursor.fetchall()
            if len(mobile_records) > 0:
                print("hay valores en:", title)
                self.cursor2.execute(querystring)
                mobile_records = self.cursor2.fetchall()
                if len(mobile_records) == 0:
                    for row in mobile_records:
                        print(row)
                        self.insert_row_with_preview_dat(row, paper)
                else:
                    print("ya existe")
                    self.id += 1
            else:
                print("add info to subset")
                self.cursor2.execute(querystring)
                mobile_records = self.cursor2.fetchall()
                if len(mobile_records) == 0:
                    self.insert_row(paper)
                else:
                    self.id += 1
        except Exception as e:
            print(title)
            print(querystring)
            print(self.id)
            fail_message(e)


    def insert_row_with_preview_dat(self, row, paper):
        headers = "("
        headers += ", ".join(self.row_values)
        headers += ")"
        insert_query = "INSERT INTO papers" + headers + " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        record_to_insert = (self.id, row[1], row[2], row[3], row[4], paper['doi'], '', paper['citations'], row[8], row[9],
            row[10], row[11], row[12], row[13], row[14], paper['type'], paper['downloads'], paper['publisher'], paper['conference_title'])

        self.cursor2.execute(insert_query, record_to_insert)
        self.conn2.commit()
        count = self.cursor2.rowcount
        self.id += 1
        self.save_id()
        print(count, "Record inserted successfully into mobile table")

    def insert_row(self, paper):
        headers = "("
        headers += ", ".join(self.row_values)
        headers += ")"

        insert_query = "INSERT INTO papers" + headers + " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        record_to_insert = (self.id, '', paper['title'], paper['year'], '', paper['doi'], '', paper['citations'], '', '',
                            '', '', '', '', None, paper['type'], paper['downloads'], paper['publisher'],
                            paper['conference_title'])
        self.cursor2.execute(insert_query, record_to_insert)
        self.conn2.commit()
        count = self.cursor2.rowcount
        self.id += 1
        self.save_id()
        print(count, "Record inserted successfully into mobile table")


    def main(self):
        for conf in self.data:
            name = conf[0] + '_' + conf[1] + '.json'
            filename = config.path_to_search_results + name
            with open(filename, encoding="utf-8") as data_file:
                papers = json.load(data_file)
                for paper in papers.values():
                    print(paper)
                    self.find_paper(paper)
                    pass


if __name__ == "__main__":
    client = PostData()
    client.main()
