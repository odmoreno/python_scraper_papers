"""
Extraer referencias
"""
import psycopg2
import json
import time
import re
from common_functions import *
from unidecode import unidecode

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
        self.reference_dict = {}
        # data para las refs
        self.current_paper_doi = ''
        self.ref_papers_tmp = {}
        self.refs_for_papers = {}
        self.temps_doi = {}
        self.doi_list = []
        self.ref_papers_path = 'data/jsons/ref_papers_tmp.json'
        self.ref_for_papers_path = 'data/jsons/ref_per_paper.json'
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

    def save_generic(self, path, collection):
        json_string = json.dumps(collection, ensure_ascii=False, indent=2)
        with open(path, 'w', encoding="utf-8") as outfile:
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
                self.current_paper_doi = key
                list = self.reference_dict[key]
                print(key)
                print(len(list))
                # Reset: lista de dois referenciados por paper
                self.doi_list = []
                for ref in list:
                    self.parse_data_ref(ref)
                #adjuntamos los dois de las ref  en un nuevo dict
                self.refs_for_papers[key] = self.doi_list
                self.save_generic(self.ref_for_papers_path, self.refs_for_papers)
        except Exception as e:
            fail_message(e)
            print(ref)

    def replace_abbr(self, text):
        t_split = text.split()
        newlist = ''
        for word in t_split:
            new_word = re.sub(r'(?<!\w)([A-Z])\.', r'\1', word)
            newlist += new_word + ' '
        return  newlist

    def parse_data_ref(self, ref):
        notes = ref['notes']
        links = ref['links']
        newword = self.replace_abbr(notes)
        notes = unidecode(newword)
        notes = notes.replace('"', '.')
        notes = notes.replace('}}', '')

        has_nd_in_notes = True if '[n. d.]' in notes else False
        has_doi_in_notes = True if 'doi' in notes else False
        has_doi_link = False
        has_cross_ref_link = False
        last_href = ''

        for element in links:
            alt_parse = element['alt'].lower()
            if(alt_parse == "digital library"):
                has_doi_link = True
            elif alt_parse == "cross ref":
                has_cross_ref_link = True
            last_href = element['href']

        if has_nd_in_notes:
            notes = notes.replace('[n. d.]', '')

        notes_split_3 = notes.split('.', maxsplit=3)
        #print(notes_split_3)

        doi = ''
        if has_doi_in_notes:
            notes_by_spaces= notes.split(' ')
            for note in notes_by_spaces:
                if 'doi.org' in note:
                    doi_split = note.split('doi.org/',1)
                    doi = doi_split[1]
                    break
        elif has_doi_link:
            doi_split = last_href.split('doi/',1)
            doi = doi_split[1]
        elif has_cross_ref_link:
            doi = last_href

        if has_doi_in_notes or has_doi_link or has_cross_ref_link:
            flag = False
            if has_doi_in_notes or has_doi_link:
                flag = True
            self.save_paper_ref(notes_split_3, doi, flag)


    def save_paper_ref(self, element, doi,flag):
        if doi not in self.ref_papers_tmp:
            i = 1
            a ={}
            for parts in element:
                a['p'+ str(i)] = parts.strip()
                i +=1

            dl_link = 'https://doi.org/' + doi
            cross_link =  'https://dl.acm.org/' + doi
            url = cross_link if flag else dl_link

            data = {
                "title": a['p3'] if 'p3' in a else '',
                "url": url,
                "year": a['p2'] if 'p2' in a else '',
                "authors": a['p1'] if 'p1' in a else '',
                "doi": doi,
                "extra": a['p4'] if 'p4' in a else '',
                'raw': element
            }
            self.ref_papers_tmp[doi] = data
            self.doi_list.append(doi)
            self.save_generic(self.ref_papers_path, self.ref_papers_tmp)



