from common_functions import *
import json
import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class AcmClient:
    def __init__(self,urls):
        self.base_url = "https://dl.acm.org"
        self.list_urls = urls
        self.driver_for_acm = make_chrome_headless()
        self.currentyear = ''

        self.papers_dict = {}
        self.authors_tmp_dict = {}

        # cargar datos
        self.load_data()


    def load_data(self):
        self.papers_dict = load_generic("data/jsons/papers.json")

    def main_fun(self):
        try:
            for url in self.list_urls:
                # get the json namefile of conference
                name = url[0] + '_' + url[1]
                namefile = config.path_to_search_results + name + '.json'
                print("Conference:", name)
                with open(namefile, encoding='utf-8') as f:
                    data = json.load(f)
                    for paper in data.values():
                        if paper['doi']  in self.papers_dict:#not in self.papers_dict:
                            self.paper_scraper(paper)
                        else:
                            # print('ya existe ...', paper['title'])
                            if len(paper['authors']) == 0:
                                self.paper_scraper(paper)

                    print("Terminado: ", name)
        except Exception as e:
            fail_message(e)
            self.driver_for_acm.quit()

    def paper_scraper(self, paper):
        url_paper = paper['url']
        self.driver_for_acm.get(url_paper)
        #time.sleep(5)
        # load scripts inside de page
        button = self.driver_for_acm.find_element_by_css_selector("button[title='Information and Authors']")
        self.driver_for_acm.execute_script("arguments[0].click();", button)
        buttons = self.driver_for_acm.find_elements_by_css_selector("button[title='Information and Authors']")
        for but in buttons:
            self.driver_for_acm.execute_script("arguments[0].click();", but)
        #find authors info & claims tag<a>
        a_tag = self.driver_for_acm.find_elements_by_css_selector("a[href='#pill-authors__contentcon']")
        for element in a_tag:
            pass
            #element.click()
        time.sleep(5)
        # parse source code
        soup = BeautifulSoup(self.driver_for_acm.page_source, "html.parser")
        # print(soup.prettify())
        authors_info = soup.findAll("div", class_="auth-info")
        authors_list = []
        for author in authors_info:
            data_author = self.get_author_props(author)
            authors_list.append(data_author)

        # print(authors_list)
        abstract_section = soup.find("div", class_="abstractSection abstractInFull")
        abstract_text = abstract_section.find('p').text.strip()
        references_list = soup.find("ol", class_="rlist references__list references__numeric")
        count = 0 if references_list is None else len(references_list)
        paper['abstract'] = abstract_text
        paper['authors'] = authors_list
        paper['n_reference'] = count
        paper['venue'] = 'vinci'
        # save paper in dict
        self.papers_dict[paper['doi']] = paper
        self.save_data()
        print("Listo : ", paper['title'])

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
        # save author in dict
        self.authors_tmp_dict[temp_id] = data
        return data


if __name__ == '__main__':

    data = get_data_conferences()

    client = AcmClient(data)
    client.main_fun()