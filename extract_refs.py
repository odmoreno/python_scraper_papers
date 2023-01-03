"""
Extraer referencias
"""
import psycopg2
import json
import time
import re
from common_functions import *
class Refs:
    def __init__(self, urls):
        self.list_urls = urls
        self.driver_for_acm = make_chrome_headless()
        self.papers_dict = {}
        self.authors_tmp_dict = {}
        self.dir = "data/"
        self.papers_path = "jsons/papers_u.json"
        self.authors_temp_path = "jsons/authors_tmp.json"
        self.load_data()
        self.id= 0
        self.reference_list = {}
        self.headers_authors = ['id', '_id', 'name', 'sid', 'org', 'gid', 'oid', 'orgid', 'acmid', 'url']


    def load_data(self):
        with open(self.dir + self.papers_path, encoding='utf-8') as fh:
            papers = json.load(fh)
        #print(papers)
        with open(self.dir + self.authors_temp_path, encoding='utf-8') as fh:
            authors = json.load(fh)
        #print(authors)

        self.papers_dict = papers
        self.authors_tmp_dict = authors
        #return [papers, authors]

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
                        print(paper['title'])
                        print(paper['url'])
                        self.get_references(paper)

                    print("Terminado: ", name)
        except Exception as e:
            fail_message(e)
            self.driver_for_acm.quit()


    def get_references(self, paper):
        url_paper = paper['url']
        self.driver_for_acm.get(url_paper)
        time.sleep(5)

        #WebDriverWait(self.driver_for_acm, 20).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.cookiePolicy-popup__body clearfix")))
        divbtn = WebDriverWait(self.driver_for_acm, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Show All References']")))

        button = self.driver_for_acm.find_element_by_css_selector("button[aria-label='Show All References']")
        self.driver_for_acm.execute_script("arguments[0].scrollIntoView();", button)
        self.driver_for_acm.execute_script("arguments[0].click();", divbtn)

        #divbtn = self.driver_for_acm.find_elements_by_tag_name("button[aria-label='Show All References']")


        # parse source code
        soup = BeautifulSoup(self.driver_for_acm.page_source, "html.parser")
        references_list = soup.find("ol", class_="rlist references__list references__numeric")
        # loop references
        for ref in references_list:
            print(ref.text)
            pass