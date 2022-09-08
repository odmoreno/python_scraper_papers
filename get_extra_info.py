"""
Obtener info adicional del paper como sus autores
"""
import json
import time
from common_functions import *


class Info:
    def __init__(self, urls):
        self.list_urls = urls
        self.base_url = "/dl.acm.org"
        self.driver_for_acm = make_chrome_headless()
        self.papers_dict = {}
        self.authors_tmp_dict = {}
        self.dir = "jsons/"
        self.papers_path = "jsons/papers.json"
        self.authors_path = "jsons/authors.json"

    def save_data(self):
        #save current papers
        json_string = json.dumps(self.papers_dict, ensure_ascii= False, indent=2)
        with open(self.papers_path, 'w', encoding="utf-8") as outfile:
            outfile.write(json_string)
        #save current authors
        json_string2 = json.dumps(self.authors_tmp_dict, ensure_ascii= False, indent=2)
        with open(self.authors_path, 'w', encoding="utf-8") as outfile:
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
        data = {
            'name': name.strip(),
            'venue': venue.strip(),
            'url': url_author,
            'id': temp_id
        }
        self.authors_tmp_dict[temp_id] = data
        return data


    def paper_scraper(self, paper):

        if paper['title'] == "Visualization of Data Changes in 2.5D Treemaps usingProcedural Textures and Animated Transitions":
            print('revisar')

        if paper['title'] == "Enabling Comparative Analysis of Election Data in Ecuador":
            print('revisar')

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
        self.papers_dict[paper['doi']] = paper
        self.save_data()
        print("Listo : ", paper['title'])

    def main_fun(self):
        try:
            for url in self.list_urls:
                # get the json namefile of conference
                name = url[0] + '_' + url[1]
                namefile = config.path_to_search_results + name + '.json'
                with open(namefile, encoding='utf-8') as f:
                    data = json.load(f)
                    for paper in data.values():
                        self.paper_scraper(paper)
                    print("Terminado: ", name)

        except Exception as e:
            fail_message(e)
            self.driver_for_acm.quit()