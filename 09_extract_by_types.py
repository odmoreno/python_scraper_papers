'''
Extraer informacion de las ref segun la pagina del publisher
'''

from common_functions import *
import time
import json

class Refs:

    def __init__(self):

        self.driver = make_chrome_headless()
        self.pub_list_path = 'data/jsons/publishers.json'
        self.ref_papers_tmp_path = 'data/jsons/ref_papers_tmp.json'
        self.ref_papers_tmp_dict = {}
        self.pub_list ={}
        #datos para loops
        self.current_paper = {}
        #nuevas colecciones generadas
        self.ref_papers_new_path = 'data/jsons/ref_papers.json'
        self.published_list_path = 'data/jsons/publisheds.json'
        self.ref_papers_new = {}
        self.published_list = {}


    def load_data(self):
        with open(self.ref_papers_tmp_path, encoding='utf-8') as fh:
            papers = json.load(fh)
        self.ref_papers_tmp_dict = papers

    def load_generic(self, path):
        with open(path, encoding='utf-8') as fh:
            elements = json.load(fh)
        return elements

    def save_generic(self, path, collection):
        json_string = json.dumps(collection, ensure_ascii=False, indent=2)
        with open(path, 'w', encoding="utf-8") as outfile:
            outfile.write(json_string)

    def get_info_tmp_ref(self):
        self.pub_list = self.load_generic(self.pub_list_path)
        self.ref_papers_new = self.load_generic(self.ref_papers_new_path)
        self.published_list = self.load_generic(self.published_list_path)
        #main fun
        try:
            for key in self.ref_papers_tmp_dict:
                if key not in self.ref_papers_new:
                    self.detect_url(key)
            self.save_generic(self.pub_list_path, self.pub_list)
        except Exception as e:
            print(key)
            fail_message(e)

    def detect_url(self, key):
        self.current_paper = self.ref_papers_tmp_dict[key]
        url = self.current_paper['url']
        self.driver.get(url)
        #time.sleep(5)
        print(self.driver.current_url)
        #self.save_publisher(self.driver.current_url)
        #separacion
        pub_name = self.pub_short_name(self.driver.current_url)
        self.find_publisher(pub_name)

    def pub_short_name(self, url):
        new_url = url.replace('https://', '')
        url_split = new_url.split('/')
        publisher_name = url_split[0]
        return publisher_name

    def save_publisher(self, url):
        new_url = url.replace('https://', '')
        url_split = new_url.split('/')
        publisher_name = url_split[0]
        if publisher_name not in self.pub_list:
            self.pub_list[publisher_name] = {'name': publisher_name, "example": url}
            self.save_generic(self.pub_list_path, self.pub_list)

    def find_publisher(self, publisher):
        if publisher in self.pub_list:
            if publisher == "ieeexplore.ieee.org":
                self.extract_from_ieee()
            elif publisher == "dl.acm.org":
                self.extract_from_acm()
        else:
            print("desconocido, usar default values")

    def replace(self, g):
        g = g.group(0).replace(',', '')
        g = g.group(0).replace(',', '')
        return g.group(0).replace(',', '')

    def extract_from_ieee(self):
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        paper_title = soup.find("h1", class_="document-title").text.strip()
        paper_pub = soup.find("div", class_="publisher-title-tooltip").text.strip()
        abstract = soup.find("div", class_="abstract-text").text.strip()

        metrics = soup.findAll("div", class_="document-banner-metric-count")
        citations = metrics[0].text
        patent = metrics[1].text if len(metrics)>2 else ''
        views = metrics[2].text  if len(metrics)>2 else metrics[1].text
        #authors
        authors = soup.findAll("span", class_="authors-info")
        auth_list = []
        for author in authors:
            text = author.text
            new_str = re.sub(r'[^a-zA-Z]', ' ', text)
            new_str = new_str.strip()
            auth_list.append(new_str)
        '''
        divaut= WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.ID, "authors")))

        self.driver.execute_script("arguments[0].click();", divaut)
        authors_element = soup.find("a", {"id": "authors"})
        authors_element.click()'''

        published_in = soup.find("div", class_="u-pb-1 stats-document-abstract-publishedIn")
        text = published_in.text
        match = re.match(r'.*([1-3][0-9]{3})', text)
        year = match.group(1)

        split_text = text.split(':', 1)
        publ = split_text[1].strip()
        published = re.sub(r'\([^()]*\)', ' ',publ).strip()

        div_doi = soup.find("div", class_="u-pb-1 stats-document-abstract-doi")
        doi_tmp = div_doi.text
        doi_split = doi_tmp.split(':',1)
        doi = doi_split[1].strip()

        title = paper_title if paper_title is not None else self.current_paper['title']
        url = self.driver.current_url
        pyear = year if year is not None else self.current_paper['year']
        if len(auth_list) == 0:
            auth_list = self.current_paper['authors']

        data = {
            "title": title,
            "url": url,
            "year": pyear,
            "authors": auth_list,
            "citations": citations,
            "views": views,
            "doi": doi,
            "conference": published,
            "abstract": abstract
        }
        self.ref_papers_new[doi] = data
        self.published_list[published] = {
            "name": published,
            "fixed": ''
        }
        self.save_generic(self.ref_papers_new_path, self.ref_papers_new)
        self.save_generic(self.published_list_path, self.published_list)

    def extract_from_acm(self):
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        paper_title = soup.find("h1", class_="citation__title")  # text-2xl-md-lh
        # "a[href='javascript:void(0)']"
        #aElements = self.driver.find_elements_by_tag_name("a[class='removed-items-count']")
        #for name1 in aElements:
        #    if (name1.get_attribute("href") is not None and "javascript:void" in name1.get_attribute("href")):
        #        # print("IM IN HUR", name.get_attribute("href"))
        #        name1.click()

        authors = self.driver.find_elements_by_class_name("loa__item")
        details = soup.find("div", class_="issue-item__detail")

        citacion = soup.find("span", class_="citation")
        metric = soup.find("span", class_="metric")
        pass

if __name__ == '__main__':
    client = Refs()
    client.load_data()
    client.get_info_tmp_ref()