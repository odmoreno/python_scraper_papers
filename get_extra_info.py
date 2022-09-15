"""
Obtener info adicional del paper como sus autores
"""
import psycopg2
import json
import time
import re
from common_functions import *


class Info:
    def __init__(self, urls):
        self.list_urls = urls
        self.base_url = "/dl.acm.org"
        self.driver_for_acm = make_chrome_headless()
        self.papers_dict = {}
        self.authors_tmp_dict = {}
        self.authors_set = {}
        self.intitution_set = {}
        self.dir = "jsons/"
        self.papers_path = "jsons/papers.json"
        self.authors_temp_path = "jsons/authors_tmp.json"
        self.load_data()
        self.real_authors_path = "jsons/authors.json"
        self.institution_temp_path = "jsons/insti_temp.json"
        self.institution_path = "jsons/insti.json"
        self.intitution_set2 = {}

        self.conn = self.connect_to_first_db()
        self.cursor = self.conn.cursor()
        self.conn2 = self.connect_to_second_db()
        self.cursor2 = self.conn2.cursor()
        self.id= 0

        self.headers_authors = ['id', '_id', 'name', 'sid', 'org', 'gid', 'oid', 'orgid', 'acmid', 'url']

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
        return conn

    def load_data(self):
        with open(self.papers_path, encoding='utf-8') as fh:
            papers = json.load(fh)
        #print(papers)
        with open(self.authors_temp_path, encoding='utf-8') as fh:
            authors = json.load(fh)
        #print(authors)

        self.papers_dict = papers
        self.authors_tmp_dict = authors
        #return [papers, authors]

    def load_data2(self):
        with open(self.real_authors_path, encoding='utf-8') as fh:
            autores = json.load(fh)
        with open(self.institution_temp_path, encoding='utf-8') as fh:
            insti = json.load(fh)

        self.authors_set = autores
        self.intitution_set = insti

    def load_insti(self):
        with open(self.institution_path, encoding='utf-8') as fh:
            insti = json.load(fh)
        self.intitution_set2 = insti

    def save_data(self):
        #save current papers
        json_string = json.dumps(self.papers_dict, ensure_ascii= False, indent=2)
        with open(self.papers_path, 'w', encoding="utf-8") as outfile:
            outfile.write(json_string)
        #save current authors
        json_string2 = json.dumps(self.authors_tmp_dict, ensure_ascii= False, indent=2)
        with open(self.authors_temp_path, 'w', encoding="utf-8") as outfile:
            outfile.write(json_string2)

    def save_autores(self):
        json_string2 = json.dumps(self.authors_set, ensure_ascii=False, indent=2)
        with open(self.real_authors_path, 'w', encoding="utf-8") as outfile:
            outfile.write(json_string2)

    def save_institutions(self):
        json_string2 = json.dumps(self.intitution_set, ensure_ascii=False, indent=2)
        with open(self.institution_temp_path, 'w', encoding="utf-8") as outfile:
            outfile.write(json_string2)

    def save_institutions2(self):
        json_string2 = json.dumps(self.intitution_set2, ensure_ascii=False, indent=2)
        with open(self.institution_path, 'w', encoding="utf-8") as outfile:
            outfile.write(json_string2)

    def get_author_props(self, element):
        name_prop = element.find('span', class_="auth-name")
        venue_prop = element.find('span', class_="info--text auth-institution")
        temp_url = element.find('span', class_="auth-name").a["href"]
        lst = ["https:/", self.base_url, temp_url]
        url_author = "".join(lst)
        name = '' if name_prop is None else name_prop.text
        venue = '' if venue_prop is None else venue_prop.text
        temp_id = temp_url[9:]
        name_text = " ".join(name.split())
        data = {
            'name': name_text,
            'institution': venue.strip(),
            'url': url_author,
            'id': temp_id
        }
        #save author in dict
        self.authors_tmp_dict[temp_id] = data
        return data


    def paper_scraper(self, paper):
        url_paper = paper['url']
        self.driver_for_acm.get(url_paper)
        time.sleep(5)
        #load scripts inside de page
        button = self.driver_for_acm.find_element_by_css_selector("button[title='Information and Authors']")
        self.driver_for_acm.execute_script("arguments[0].click();", button)
        buttons = self.driver_for_acm.find_elements_by_css_selector("button[title='Information and Authors']")
        for but in buttons:
            self.driver_for_acm.execute_script("arguments[0].click();", but)
        time.sleep(5)
        # parse source code
        soup = BeautifulSoup(self.driver_for_acm.page_source, "html.parser")
        #print(soup.prettify())
        authors_info = soup.findAll("div", class_="auth-info")
        authors_list = []
        for author in authors_info:
            data_author = self.get_author_props(author)
            authors_list.append(data_author)

        #print(authors_list)
        abstract_section = soup.find("div", class_="abstractSection abstractInFull")
        abstract_text = abstract_section.find('p').text.strip()
        references_list = soup.find("ol", class_="rlist references__list references__numeric")
        count = 0 if references_list is None else  len(references_list)
        paper['abstract'] = abstract_text
        paper['authors'] = authors_list
        paper['n_reference'] = count
        # save paper in dict
        self.papers_dict[paper['doi']] = paper
        self.save_data()
        print("Listo : ", paper['title'])

    def main_fun(self):
        try:
            for url in self.list_urls:
                # get the json namefile of conference
                name = url[0] + '_' + url[1]
                namefile = config.path_to_search_results + name + '.json'
                print("Inicia:", name)
                with open(namefile, encoding='utf-8') as f:
                    data = json.load(f)
                    for paper in data.values():
                        if paper['doi'] not in self.papers_dict:
                            self.paper_scraper(paper)
                        else:
                            print('ya existe ...', paper['title'])
                            if len(paper['authors']) == 0:
                                self.paper_scraper(paper)

                    print("Terminado: ", name)
        except Exception as e:
            fail_message(e)
            self.driver_for_acm.quit()

    def get_authors(self):
        try:
            self.load_data2()
            for author in self.authors_tmp_dict.values():
                self.get_authors_info(author)

            print("fin")
        except Exception as e:
            print(e)
            fail_message(e)
            self.driver_for_acm.quit()

    def get_authors_info(self, autor):

        url = autor['url']
        if autor['id']  not in self.authors_set:
            print('Current autor', autor['name'])
            if autor['url'] != "":
                self.driver_for_acm.get(url)
                time.sleep(5)
                buttons = self.driver_for_acm.find_elements_by_class_name("removed-items-count")
                for but in buttons:
                    self.driver_for_acm.execute_script("arguments[0].click();", but)
                time.sleep(5)

                # parse source code
                soup = BeautifulSoup(self.driver_for_acm.page_source, "html.parser")
                # print(soup.prettify()) #removed-items-count
                institutions_ul = soup.find("ul", class_="rlist--inline list-of-institutions truncate-list trunc-done")
                if institutions_ul is None:
                    institutions_ul = soup.find("ul", class_="rlist--inline list-of-institutions truncate-list")

                list = []
                for li in institutions_ul:
                    temp_url = li.a["href"]
                    name = li.text.strip()
                    lst = ["https:/", self.base_url, temp_url]
                    url_insti = "".join(lst)
                    split_text = temp_url.split("/")
                    # temp_id = temp_url[13:]
                    temp_id = split_text[len(split_text) - 1]
                    data = {
                        'id': temp_id,
                        'name': name,
                        'url': url_insti
                    }
                    self.intitution_set[data['id']] = data
                    list.append(data)

                del autor['venue']
                autor['institutions'] = list
                self.authors_set[autor['id']] = autor
                metrics_div = soup.find("div", class_="owl-stage")
                # guardamos en jsons
                self.save_autores()
                self.save_institutions()
                print('Listo', autor['name'])
        else:
            print("ya existe", autor['name'])
        """
        for metric in metrics_div:
            metric_info = metric

        """
    def get_institutions(self):
        try:
            self.load_data2()
            self.load_insti()
            for insti in self.intitution_set.values():
                if insti['id'] != 'javascript:void(0)':
                    if insti['id'] not in self.intitution_set2:
                        self.get_institution_info(insti)
                    else:
                        print('Existe', insti["name"])
                else:
                    print('doh')
        except Exception as e:
            print(e)
            fail_message(e)
            self.driver_for_acm.quit()
            raise Exception("Oh crud") from e

    def get_institution_info(self, insti):
        url = insti['url']
        self.driver_for_acm.get(url)
        time.sleep(5)
        # parse source code
        soup = BeautifulSoup(self.driver_for_acm.page_source, "html.parser")
        address_tag = soup.find('span', class_="address")
        address = '' if address_tag is None else address_tag.text
        split_adress = address.split(',')
        for i in range(len(split_adress)):
            key = 'ad'+ str(i)
            insti[key] = split_adress[i].strip()
        self.intitution_set2[insti['id']] = insti
        self.save_institutions2()
        pass

    def loop_authors(self):
        self.load_data2()
        for author in self.authors_set.values():
            self.find_author(author)
            pass

    def find_author(self, author):
        try:
            name = re.sub(' +', ' ', author['name'])
            querystring = "SELECT * FROM authors as p"
            querystring += " WHERE p.name LIKE '%" + name + "%'"
            self.cursor.execute(querystring)
            mobile_records = self.cursor.fetchall()
            if len(mobile_records) > 0:
                print("hay valores en:", name)
                self.cursor2.execute(querystring)
                mobile_records = self.cursor2.fetchall()
                if len(mobile_records) == 0:
                    value =  2 if len(mobile_records) > 1 else 1
                    list = mobile_records[:value]
                    for row in list:
                        print(row)
                        self.insert_row_preview_author(row, author, name)
                    else:
                        print("ya existe")
                        self.id += 1
            else:
                print("add info to subset")
                self.cursor2.execute(querystring)
                mobile_records = self.cursor2.fetchall()
                if len(mobile_records) == 0:
                    self.insert_row_author(author, name)
                else:
                    self.id += 1

        except Exception as e:
            print(name)
            print(querystring)
            #print(self.id)
            fail_message(e)
            raise Exception("Oh crud") from e
        pass

    def insert_row_preview_author(self, row, author, author_name):
        headers = "("
        headers += ", ".join(self.headers_authors)
        headers += ")"
        insert_query = "INSERT INTO authors" + headers + " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        record_to_insert = (
        self.id, row[1], author_name, row[3], row[4], row[5], row[6], row[7], author['id'], author['url'])
        self.cursor2.execute(insert_query, record_to_insert)
        self.conn2.commit()
        count = self.cursor2.rowcount
        self.id += 1
        print(self.id, "Record inserted successfully into mobile table", author_name)

    def insert_row_author(self, author, author_name):
        headers = "("
        headers += ", ".join(self.headers_authors)
        headers += ")"
        insert_query = "INSERT INTO authors" + headers + " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        record_to_insert = (
            self.id, '', author_name, '', '', '', '', '', author['id'], author['url'])

        self.cursor2.execute(insert_query, record_to_insert)
        self.conn2.commit()
        count = self.cursor2.rowcount
        self.id += 1

        print(count, "Record inserted successfully into mobile table", author_name)
        pass