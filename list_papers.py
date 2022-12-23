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

    def save_data_to_json(self, name, data):
        filename = 'data/conferences/' + name + '.json'
        json_string = json.dumps(data, ensure_ascii= False, indent=2)
        # Using a JSON string
        with open(filename, 'w', encoding="utf-8") as outfile:
            outfile.write(json_string)


    def get_data_papers(self, tipo, contenido):
        # Result title
        title_tmp = contenido.find("h5").text
        title = title_tmp.strip("'")
        """
        journal_temp = contenido.find("div", class_="issue-item__detail")
        journal = journal_temp.find("a")
        """
        # Result url
        temp_url = contenido.find("h5").a["href"]
        lst = ["https:/",temp_url[:4],".org",temp_url[4:],]
        url = "".join(lst)
        # Get DOI
        doi = temp_url[5:]
        # Result date
        allspans = contenido.find("div", class_="issue-item__detail").findAll("span")
        texts = []
        for span in allspans:
            contenttext = span.text.rstrip(", ")
            texts.append(contenttext)
        date = texts[0]
        numbers = re.compile(r"\d+(?:\.\d+)?")
        p_year = numbers.findall(date)[0]
        p_year = self.currentyear
        # Result authors
        authors = []

        ul = contenido.find("ul")

        for li in ul.findAll("li"):  # list of authors
            name = li.text.rstrip(", \n").strip("'")
            temp_urlname = li.a["href"]
            lst = ["https:/", "dl.acm", ".org", temp_urlname, ]
            urlname = "".join(lst)
            dataauthor = {
                "name": name,
                "url": urlname
            }
            if "javascript:void(0)" not in urlname:
                authors.append(dataauthor)
            #authors.append(li.text.rstrip(", \n").strip("'"))

        t_author_list = str(authors).strip("[]")
        author_list = t_author_list.replace("'", "")
        # Citation
        n_citation = contenido.find("div", class_="citation").find('span')
        n_citation = '' if n_citation is None else n_citation.text
        # Downloads
        n_descargas = contenido.find("div", class_="metric")
        n_descargas = '' if n_descargas is None else n_descargas.find('span').text
        data = {
            "type": tipo,
            "title" : title,
            "url" : url,
            "year": p_year,
            #"journal": journal,
            "authors": authors,
            "citations": n_citation,
            "downloads": n_descargas,
            "doi" : doi,
            "extra": texts
        }
        return data

    def get_info_conference(self, content):

        pass


    def main_fun(self):
        try:
            for url in self.list_urls:
                # get the name of conference
                name = url[0] + '_' + url[1]
                self.currentyear = url[1]
                print('Anio', name)
                conference_title = url[3]
                conference_publisher = url[4]
                conference_isbn = url[6]
                conference = {}
                # Check if exist path of json
                flag_path = check_if_exist_file_json(config.path_to_search_results, name)
                if not flag_path:
                    self.driver_for_acm.get(url[2])

                    #topics_xpath = "//div[@class='removed-items-count']"
                    #WebDriverWait(self.driver_for_acm, 10).until(
                    #    expected_conditions.visibility_of_element_located((By.XPATH, topics_xpath)))

                    WebDriverWait(self.driver_for_acm, 20).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a[class='removed-items-count']"))).click()

                    # open accordions tabs accordion-tabbed__content
                    #popup = self.driver_for_acm.find_elements_by_class_name('accordion-tabbed__content')
                    #elements = self.driver_for_acm.find_elements_by_xpath("//a[contains(@class, 'section__title accordion-tabbed__control left-bordered-title')]")
                    """
                    //*[@id="pb-page-content"]/div/main/div[4]/div/div[2]/div[1]/div/div[2]/div/div/div[2]"""
                    divhead = self.driver_for_acm.find_elements_by_css_selector("a[class='section__title accordion-tabbed__control left-bordered-title'][aria-expanded='false']")
                    for header in divhead:
                        self.driver_for_acm.execute_script("arguments[0].click();", header)
                        header.click()

                    clickmore = self.driver_for_acm.find_elements_by_xpath("//a[contains(@class, 'removed-items-count')]")
                    for el in clickmore:
                        #element.click()
                        self.driver_for_acm.execute_script("arguments[0].click();", el)

                    self.driver_for_acm.execute_script(
                        "document.getElementsByClassName('accordion-tabbed__content')[0].style.display='block';")

                    #"a[href='javascript:void(0)']"
                    aElements = self.driver_for_acm.find_elements_by_tag_name("a[class='removed-items-count']")
                    for name1 in aElements:
                        if (name1.get_attribute("href") is not None and "javascript:void" in name1.get_attribute("href")):
                            #print("IM IN HUR", name.get_attribute("href"))
                            name1.click()



                    # parse source code
                    soup = BeautifulSoup(self.driver_for_acm.page_source, "html.parser")
                    #time.sleep(10)
                    # Get the result containers
                    result_containers = soup.findAll("div", class_="issue-item clearfix")
                    item_citation = soup.findAll("div", class_="issue-heading")
                    item_content = soup.findAll("div", class_="issue-item__content")
                    #loop and search for results
                    for index in range(len(item_content)):
                        #print(index)
                        citation = item_citation[index]
                        tipo_de_paper = citation.text
                        contenido = item_content[index].find('div', {'class': 'issue-item__content-right'})
                        data = self.get_data_papers(tipo_de_paper, contenido)
                        #data['conference_title'] = conference_title
                        data['publisher'] = conference_publisher
                        data['conference_isbn'] = conference_isbn
                        conference[data['doi']] = data

                    self.save_data_to_json(name, conference)
                else:
                    print('Ya existe :', name)

        except Exception as e:
            fail_message(e)
            self.driver_for_acm.quit()

