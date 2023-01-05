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
        self.root_url = "https://dl.acm.org/"
        self.dir = "data/"
        self.papers_path = "jsons/papers_u.json"
        self.authors_temp_path = "jsons/authors_tmp.json"
        self.ref_path = "data/jsons/ref_list_raw.json"
        self.reference_list = {}
        self.headers_authors = ['id', '_id', 'name', 'sid', 'org', 'gid', 'oid', 'orgid', 'acmid', 'url']
        self.reference_dict = {}
        # data para las refs
        self.ref_docs_tmp = {}
        self.refs_for_papers = {}
        self.temps_doi = {}
        # load
        self.load_data()
        self.id= 0


    def load_data(self):
        with open(self.dir + self.papers_path, encoding='utf-8') as fh:
            papers = json.load(fh)
        #print(papers)
        with open(self.dir + self.authors_temp_path, encoding='utf-8') as fh:
            authors = json.load(fh)
        #print(authors)
        self.papers_dict = papers
        self.authors_tmp_dict = authors
        with open(self.ref_path, encoding='utf-8') as fh:
            refs = json.load(fh)
        self.reference_dict = refs
        #return [papers, authors]

    def load_refs(self):
        with open(self.ref_path, encoding='utf-8') as fh:
            refs = json.load(fh)
        self.reference_dict = refs

    def save_list(self):
        # save current list
        json_string = json.dumps(self.reference_list, ensure_ascii=False, indent=2)
        with open(self.ref_path, 'w', encoding="utf-8") as outfile:
            outfile.write(json_string)

    def main_fun(self):
        try:
            for url in self.list_urls:
                # get the json namefile of conference
                name = url[0] + '_' + url[1]
                namefile = config.path_to_search_results + name + '.json'
                print("-- Inicia:", name)
                with open(namefile, encoding='utf-8') as f:
                    data = json.load(f)
                    for paper in data.values():
                        print(paper['title'])
                        print(paper['url'])
                        if paper['doi'] not in self.reference_dict:
                            self.get_references(paper)

                    print("-- Terminado: ", name)
        except Exception as e:
            fail_message(e)
            self.driver_for_acm.quit()

    def check_exist_tag(self):
        try:
            self.driver_for_acm.find_element_by_css_selector("button[aria-label='Show All References']")
        except NoSuchElementException:
            return False
        return True


    def get_references(self, paper):
        url_paper = paper['url']
        self.driver_for_acm.get(url_paper)
        if paper['title'] == "Facilitating Visualization Capacity Building":
            print("uh")
        #time.sleep(5)
        #WebDriverWait(self.driver_for_acm, 20).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div.cookiePolicy-popup__body clearfix")))

        boool = self.check_exist_tag()

        if boool:
            button = self.driver_for_acm.find_element_by_css_selector("button[aria-label='Show All References']")

            divbtn = WebDriverWait(self.driver_for_acm, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Show All References']")))

            self.driver_for_acm.execute_script("arguments[0].scrollIntoView();", button)
            self.driver_for_acm.execute_script("arguments[0].click();", divbtn)
            #divbtn = self.driver_for_acm.find_elements_by_tag_name("button[aria-label='Show All References']")
            # parse source code

        soup = BeautifulSoup(self.driver_for_acm.page_source, "html.parser")
        references_list = soup.find("ol", class_="rlist references__list references__numeric")
        # loop references
        ref_list = []
        if references_list != None:
            for ref in references_list:
                text = ref.text
                #print(text)
                data_ref = self.extract_refs_info(paper, ref)
                ref_list.append(data_ref)

        self.reference_list[paper['doi']] = ref_list
        self.save_list()

    def extract_refs_info(self, paper, ref):
        try:
            #print("inside")
            refs_note = ref.find('span', class_="references__note")
            refs_suffix = ref.find_all('span', class_="references__suffix")
            links = []
            for link in refs_suffix:
                a_tag = link.a
                a_href = link.a["href"]
                a_class = link.a["class"] if "class" in a_tag.attrs else ""
                img_tag = link.a.img
                img_alt = link.a.img['alt'] if "alt" in img_tag.attrs else ""
                data = {
                    'href': a_href,
                    'alt': img_alt
                }
                links.append(data)
            data_pad = {
                'notes': refs_note.contents[0],
                'links': links
            }

            return data_pad
        except Exception as e:
            fail_message(e)

    def loop_raw_refs(self):
        #self.load_refs()
        try:
            for key in self.reference_dict:
                # get refs
                list = self.reference_dict[key]
                for ref in list:
                    self.parse_data_ref(ref)

        except Exception as e:
            fail_message(e)

    def parse_data_ref(self, ref):
        notes = ref['notes']
        links = ref['links']

        has_nd_in_notes = True if '[n. d.]' in notes else False
        has_doi_in_notes = True if 'doi' in notes else False
        has_doi_link = False
        last_href = ''

        for element in links:
            alt_parse = element['alt'].lower()
            if(alt_parse == "digital library"):
                has_doi_link = True
            last_href = element['href']

        notes_split_3 = notes.split('.', maxsplit=3)

        print(notes_split_3)